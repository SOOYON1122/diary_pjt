from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import os

# 이미지 업로드 경로 설정
def note_image_path(instance, filename):
  ext = filename.split('.')[-1]
  filename = f'{uuid.uuid4()}.{ext}'
  return f'diary/{instance.user.username}/{filename}'


# 다이어리 모델
class Diary(models.Model):
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    related_name="diaries",
    on_delete=models.SET_NULL,
    null=True,
    blank=True
  )
  diary_title = models.CharField(max_length=30)
  diary_content = models.TextField()
  diary_category = models.CharField(max_length=30)
  diary_img = models.ImageField(upload_to=note_image_path, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  diary_friends = models.ManyToManyField(
    settings.AUTH_USER_MODEL,
    related_name="shared_diaries",
    blank=True
  )

  def __str__(self):
    return self.diary_title


# 다이어리 내의 노트 모델
class Note(models.Model):
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    related_name="user_notes",
    on_delete=models.CASCADE
  )
  diary = models.ForeignKey(
    Diary,
    related_name="diary_notes",
    on_delete=models.CASCADE
  )
  note_title = models.CharField(max_length=100)
  note_content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  like_users = models.ManyToManyField(
    settings.AUTH_USER_MODEL,
    related_name='like_notes',
    blank=True
  )

  def __str__(self):
    return self.note_title

  def clean(self):
    super().clean()
    if self.diary.user != self.user and not self.diary.diary_friends.filter(id=self.user.id).exists():
      raise ValidationError("노트를 작성할 권한이 없습니다.")

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)


# 노트 하나에 들어갈 이미지 모델 (최대 10장)
class NoteImage(models.Model):
  note = models.ForeignKey(
    Note,
    related_name="note_images",
    on_delete=models.CASCADE
  )
  image = models.ImageField(upload_to=note_image_path)
  uploaded_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('note', 'image')

  def __str__(self):
    return f"Image for {self.note.note_title}"

  def clean(self):
    super().clean()
    if self.note.note_images.count() >= 10:
      raise ValidationError("노트 당 최대 10장의 이미지만 업로드할 수 있습니다.")

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)


# comment 영역 (분리 필요시, 분리)
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'user_comments')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="notes_comment")
    content = models.CharField(max_length=125)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)