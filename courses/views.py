from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import LessonSerializer, CourseDetailSerializer, CourseListSerializer
from users.permissions import IsModerator, IsOwnerOrAdmin


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

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