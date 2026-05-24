import random
from django.core.management.base import BaseCommand
from users.models import Payment, User
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = 'Генерирует тестовые платежи для пользователей'

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаем генерацию данных...")

        users = list(User.objects.all())
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not users or not courses or not lessons:
            self.stdout.write(self.style.ERROR('Ошибка: Сначала создайте пользователей, курсы и уроки!'))
            return

        for user in users:
            # Создаем платеж за случайный курс для каждого пользователя
            course = random.choice(courses)
            Payment.objects.create(
                user=user,
                course=course,
                amount=random.randint(1000, 5000),
                payment_method='transfer' if random.random() > 0.5 else 'cash'
            )

            # С вероятностью 20% создадим платеж за урок для этого же пользователя
            if random.random() < 0.2:
                lesson = random.choice(lessons.filter(course=course))  # Урок из того же курса
                Payment.objects.create(
                    user=user,
                    lesson=lesson,
                    amount=random.randint(300, 900),
                    payment_method='cash'
                )

        self.stdout.write(self.style.SUCCESS('Данные успешно созданы!'))