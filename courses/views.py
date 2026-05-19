from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from users.models import Payment
from .models import Course, Lesson, Subscription
from .serializers import LessonSerializer, CourseDetailSerializer, CourseSerializer
from users.permissions import IsModerator, IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .paginators import StandardResultsSetPagination
from .services.payment_service import create_stripe_product_and_price, create_checkout_session
import stripe
from django.conf import settings
from .tasks import send_course_update_notification




class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        """
        Определяем права доступа для каждого действия.
        """
        permission_classes = [permissions.IsAuthenticated]
        if self.action in ["list", "retrieve"]:
            # Просмотр списка и деталей разрешен всем авторизованным пользователям
            permission_classes = [permissions.IsAuthenticated]

        elif self.action == "create":
            # СОЗДАНИЕ: Только Аутентифицированные И НЕ Модераторы
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]

        elif self.action in ["update", "partial_update"]:
            # РЕДАКТИРОВАНИЕ: Владельцы/Админы ИЛИ Модераторы (логика внутри IsOwnerOrAdmin)
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

        elif self.action == "destroy":
            # УДАЛЕНИЕ: Только Владельцы или Админы (Модераторам запрещено)
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Привязываем курс к авторизованному пользователю при создании
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        """
        Подписка на курс.
        """
        course = get_object_or_404(Course, pk=pk)
        subscription, created = course.subscriptions.get_or_create(user=request.user)
        if created:
            return Response({"message": "Подписка добавлена"}, status=status.HTTP_200_OK)
        else:
            subscription.delete()
            return Response({"message": "Подписка удалена"}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        """
        Этот метод вызывается при успешном обновлении объекта.
        """
        instance = serializer.save()

        # --- ЛОГИКА ОТПРАВКИ ПИСЕМ ---
        # Получаем всех подписчиков этого курса (исключая владельца)
        subscribers = instance.subscriptions.exclude(user=instance.owner).values_list("user__email", flat=True)
        subscriber_list = list(subscribers)

        # Если есть подписчики, вызываем задачу Celery (асинхронно!)
        if subscriber_list:
            send_course_update_notification.delay(instance.title, subscriber_list)


class LessonListCreate(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [permissions.IsAuthenticated]
        else:
            # СОЗДАНИЕ: Только Аутентифицированные И НЕ Модераторы
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        # РЕДАКТИРОВАНИЕ/УДАЛЕНИЕ: Владельцы/Админы ИЛИ Модераторы (только для PATCH)
        permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]


class SubscriptionView(APIView):
    """
    Эндпоинт для подписки/отписки пользователя на курс.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)

        sub_item, created = Subscription.objects.get_or_create(user=user, course=course)

        if not created:
            sub_item.delete()
            message = 'Подписка удалена'
        else:
            message = 'Подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)


class CreatePaymentSessionView(APIView):
    """
    Создает платежную сессию для курса.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "course_id is required"}, status=400)

        try:
            course = Course.objects.get(id=course_id)

            # 1. Создаем запись о платеже в нашей БД (опционально, но полезно)
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                payment_method='stripe'
            )

            # 2. Вызываем сервисную функцию для работы со Stripe
            product, price = create_stripe_product_and_price(course)

            if not price:
                return Response({"error": "Failed to create price in Stripe"}, status=500)

            session = create_checkout_session(price.id)

            if not session:
                return Response({"error": "Failed to create checkout session"}, status=500)

            # 3. Сохраняем ID сессии в нашей БД (опционально)
            payment.stripe_session_id = session.id
            payment.save()

            # 4. Отдаем пользователю ссылку на оплату
            return Response({
                "message": "Payment session created",
                "url": session.url
            }, status=201)

        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)