from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings

# Create your views here.
def signup(request):
    if request.user.is_authenticated:
        return redirect('diaries:index')
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
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
        form_user = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
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

@login_required
def delete(request, user_pk):
    request.user.delete()
    return redirect('diaries:index')

def findid(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user is not None:
                method_email = EmailMessage(
                    'Your ID is in the email',
                    str(user.username),
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                method_email.send(fail_silently=False)
                print('success', email)
                return render(request, 'accounts/idsent.html')
            
        except:
            print('fail', email)
            messages.info(request, 'There is no username along with the email')
    context = {}
    return render(request, 'accounts/findid.html', context)


# def send_email(request):
#     subject = 'message'
#     to = ['example@gmail.com']
#     from_email = settings.EMAIL_HOST_USER,
#     message = '이메일 테스트'
#     EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send(fail_silently=False)


# views.py
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

def email(request):
    subject = 'Thank you for registering to our site'
    message = 'It means a world to us'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['example@gmail.com']
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
    return redirect('accounts:findid')