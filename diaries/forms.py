from PIL import Image
from django import forms
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.db.models import Q
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Diary, Note, NoteImage, Comment
from friends.models import Friendship

User = get_user_model()

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
    class Meta:
        model = Note
        fields = ['note_title', 'note_content']


class NoteImageForm(forms.ModelForm):
    class Meta:
        model = NoteImage
        fields = ('image',)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image is not None:
            
            # 파일 크기 제한 (15MB)
            if image.size > 15 * 1024 * 1024:
                raise ValidationError("이미지 파일 크기는 15MB를 초과할 수 없습니다.")
            
            # 이미지가 실제 이미지인지 검증
            try:
                img = Image.open(image)
                img.verify()
            except Exception:
                raise ValidationError("유효하지 않은 이미지 파일입니다.")
        
        return image


# Note와 연결된 NoteImage의 인라인 폼셋
NoteImageFormSet = inlineformset_factory(
    Note, NoteImage,  # Note에 연결된 NoteImage
    form=NoteImageForm,
    extra=10,  # 기본으로 최대 5개의 이미지를 업로드할 수 있게 설정
    max_num=10,  # 최대 10개의 이미지를 업로드할 수 있도록 제한
    can_delete=True  # 이미지를 개별 삭제할 수 있게 설정
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'note',)

