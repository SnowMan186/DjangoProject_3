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
            # Создавать курсы могут только обычные пользователи (владельцы), но не модераторы!
            permission_classes = [permissions.IsAuthenticated]

        elif self.action in ['update', 'partial_update']:
            # Редактировать могут: Модераторы ИЛИ Владельцы (IsOwnerOrAdmin)
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwnerOrAdmin]

        elif self.action == 'destroy':
            # Удалять не могут ни модераторы, ни владельцы! Только админы.
            permission_classes = [permissions.IsAdminUser]

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
        if self.request.method == 'GET':
            permission_classes = [permissions.IsAuthenticated]

        elif self.request.method in ['PUT', 'PATCH']:
            # Редактировть: Модераторы ИЛИ Владельцы
            permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwnerOrAdmin]

        elif self.request.method == 'DELETE':
            # Удалять нельзя ни модераторам, ни владельцам! Только админам.
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]