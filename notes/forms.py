from django import forms
from .models import Note, NoteImage, Comment
from diaries.models import Diary


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        # fields = '__all__'
        fields = ('note_title', 'note_content', 'diary_id',)

    diary_id = forms.ModelChoiceField(queryset=Diary.objects.all(), label="다이어리 선택")


class NoteImageForm(forms.ModelForm):
    class Meta:
        model = NoteImage
        # fields = '__all__'
        fields = ('image',)

        # 이미지 업로드 수 제한두기
        def clean_image(self):
            images = self.cleaned_data.get('image')
            if len(images) > 3:  # 3개 이상 업로드 시 오류
                raise forms.ValidationError("이미지는 최대 3개까지만 업로드할 수 있습니다.")
            return images


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('user', 'note',)