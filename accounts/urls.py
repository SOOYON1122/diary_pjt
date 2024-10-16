from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('mypage/<int:user_pk>/', views.mypage, name="mypage"),   
    path('mypage/<int:user_pk>/update/', views.update, name="update"),   
    path('mypage/<int:user_pk>/delete/', views.delete, name="delete"),
]