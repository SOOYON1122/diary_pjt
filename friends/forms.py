from django import forms
from .models import Friendship


class FriendshipForm(forms.Form):

  to_user = forms.CharField(label="친구 검색", max_length=150)

  class Meta:
    model = Friendship
    fields = ('to_user',)