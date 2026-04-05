from rest_framework import serializers
from .models import Course, Lesson


class LessonNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'video_url']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonNestedSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'lessons', 'lessons_count']

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer:
    pass


class CourseListSerializer:
    pass