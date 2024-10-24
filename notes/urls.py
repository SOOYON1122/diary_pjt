from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'notes'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:note_pk>/comments/', views.comments_create, name='comments_create'),
    path('comments/<int:comment_pk>/delete/', views.comments_delete, name='comments_delete'),
    path('<int:note_pk>/likes/', views.likes, name='likes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
