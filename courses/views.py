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
        if self.action in ['list', 'retrieve']:
            # Просмотр списка и деталей разрешен всем авторизованным пользователям
            permission_classes = [permissions.IsAuthenticated]

        elif self.action == 'create':
            # Создавать курсы могут только обычные пользователи (владельцы)
            permission_classes = [permissions.IsAuthenticated]

        elif self.action in ['update', 'partial_update']:
            # Редактировать могут: Владельцы/Админы ИЛИ Модераторы (только PATCH)
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

        elif self.action == 'destroy':
            # Удалять могут ТОЛЬКО Админы или Владельцы. Модераторам запрещено.
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
        else:  # POST (создание)
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        # Для всех методов используем один пермишен с логикой внутри
        permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]