from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from users.models import User

@shared_task(name="send_course_update_notification")
def send_course_update_notification(course_title, subscriber_emails):
    """
    Задача для отправки писем об обновлении курса.
    """
    subject = f'Курс "{course_title}" был обновлен!'
    message = f'В курсе "{course_title}" появились новые материалы. Успейте изучить!'
    email_from = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        message,
        email_from,
        subscriber_emails,
        fail_silently=False,
    )


@shared_task(name="deactivate_inactive_users")
def deactivate_inactive_users():
    """
    Периодическая задача: блокирует пользователей, не заходивших более месяца.
    """
    print("Running periodic task to deactivate inactive users...")

    # Вычисляем дату "один месяц назад" от текущего момента
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим всех активных пользователей, чей last_login раньше чем one_month_ago
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=one_month_ago,
    )

    count = inactive_users.count()

    # Обновляем батчем (это быстро и не нагружает БД)
    inactive_users.update(is_active=False)

    print(f"Deactivated {count} users.")
