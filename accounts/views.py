from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib import messages
from .models import Profile
from .forms import RegistrationForm, LoginForm, EditProfileForm
from .utils import send_verification_email

def home(request):
    if Profile.objects.filter(user=request.user).exists():
        return render(request, 'home_logined.html')
    else:
        return render(request, 'home.html')

def logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_verification_email(user)
            messages.success(request, 'Registration successful. Please check your email to verify your account.')
            return redirect('email_sent')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def email_sent(request):
    return render(request, 'email_sent.html')

def confirm_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.verification_token = ''
        profile.save()
        return render(request, 'confirmed.html')
    except Profile.DoesNotExist:
        return render(request, 'confirmed.html', {'error': 'Invalid token'})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            roll = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=roll, password=password)
            if Profile.objects.get(user=user).email_verified == False:
                messages.error(request, 'Please verify your email to login')
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid roll number or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('home')
    else:
        form = EditProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'reset_password.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

def documentation(request):
    return render(request, 'documentation.html')