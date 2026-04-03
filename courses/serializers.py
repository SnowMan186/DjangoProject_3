from rest_framework import serializers
from .models import Course, Lesson


class LessonListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка уроков (минимум данных)"""

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра курса (со списком уроков)"""
    lessons = LessonListSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка курсов (без вложенных уроков)"""
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'lessons_count']  # Только основные поля

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer:
    pass