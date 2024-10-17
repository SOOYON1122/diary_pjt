from django.urls import path
from . import views

app_name = "friends"

urlpatterns = [
  path('add-friend', views.addfriend, name="add_friend"),
  path('search-friend/', views.searchfriend, name="search_friend"),
  path('my-friends/', views.myfriends, name="my_friends"),
  path('reject-friend/<int:friend_id>/', views.rejectfriend, name="reject_friend"),
  path('accept-friend/<int:friend_id>/', views.acceptfriend, name="accept_friend"),
]