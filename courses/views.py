from rest_framework import viewsets, generics, permissions, status
from .models import Course, Lesson, Subscription
from .serializers import LessonSerializer, CourseDetailSerializer, CourseListSerializer
from users.permissions import IsModerator, IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .paginators import StandardResultsSetPagination


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def get_permissions(self):
        """
        Мгновенно определяем права доступа для каждого действия.
        Используем ~IsModerator для запрета создания.
        """
        if self.action in ['list', 'retrieve']:
            # Просмотр списка и деталей разрешен всем авторизованным пользователям
            permission_classes = [permissions.IsAuthenticated]

        elif self.action == 'create':
            # СОЗДАНИЕ: Только Аутентифицированные И НЕ Модераторы
            permission_classes = [permissions.IsAuthenticated, ~IsModerator]

        elif self.action in ['update', 'partial_update']:
            # РЕДАКТИРОВАНИЕ: Владельцы/Админы ИЛИ Модераторы (логика внутри IsOwnerOrAdmin)
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

        elif self.action == 'destroy':
            # УДАЛЕНИЕ: Только Владельцы или Админы (Модераторам запрещено)
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Привязываем курс к авторизованному пользователю при создании
        serializer.save(owner=self.request.user)


class LessonListCreate(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

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