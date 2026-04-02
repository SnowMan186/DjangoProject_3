from django.contrib.auth.models import AbstractUser
from django.db import models
from courses.models import Course, Lesson

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"Платеж {self.id} от {self.user.email}"
