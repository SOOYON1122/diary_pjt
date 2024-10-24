from django.urls import path
from . import views

app_name = "diaries"

urlpatterns = [
  path('', views.index, name="index"),
  path('create-diary/', views.creatediary, name="create_diary"),
  path('my-diary/', views.mydiary, name="my_diary"),
  path('<int:diary_pk>/', views.noteindex, name="note_index"),
  path('<int:diary_pk>/create/', views.createnote, name='create_note'),
  path('<int:diary_pk>/<int:note_pk>/', views.notedetail, name="note_detail"),
  path('<int:diary_pk>/<int:note_pk>/comments/', views.comments_create, name='comments_create'),
  path('<int:diary_pk>/<int:note_pk>/<int:comment_pk>/delete/', views.comments_delete, name='comments_delete'),
  path('<int:diary_pk>/<int:note_pk>/likes/', views.likes, name='likes'),
]