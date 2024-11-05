from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

app_name = "accounts"

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('mypage/<str:user_username>/', views.mypage, name="mypage"),   
    path('mypage/<str:user_username>/update/', views.update, name="update"),   
    path('mypage/<str:user_username>/delete/', views.delete, name="delete"),
    # 아이디 찾기
    path('findid/', views.findid, name="findid"),
    # path('testemail/', views.email, name="email"),
    # 비밀번호 초기화
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # 이메일 활성화
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]