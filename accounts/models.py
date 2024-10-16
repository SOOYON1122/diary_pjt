import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return 'user_{0}/{1}'.format(instance.user.username, filename)

class User(AbstractUser):
    nickname = models.CharField(max_length=10)
    profile_image = models.ImageField(upload_to=user_directory_path)