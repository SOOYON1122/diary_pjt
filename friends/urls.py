from django.urls import path
from . import views

app_name = "friends"

urlpatterns = [
  path('add-friend', views.addfriend, name="add_friend"),
  path('my-friends/', views.myfriends, name="my_friends"),
]