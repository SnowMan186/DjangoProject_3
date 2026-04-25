from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_link


class LessonNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'video_url': {
                'validators': [validate_youtube_link]
            }
        }


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonNestedSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'lessons', 'lessons_count']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonNestedSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    # НОВОЕ ПОЛЕ: Признак подписки текущего пользователя (из контекста)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на этот курс.
        """
        # Получаем текущего пользователя из контекста запроса
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем наличие подписки в базе
            return obj.subscriptions.filter(user=request.user).exists()
        return False


class CourseListSerializer:
    pass