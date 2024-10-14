# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm
from .models import Profile
import uuid
from requests import request
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            roll = form.cleaned_data['roll'].lower()

            profile = Profile.objects.create(
                user=user,
                roll=roll,
                verification_token=str(uuid.uuid4())
            )
            login(request, user)
            send_verification_email(request, roll, profile.verification_token)
            print("check you gmail") # Redirect to home page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})




# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # Deactivate account till it is verified
#             user.save()
#             profile = Profile.objects.create(
#                 user=user,
#                 phone=form.cleaned_data['phone'],
#                 address=form.cleaned_data['address'],
#                 verification_token=str(uuid.uuid4())
#             )
#             send_verification_email(request, user, profile.verification_token)
#             messages.success(request, 'Registration successful. Please check your email to verify your account.')
#             return redirect('registration_success')  # Redirect to a new page
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'register.html', {'form': form})

# def registration_success(request):
#     return render(request, 'registration_success.html')



def send_verification_email(request, roll, token):
    current_site = get_current_site(request)
    subject = 'Verify your email'
    verification_link = f"http://{current_site.domain}{reverse('verify_email', args=[token])}"
    message = f'Click this link to verify your email: {verification_link}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [ roll.lower() + '@iitb.ac.in' ]
    send_mail(subject, message, from_email, recipient_list)

def verify_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.verification_token = ''
        profile.save()
        return render(request, 'email_verification.html', {'success': True})
    except Profile.DoesNotExist:
        return render(request, 'email_verification.html', {'success': False})