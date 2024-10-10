from django.urls import path
from . import views

app_name = "diaries"

urlpatterns = [
  path('', views.index, name="index"),
  path('create-diary/', views.creatediary, name="create_diary"),
  path('my-diary/', views.mydiary, name="my_diary"),
]