from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreate, LessonRetrieveUpdateDestroy, SubscriptionView, CreatePaymentSessionView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreate.as_view()),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroy.as_view()),
    path('subscribe/', SubscriptionView.as_view(), name='subscription-toggle'),
    path('create-payment-session/', CreatePaymentSessionView.as_view(), name='create-payment'),
]