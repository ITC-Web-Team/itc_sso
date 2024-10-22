from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Projects, LoginSession, SSOSession
from .forms import RegistrationForm, LoginForm, EditProfileForm
from .utils import send_verification_email, send_reset_password_email
from rest_framework.decorators import api_view
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
import logging
from django.contrib.auth.models import User

# Initialize logger
logger = logging.getLogger(__name__)

def home(request):
    """
    Show the homepage. If the user is logged in, display their current and previous SSO sessions.
    If the user is not logged in, show the default homepage.
    """
    if request.user.is_authenticated:
        # Fetch all SSO sessions for the logged-in user
        sso_sessions = SSOSession.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'home.html', {
            'sso_sessions': sso_sessions,
            'user': request.user,
        })
    else:
        # If user is not authenticated, show the default home page
        return render(request, 'home.html', {
            'sso_sessions': None,
        })


def logout_view(request):
    """ Log the user out and update the SSO session to inactive """
    if request.user.is_authenticated:
        SSOSession.objects.filter(user=request.user, device=request.META['HTTP_USER_AGENT']).update(active=False)
    
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    
    return redirect('login')


def register(request):
    """
    Handle user registration, send a verification email, and
    redirect to the email_sent page upon successful registration.
    """
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm
from .utils import send_verification_email  # Assuming this is your email utility

def register(request):
    """
    Handle user registration, send a verification email, and
    redirect to the email_sent page upon successful registration.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            roll = form.cleaned_data['roll']

            existing_user = User.objects.filter(username=roll).first()
            existing_profile = Profile.objects.filter(roll=roll).first()

            if existing_user and existing_profile and not existing_profile.email_verified:
                existing_user.delete()

            user = form.save()
            user.email = f'{roll}@iitb.ac.in'  
            user.save()

            send_verification_email(user)

            messages.success(request, 'Registration successful. Please check your LDAP email to verify your account.')

            return redirect('email_sent')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})



def email_sent(request):
    """ Render the page after email is sent for verification """
    email = request.GET.get('email')
    return render(request, 'email_sent.html', {'email': email})

def confirm_email(request, token):
    """
    Confirm user email by matching the verification token. If token matches,
    the email is verified.
    """
    try:
        profile = Profile.objects.get(verification_token=token)
        profile.email_verified = True
        profile.verification_token = ''
        profile.save()
        return render(request, 'confirmed.html')
    except Profile.DoesNotExist:
        return render(request, 'confirmed.html', {'error': 'Invalid token'})


def login_view(request):
    """
    Handle user login, check if the email is verified, and provide appropriate
    messages for success or failure.
    """
    if request.method == 'POST':
        try:
            roll = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=roll, password=password)

            if user is not None:
                if user.profile.email_verified:
                    login(request, user)

                    # Handle SSO session management

                    device = request.META['HTTP_USER_AGENT']  # Get device info (browser info)
                    try:
                        sso_session = SSOSession.objects.get(user=user, device=device, active=True)
                        if not sso_session.is_session_valid():
                            sso_session.device = device
                            sso_session.active = True
                            sso_session.created_at = timezone.now()  
                            sso_session.save()
                        else:
                            pass
                    except SSOSession.DoesNotExist:
                        SSOSession.objects.create(
                            user=user,
                            device=device,
                            active=True,
                        )

                    # Check for 'next' parameter in the URL for redirection after login
                    next_url = request.GET.get('next', 'home')  # Defaults to 'home' if next isn't present
                    messages.success(request, f'Welcome, {user.username}!')
                    return redirect(next_url)
                else:
                    # Email is not verified
                    messages.error(request, 'Email not verified. Please verify your email to log in.')
            else:
                # User authentication failed
                messages.error(request, 'Invalid roll number or password, are you registered?')
        except Exception as e:
            logger.error(f"Login error: {e}")  # Log the error for debugging in production
            messages.error(request, 'An error occurred while logging in. Please try again.')

    # Render the login form on GET or failed POST
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def edit_profile(request):
    """
    Allow users to edit their profile. Handle the form submission to update
    profile data.
    """
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


def documentation(request):
    """ Render the documentation page """
    return render(request, 'documentation.html')

def forgotpassword(request):
   
    if request.method == 'POST':
        roll = request.POST.get('roll')
        send_reset_password_email(roll)
        return messages.success(request, 'Password reset email sent. Please check your email.')

    return render(request, 'forgotpassword.html')
   


def resetpassword(request, token):
    user = Profile.objects.get(reset_token=token)
    if request.method == 'POST':
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 == pass2:
            user.set_password(pass1)
            user.save()
            return redirect('login')

        else:
            return messages.error(request, 'Passwords do not match.')
        
        
    return render(request, 'resetpassword.html')
    




@login_required
def project_ssocall(request, id):
    """
    Handle SSO (Single Sign-On) login for specific projects.
    If a valid session exists, the user is redirected to the project URL;
    otherwise, a new session is created.
    """
    project = get_object_or_404(Projects, id=id)
    
    # Check for an existing valid session
    existing_session = LoginSession.objects.filter(user=request.user, project=project).first()
    if existing_session and existing_session.is_session_valid():
        project_url = project.redirect_url
        return redirect(f"{project_url}?accessid={existing_session.id}")
    
    # Create a new session if no valid session exists
    session = LoginSession.objects.create(user=request.user, project=project)
    project_url = project.redirect_url
    return redirect(f"{project_url}?accessid={session.id}")


@api_view(['POST'])
def return_user_data(request):
    """
    API to return user profile data based on the session ID.
    Ensures session validity and expiration check.
    """
    session_id = request.data.get('id')
    if not session_id:
        return JsonResponse({"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = LoginSession.objects.get(id=session_id)
    except LoginSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    if not session.is_session_valid():
        return JsonResponse({"error": "Session has expired"}, status=status.HTTP_403_FORBIDDEN)

    person = Profile.objects.get(user=session.user)
    return JsonResponse({
        "name": person.name,
        "roll": person.roll,
        "branch": person.branch,
        "passing_year": person.passing_year,
        "course": person.course
    }, status=200)

