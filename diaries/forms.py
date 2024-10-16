from django import forms
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Diary, Note, NoteImage


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
      self.fields['diary_friends'].queryset = self.current_user.friends.all()  # friends 관계가 설정되어 있다고 가정

  def clean_diary_friends(self):
    friends = self.cleaned_data.get('diary_friends')
    if friends.count() > 7:
      raise ValidationError("다이어리에 추가할 친구는 최대 7명입니다.")
    return friends


class NoteForm(forms.ModelForm):
  class Meta:
    model = Note
    fields = ['note_title', 'note_content', 'diary']

  def __init__(self, *args, **kwargs):
    self.current_user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super().clean()
    diary = cleaned_data.get('diary')

    if diary:
      if diary.user != self.current_user and not diary.diary_friends.filter(id=self.current_user.id).exists():
        raise ValidationError("노트를 작성할 권한이 없습니다.")

    return cleaned_data


class NoteImageForm(forms.ModelForm):
  class Meta:
    model = NoteImage
    fields = ['image']

  def __init__(self, *args, **kwargs):
    self.note = kwargs.pop('note', None)
    super().__init__(*args, **kwargs)

  def clean_image(self):
    image = self.cleaned_data.get('image')
    if self.note:
      if self.note.note_images.count() >= 10:
        raise ValidationError("노트 당 최대 10장의 이미지만 업로드할 수 있습니다.")
    return image


NoteImageFormSet = inlineformset_factory(
  Note,
  NoteImage,
  form=NoteImageForm,
  extra=3,  # 초기 폼 개수
  can_delete=True,
  max_num=10,
  validate_max=True
)


User = get_user_model()

class NoteImageFormSetTest(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='user', password='password')
    self.diary = Diary.objects.create(user=self.user, diary_title='Diary', diary_content='Content', diary_category='Category')
    self.diary.diary_friends.add(self.user)

  def test_note_image_formset_valid(self):
    note = Note.objects.create(user=self.user, diary=self.diary, note_title='Note', note_content='Content')
    image1 = SimpleUploadedFile("image1.jpg", b"file_content", content_type="image/jpeg")
    image2 = SimpleUploadedFile("image2.jpg", b"file_content", content_type="image/jpeg")
    form_data = {
      'note_images-TOTAL_FORMS': '2',
      'note_images-INITIAL_FORMS': '0',
      'note_images-MIN_NUM_FORMS': '0',
      'note_images-MAX_NUM_FORMS': '10',
      'note_images-0-image': image1,
      'note_images-1-image': image2,
    }
    formset = NoteImageFormSet(data=form_data, files=request.FILES, instance=note)
    self.assertTrue(formset.is_valid())
  
  def test_note_image_formset_exceeds_max(self):
    note = Note.objects.create(user=self.user, diary=self.diary, note_title='Note', note_content='Content')
    for i in range(10):
      NoteImage.objects.create(note=note, image='path/to/image.jpg')
    image11 = SimpleUploadedFile("image11.jpg", b"file_content", content_type="image/jpeg")
    form_data = {
      'note_images-TOTAL_FORMS': '1',
      'note_images-INITIAL_FORMS': '10',
      'note_images-MIN_NUM_FORMS': '0',
      'note_images-MAX_NUM_FORMS': '10',
      'note_images-0-image': image11,
    }
    formset = NoteImageFormSet(data=form_data, files=request.FILES, instance=note)
    self.assertFalse(formset.is_valid())
