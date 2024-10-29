from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('mypage/<int:user_pk>/', views.mypage, name="mypage"),   
    path('mypage/<int:user_pk>/update/', views.update, name="update"),   
    path('mypage/<int:user_pk>/delete/', views.delete, name="delete"),

    path('findid/', views.findid, name="findid"),
    path('testemail/', views.email, name="email"),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]