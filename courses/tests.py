from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Course, Lesson

User = get_user_model()


class CoursesAPITestCase(TestCase):

    def setUp(self):
        """Настройка тестовых данных."""
        # Создаем двух пользователей: обычного и модератора/админа если нужно
        self.user1 = User.objects.create_user(email='user1@test.com', password='testpass123')
        self.user2 = User.objects.create_user(email='user2@test.com', password='testpass123')

        self.client = Client()

        # Создаем курс от имени user1 и урок к нему для тестов прав доступа
        self.course1 = Course.objects.create(owner=self.user1, title='Курс владельца')
        self.course2 = Course.objects.create(owner=self.user2, title='Чужой курс')

        self.lesson1 = Lesson.objects.create(owner=self.user1, course=self.course1, title='Урок владельца',
                                             video_url='https://youtube.com')
        self.lesson2 = Lesson.objects.create(owner=self.user2, course=self.course2, title='Чужой урок',
                                             video_url='https://youtube.com')

    def test_lesson_crud_permissions(self):
        """Тестируем CRUD уроков с разными правами доступа."""

        client = self.client

        # --- ТЕСТ 1: Неавторизованный пользователь не может создать урок ---
        response = client.post('/api/lessons/', {
            'title': 'Новый урок',
            'course': self.course1.id,
            'video_url': 'https://youtube.com'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # --- ТЕСТ 2: Пользователь может создать СВОЙ урок ---
        client.force_authenticate(user=self.user1)

        response = client.post('/api/lessons/', {
            'title': 'Новый урок',
            'course': self.course1.id,
            'video_url': 'https://youtube.com'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # --- ТЕСТ 3: Пользователь НЕ может редактировать ЧУЖОЙ урок ---
        response = client.put(f'/api/lessons/{self.lesson2.id}/', {
            'title': 'Попытка взлома',
            'course': self.course2.id,
            'video_url': 'https://youtube.com'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # --- ТЕСТ 4: Валидатор ссылки на видео работает ---
        response = client.post('/api/lessons/', {
            'title': 'Урок с плохой ссылкой',
            'course': self.course1.id,
            'video_url': 'https://vimeo.com'  # Не YouTube!
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_toggle(self):
        """Тестируем функционал подписки и отписки."""
        client = self.client
        url = '/api/courses/subscribe/'

        # Аутентифицируем пользователя
        client.force_authenticate(user=self.user1)

        # --- ТЕСТ 1: Пользователь подписывается на курс ---
        response = client.post(url, {'course_id': self.course2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')

        # Проверяем, что подписка создалась в базе
        self.assertTrue(self.user1.subscriptions.filter(course=self.course2).exists())

        # --- ТЕСТ 2: Пользователь отписывается от того же курса ---
        response = client.post(url, {'course_id': self.course2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')

        # Проверяем, что подписка удалилась из базы
        self.assertFalse(self.user1.subscriptions.filter(course=self.course2).exists())

    def test_course_crud_permissions(self):
        """Тестируем создание и удаление курсов с разными правами."""
        client = self.client

        # Аутентифицируем пользователя1 (владелец)
        client.force_authenticate(user=self.user1)

        # --- ТЕСТ 1: Пользователь может СОЗДАТЬ свой курс ---
        response = client.post('/api/courses/', {
            'title': 'Новый курс от user1',
            'description': 'Описание'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # --- ТЕСТ 2: Пользователь НЕ может УДАЛИТЬ чужой курс ---
        response = client.delete(f'/api/courses/{self.course2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
