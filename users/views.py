from rest_framework import viewsets, generics, filters, permissions
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .forms import CustomUserCreationForm
from django.views.generic.edit import CreateView


class IsOwnerOrAdmin:
    pass


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Разрешаем регистрацию (create) всем, остальные действия только админам или себе."""
        if self.action == 'create':
            # Регистрация доступна всем
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Редактировать и удалять можно только свой профиль или если ты админ
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else: # list, retrieve
            # Список и просмотр профилей - только для авторизованных
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # При регистрации пароль нужно хешировать
        user = serializer.save()
        user.set_password(user.password)
        user.save()

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Фильтрация по полям
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['date']

class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = '/'