from django import forms
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Diary, Note, NoteImage, Comment
from friends.models import Friendship



User = get_user_model()

class DiaryForm(forms.ModelForm):
  class Meta:
    model = Diary
    fields = ['diary_title', 'diary_content', 'diary_category', 'diary_img']

  # 친구 목록에서 친구 추가하는 걸 Template에서 js로 동적 처리 예정
  diary_friends = forms.ModelMultipleChoiceField(
    queryset=None,
    widget=forms.SelectMultiple(attrs={
      'id': 'friend-select',
      'class': 'friend-select',
    }),
    required=False
  )

  def __init__(self, *args, **kwargs):
    self.current_user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

    if self.current_user:
      # 현재 사용자의 친구 요청을 기반으로 친구 목록 가져오기
      friends_queryset = Friendship.objects.filter(
        from_user=self.current_user,
        is_friend=True
      ).values_list('to_user', flat=True)

      self.fields['diary_friends'].queryset = User.objects.filter(id__in=friends_queryset)

  def clean_diary_friends(self):
    friends = self.cleaned_data.get('diary_friends')
    if friends.count() > 7:
      raise ValidationError("다이어리에 추가할 친구는 최대 7명입니다.")
    return friends


class NoteForm(forms.ModelForm):
  class Meta:
    model = Note
    fields = ('note_title', 'note_content', 'diary',)  # 'diary'를 fields에 추가

  diary = forms.ModelChoiceField(queryset=Diary.objects.all(), label="다이어리 선택")

  def __init__(self, *args, **kwargs):
    self.current_user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super().clean()
    diary = cleaned_data.get('diary')

    # diary가 None인지 체크
    if diary is None:
      raise ValidationError("다이어리를 선택해야 합니다.")

    # diary가 None이 아닌 경우만 다음 체크 수행
    if diary.user_id != self.current_user and not diary.diary_friends.filter(id=self.current_user.id).exists():
      raise ValidationError("노트를 작성할 권한이 없습니다.")

    return cleaned_data



class NoteImageForm(forms.ModelForm):
    class Meta:
        model = NoteImage
        fields = ('image',)  # 이미지 필드만 포함

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        if image:
            # 이미지 형식 체크
            if not image.name.endswith(('.png', '.jpg', '.jpeg')):
                raise ValidationError("이미지는 PNG 또는 JPG 형식이어야 합니다.")
            
            # 이미지 크기 제한 예시 (5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("이미지 파일 크기는 5MB를 초과할 수 없습니다.")
        
        return image
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'note',)