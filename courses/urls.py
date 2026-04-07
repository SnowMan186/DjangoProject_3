from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreate, LessonRetrieveUpdateDestroy

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreate.as_view()),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroy.as_view()),
]