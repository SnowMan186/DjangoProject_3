from django.db import models


class Course(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True)
    description = models.TextField()

class Lesson(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True)
    video_url = models.URLField()