from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Projects, LoginSession, SSOSession
from .forms import RegistrationForm, LoginForm, EditProfileForm
from .utils import send_verification_email, send_reset_password_email, generate_encrypted_id
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
import logging
from django.contrib.auth.models import User

# Initialize logger
logger = logging.getLogger(__name__)

# ------------------------------ General Views ------------------------------

def home(request):
    """
    Show the homepage. If the user is logged in, display their current and previous SSO sessions,
    as well as all available projects. If the user is not logged in, show the default homepage.
    """
    if request.user.is_authenticated:
        sso_sessions = SSOSession.objects.filter(user=request.user).order_by('-created_at')[0:5]
        projects = Projects.objects.all() 
        return render(request, 'home.html', {
            'sso_sessions': sso_sessions,
            'user': request.user,
            'projects': projects,
        })
    else:
        projects = Projects.objects.all()
        return render(request, 'home.html', {
            'sso_sessions': None,
            'projects': projects,
        })

def documentation(request):
    """ Render the documentation page """
    return render(request, 'documentation.html')

def login_view(request):
    """
    Handle user login and update SSO session information.
    """
    next_url = request.GET.get('next', 'home')

    if request.user.is_authenticated:
        messages.success(request, f'Welcome, {request.user.username}!')
        return redirect(next_url)

    if request.method == 'POST':
        if request.user.is_authenticated:
            messages.success(request, f'Welcome, {request.user.username}!')
            return redirect(next_url)
        
        try:
            roll = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=roll, password=password)

            if user is not None:
                if user.profile.email_verified:
                    login(request, user)

                    device = request.META['HTTP_USER_AGENT'][:100]
                    session_key = request.session.session_key

                    SSOSession.objects.update_or_create(
                        user=user,
                        session_key=session_key,
                        defaults={'device': device, 'active': True}
                    )
                    next_url = request.POST.get('next', next_url)
                    messages.success(request, f'Welcome, {user.username}!')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Email not verified. Please verify your email to log in.')
            else:
                messages.error(request, 'Invalid roll number or password, are you registered?')
        except Exception as e:
            logger.error(f"Login error: {e}")
            messages.error(request, 'An error occurred while logging in. Please try again.')

    form = LoginForm()
    return render(request, 'login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """
    Log the user out and update the SSO session to inactive.
    Redirect to the next URL if provided.
    """
    if request.user.is_authenticated:
        try:
            if request.session.session_key:
                session_key = request.session.session_key
                SSOSession.objects.filter(user=request.user, session_key=session_key).update(active=False)
            else:
                SSOSession.objects.filter(user=request.user, device=request.META['HTTP_USER_AGENT'][:100]).latest('created_at').update(active=False)
        except SSOSession.DoesNotExist:
            logger.error(f"Session not found for user {request.user.username}")
    
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    next_url = request.GET.get('next', 'login')
    return redirect(next_url)



def register(request):
    """
    Handle user registration, send a verification email, and
    redirect to the email_sent page upon successful registration.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
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

            return redirect('/email-sent' + f'?email={user.email}')
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


def forgotpassword(request):
    """
    Handle password reset requests. Send a reset password email to the user.
    """
    if request.method == 'POST':
        roll = request.POST.get('roll')
        send_reset_password_email(roll)
        messages.success(request, 'Password reset email sent. Please check your email.')
        return redirect('login')

    return render(request, 'forgotpassword.html')


def resetpassword(request, token):
    """
    Allow users to reset their password using the reset token.
    """
    user = Profile.objects.get(reset_token=token)
    if request.method == 'POST':
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        if pass1 == pass2:
            user.set_password(pass1)
            user.save()
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
        
    return render(request, 'resetpassword.html')


# ---------------------------- Profile and User Actions ----------------------------

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

# ---------------------------- Project and SSO Handling ----------------------------

@login_required
def project_ssocall(request, id):
    """
    Handle SSO (Single Sign-On) login for specific projects.
    If a valid session exists, the user is redirected to the project URL;
    otherwise, a new session is created.
    """
    project = get_object_or_404(Projects, id=id)    
    user = request.user

    newid = generate_encrypted_id(user.id, project.id)

    project_url = project.redirect_url
    if LoginSession.objects.filter(sessionkey = newid).exists():
        session = LoginSession.objects.get(sessionkey = newid)
        if session.is_session_valid():
            return redirect(f'{project_url}?accessid={session.sessionkey}')
        else:
            session.delete()
    session = LoginSession.objects.create(sessionkey = newid, user=user, project=project)

    return render(request, 'ssologin.html', {
        'project': project, 
        'redirecturl': f'{project_url}?accessid={session.sessionkey}',
        'user': user.profile.name
    })


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
        session = LoginSession.objects.get(sessionkey=session_id)
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