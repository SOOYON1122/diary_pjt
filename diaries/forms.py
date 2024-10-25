from PIL import Image
from django import forms
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q

from .models import Diary, Note, NoteImage, Comment
from friends.models import Friendship



User = get_user_model()

class MultipleImageInput(forms.ClearableFileInput):
  allow_multiple_selected = True  # 다중 선택 허용

  # widget에 multiple 속성을 추가
  def __init__(self, attrs=None):
    attrs = attrs or {}
    attrs.update({'multiple': True})  # multiple 속성 추가
    super().__init__(attrs)


class MultipleImageField(forms.FileField):
  def __init__(self, *args, **kwargs):
    kwargs.setdefault("widget", forms.ClearableFileInput(attrs={'multiple': True}))
    super().__init__(*args, **kwargs)

  def clean(self, data, initial=None):
    files = data if isinstance(data, list) else [data]
    cleaned_files = []
    
    for file in files:
      # 기본 clean()을 호출해 파일이 유효한지 검사합니다.
      cleaned_file = super().clean(file, initial)

      # 확장자 체크
      if not cleaned_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError(f"{cleaned_file.name} 파일은 PNG 또는 JPG 형식이어야 합니다.")
      
      # 파일 크기 제한 (15MB)
      if cleaned_file.size > 15 * 1024 * 1024:
        raise ValidationError(f"{cleaned_file.name} 파일의 크기는 15MB를 초과할 수 없습니다.")

      # 실제 이미지 파일인지 확인
      try:
        img = Image.open(cleaned_file)
        img.verify()  # Pillow를 사용하여 이미지가 유효한지 검사
        cleaned_files.append(cleaned_file)  # 검증을 통과한 파일만 추가
      except Exception:
        raise ValidationError(f"{cleaned_file.name} 파일은 유효하지 않은 이미지이거나 손상된 파일입니다.")

    return cleaned_files


class DiaryForm(forms.ModelForm):

  # 친구 목록에서 친구 추가하는 걸 Template에서 js로 동적 처리 예정
  diary_friends = forms.CharField(widget=forms.HiddenInput(), required=False)

  class Meta:
    model = Diary
    fields = ['diary_title', 'diary_content', 'diary_category', 'diary_img']

  def __init__(self, *args, **kwargs):
    self.current_user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

    if self.current_user:
      # 친구 관계에서 현재 사용자가 친구인 모든 친구들 가져오기
      friends_queryset = Friendship.objects.filter(
        Q(from_user=self.current_user) | Q(to_user=self.current_user),
        is_friend=True
      ).values_list('from_user', 'to_user', flat=False)

      # 친구 아이디들만 리스트로 추출
      friend_ids = set()
      for from_user, to_user in friends_queryset:
        if from_user == self.current_user.id:
          friend_ids.add(to_user)
        else:
          friend_ids.add(from_user)

      # 친구 목록을 queryset으로 설정
      self.friend_queryset = User.objects.filter(id__in=friend_ids)

  def clean_diary_friends(self):
    friends = self.cleaned_data.get('diary_friends')
    friend_ids = friends.split(',') if friends else []
    if len(friend_ids) > 7:
      raise ValidationError("다이어리에 추가할 친구는 최대 7명입니다.")
    return friend_ids



class NoteForm(forms.ModelForm):
    
    image = MultipleImageField(required=False)  # MultipleFileField 사용

    class Meta:
        model = Note
        fields = ['note_title', 'note_content', 'image']

    def clean(self):
      cleaned_data = super().clean()
      images = self.files.getlist('image')  # 다중 이미지 파일 가져오기

      # 각 이미지에 대해 검증
      for image in images:
        # 확장자 체크
        if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
          raise ValidationError(f"{image.name} 파일은 PNG 또는 JPG 형식이어야 합니다.")
        
        # 파일 크기 제한 (15MB)
        if image.size > 15 * 1024 * 1024:
          raise ValidationError(f"{image.name} 파일의 크기는 15MB를 초과할 수 없습니다.")

      return cleaned_data

# class NoteImageForm(forms.ModelForm):
#     class Meta:
#         model = NoteImage
#         fields = ('image',)  # 이미지 필드만 포함

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     def clean_image(self):
#         image = self.cleaned_data.get('image')
        
#         if image:
#             # 이미지 형식 체크
#             if not image.name.endswith(('.png', '.jpg', '.jpeg')):
#                 raise ValidationError("이미지는 PNG 또는 JPG 형식이어야 합니다.")
            
#             # 이미지 크기 제한 예시 (5MB)
#             if image.size > 15 * 1024 * 1024:
#                 raise ValidationError("이미지 파일 크기는 15MB를 초과할 수 없습니다.")
        
#         return image
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'note',)