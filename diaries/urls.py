from django.urls import path
from . import views

app_name = "diaries"

urlpatterns = [
    path('', views.index, name="index"),
    path('create-diary/', views.creatediary, name="create_diary"),
    path('my-diary/', views.mydiary, name="my_diary"),
    path('<int:diary_pk>/', views.notelist, name="note_list"),  # 다이어리의 모든 노트를 보여주는 페이지
    path('<int:diary_pk>/note/<int:note_pk>/', views.notedetail, name="note_detail"),  # 특정 노트 세부정보
    path('<int:diary_pk>/create/', views.createnote, name='create_note'),
    path('<int:diary_pk>/<int:note_pk>/comments/', views.comments_create, name='comments_create'),
    path('<int:diary_pk>/<int:note_pk>/<int:comment_pk>/delete/', views.comments_delete, name='comments_delete'),
    path('<int:diary_pk>/<int:note_pk>/likes/', views.likes, name='likes'),
    path('<int:diary_pk>/note/<int:note_pk>/delete/', views.delete_note, name='delete_note'),
    path('diary/<int:diary_pk>/note/<int:note_pk>/edit/', views.editnote, name='edit_note'),
]




# from django.urls import path
# from . import views

# app_name = "diaries"

# urlpatterns = [
#   path('', views.index, name="index"),
#   path('create-diary/', views.creatediary, name="create_diary"),
#   path('my-diary/', views.mydiary, name="my_diary"),
#   # path('<int:diary_pk>/', views.notelist, name="note_list"),
#   path('<int:diary_pk>/create/', views.createnote, name='create_note'),
#   path('<int:diary_pk>/', views.notedetail, name="note_detail"),
#   path('<int:diary_pk>/<int:note_pk>/comments/', views.comments_create, name='comments_create'),
#   path('<int:diary_pk>/<int:note_pk>/<int:comment_pk>/delete/', views.comments_delete, name='comments_delete'),
#   path('<int:diary_pk>/<int:note_pk>/likes/', views.likes, name='likes'),
# ]