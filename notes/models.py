from django.db import models
from django.conf import settings
from diaries.models import Diary
# Create your models here.

class Note(models.Model):
    # note id(pk)와 diary_id(fk)분리
    diary_id = models.ForeignKey(Diary, on_delete = models.CASCADE)
    note_writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='u_notes')
    note_title = models.CharField(max_length=255)
    note_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_notes')

    def __str__(self):
        return self.note_title
    
# 사진저장 경로 확인
class NoteImage(models.Model):
    note = models.ForeignKey(Note, related_name='note_images', on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='note_images/%y/%b/%a')
    image = models.ImageField(upload_to='notes/static/img/%y/%b/%a')

    class Meta:
        unique_together = ('note', 'image')


# comment 영역 (분리 필요시, 분리)
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'note_comments')
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    content = models.CharField(max_length=125)
    created_at = models.DateTimeField(auto_now_add=True)