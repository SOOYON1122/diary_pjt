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
            # user = form.save()
            # auth_login(request, user)
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return render(request, 'accounts/emailsent.html')
    else:
        form = CustomUserCreationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/signup.html', context)

# 활성화 이메일 보내기
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .tokens import account_activation_token

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('accounts/activateaccount.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        return render(request, 'accounts/emailsent.html')
    else:
        redirect('accounts:singup')

from django.contrib.auth import get_user_model

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # messages.success(request, '인증이 성공했습니다. 이제 로그인이 가능합니다.')
        return redirect('accounts:login')
    else:
        # messages.error(request, '인증 링크가 유효하지 않습니다. 다른 이메일로 재시도해보세요.')
    
        return redirect('diaries:index')
    

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
def mypage(request, user_username):
    return render(request, 'accounts/mypage.html')

@login_required
def update(request, user_username):
    if request.method == "POST":
        form_user = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        form_password = PasswordChangeForm(request.user, request.POST)
        if form_user.is_valid() and form_password.is_valid():
            form_user.save()
            user = form_password.save()
            update_session_auth_hash(request, user)
            return redirect('accounts:mypage', user.username)
    else:
        form_user = CustomUserChangeForm(instance=request.user)
        form_password = PasswordChangeForm(request.user)
    context = {
        'form_user' : form_user,
        'form_password' : form_password,
    }
    return render(request, 'accounts/update.html', context)

@login_required
def delete(request, user_username):
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
                return render(request, 'accounts/emailsent.html')
            
        except:
            print('fail', email)
            messages.info(request, 'There is no username along with the email')
    context = {}
    return render(request, 'accounts/findid.html', context)

# 이메일 보내기 테스트
# from django.core.mail import send_mail
# from django.conf import settings
# from django.shortcuts import redirect

# def email(request):
#     subject = 'Thank you for registering to our site'
#     message = 'It means a world to us'
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = ['example@gmail.com']
#     send_mail(subject, message, email_from, recipient_list, fail_silently=False)
#     return redirect('accounts:findid')