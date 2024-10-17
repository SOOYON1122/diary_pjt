from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'email',
            'nickname',
            'profile_image',
        )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'email',
            'nickname',
            'profile_image',
        )