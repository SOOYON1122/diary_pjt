from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('diaries:index')
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('diaries:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/signup.html', context)
    

def login(request):
    if request.user.is_authenticated:
        return redirect('diaries:index')
    
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('diaries:index')
    else:
        form = AuthenticationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/login.html', context)
    
@login_required
def logout(request):
    auth_logout(request)
    return redirect('diaries:index')

@login_required
def mypage(request, user_pk):
    return render(request, 'accounts/mypage.html')

@login_required
def update(request, user_pk):
    if request.method == "POST":
        form_user = CustomUserChangeForm(request.POST, instance=request.user)
        form_password = PasswordChangeForm(request.user, request.POST)
        if form_user.is_valid() and form_password.is_valid():
            form_user.save()
            user = form_password.save()
            update_session_auth_hash(request, user)
            return redirect('accounts:mypage', user.pk)
    else:
        form_user = CustomUserChangeForm(instance=request.user)
        form_password = PasswordChangeForm(request.user)
    context = {
        'form_user' : form_user,
        'form_password' : form_password,
    }
    return render(request, 'accounts/update.html', context)