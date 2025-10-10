from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Profile, Project, LoginSession, SSOSession
from .forms import RegistrationForm, LoginForm, EditProfileForm, ProjectForm
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
    as well as all verified Project. If the user is not logged in, show the default homepage.
    """

    project = Project.objects.filter(is_verified=True)

    if request.user.is_authenticated:
        sso_sessions = SSOSession.objects.filter(user=request.user).order_by('-created_at')[0:5]
        
        return render(request, 'home.html', {
            'sso_sessions': sso_sessions,
            'user': request.user,
            'Project': project,
        })
    else:
        return render(request, 'home.html', {
            'sso_sessions': None,
            'Project': project,
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
                    
                    # Get next URL from POST data if available, otherwise from GET parameter
                    next_url = request.POST.get('next', next_url)
                    
                    messages.success(request, f'Welcome, {user.username}!')
                    # Use the next_url directly instead of hardcoding 'home'
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
                
            # Deactivate all active login sessions for this user
            # This will trigger the save method which decrements the active_logins counter
            for session in LoginSession.objects.filter(user=request.user, active=True):
                session.active = False
                session.save()
                
        except SSOSession.DoesNotExist:
            logger.error(f"Session not found for user {request.user.username}")
    
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    next_url = request.GET.get('next', 'login')
    return redirect(next_url)



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            roll = form.cleaned_data["roll"]
            name = form.cleaned_data["name"]
            dept = form.cleaned_data["department"]
            year = form.cleaned_data["passing_year"]
            degree = form.cleaned_data["degree"]
            password = form.cleaned_data["password1"]

            # Check if an unverified user exists
            user, created = User.objects.get_or_create(username=roll)

            if created:
                user.set_password(password)
                user.email = f'{roll}@iitb.ac.in'
                user.save()

                Profile.objects.create(
                    user=user,
                    roll=roll,
                    name=name,
                    department=dept,
                    passing_year=year,
                    degree=degree
                )
            else:
                profile = Profile.objects.get(user=user)
                if profile.email_verified:
                    messages.error(request, "This roll number is already registered and verified.")
                    return redirect('login')

                # Update user and profile
                user.set_password(password)
                user.email = f'{roll}@iitb.ac.in'
                user.save()

                profile.name = name
                profile.department = dept
                profile.passing_year = year
                profile.degree = degree
                profile.save()

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
        if profile:
            profile.email_verified = True
            profile.verification_token = ''  # Clear the token after use
            profile.save()
            messages.success(request, 'Email verified successfully! You can now login.')
            return render(request, 'confirmed.html')
    except Profile.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
        return render(request, 'confirmed.html', {'error': 'Invalid token'})
    except Exception as e:
        messages.error(request, f'Verification failed: {str(e)}')
        return render(request, 'confirmed.html', {'error': f'Verification failed: {str(e)}'})


def forgotpassword(request):
    """
    Handle password reset requests. Send a reset password email to the user.
    """
    if request.method == 'POST':
        roll = request.POST.get('roll')
        try:
            user = User.objects.get(username=roll)
            send_reset_password_email(user)
            messages.success(request, 'Password reset email sent. Please check your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this roll number.')
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            messages.error(request, 'An error occurred while processing your request.')

    return render(request, 'forgotpassword.html')


def resetpassword(request, token):
    """
    Allow users to reset their password using the reset token.
    Handles password validation and updates user password securely.
    """
    try:
        profile = Profile.objects.get(reset_token=token)
        user = profile.user
        
        if request.method == 'POST':
            pass1 = request.POST.get('password1')
            pass2 = request.POST.get('password2')
            
            if pass1 == pass2:
                if len(pass1) < 8:
                    messages.error(request, 'Password must be at least 8 characters long.')
                else:
                    # Update the user's password
                    user.set_password(pass1)
                    user.save()
                    
                    # Clear the reset token
                    profile.reset_token = ''
                    profile.save()
                    
                    messages.success(request, 'Password has been reset successfully. Please login with your new password.')
                    return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        
        return render(request, 'resetpassword.html', {'token': token})
        
    except Profile.DoesNotExist:
        messages.error(request, 'Invalid or expired reset token.')
        return redirect('forgotpassword')


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
def add_project(request):
    """
    Allow authenticated users to add new projects
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project added successfully. Waiting for verification.')
            return redirect('manage_projects')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/add_project.html', {'form': form})

@login_required
def manage_projects(request):
    """
    Show user's projects and their status
    """
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'projects/manage_projects.html', {'projects': projects})

@login_required
def project_details(request, project_id):
    """
    Show project details and statistics
    """
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    active_sessions = LoginSession.objects.filter(project=project, active=True).count()
    
    return render(request, 'projects/project_details.html', {
        'project': project,
        'active_sessions': active_sessions,
        'total_sessions': LoginSession.objects.filter(project=project).count()
    })

@user_passes_test(lambda u: u.is_staff)
def verify_project(request, project_id):
    """
    Allow admin to verify projects
    """
    project = get_object_or_404(Project, id=project_id)
    project.is_verified = True
    project.save()
    messages.success(request, f'Project {project.name} has been verified.')
    return redirect('admin:accounts_project_changelist')

@login_required(login_url='/login/')
def project_ssocall(request, id):
    project = get_object_or_404(Project, id=id)    
    user = request.user

    if not project.can_accept_new_login():
        messages.error(request, 'This unverified project has reached its maximum login limit (10 active logins).')
        return redirect('home')

    newid = generate_encrypted_id(user.id, project.id)
    project_url = project.redirect_url

    # First clean up any expired sessions for this project
    for session in LoginSession.objects.filter(project=project, active=True):
        if not session.is_session_valid():
            # The is_session_valid method will handle the deactivation and counter decrement
            pass

    # Update the active_logins count to ensure it's accurate
    active_count = LoginSession.objects.filter(project=project, active=True).count()
    if project.active_logins != active_count:
        project.active_logins = active_count
        project.save()

    # Check if there's an existing valid session
    if LoginSession.objects.filter(sessionkey=newid).exists():
        session = LoginSession.objects.get(sessionkey=newid)
        if session.is_session_valid():
            return redirect(f'{project_url}?accessid={session.sessionkey}')
        else:
            # Session has expired, it's already been deactivated by is_session_valid
            session.delete()  # We can delete it now as we'll create a new one

    # Create a new session and increment the counter
    session = LoginSession.objects.create(sessionkey=newid, user=user, project=project)
    project.active_logins += 1
    project.save()

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
        # Session has been marked as inactive and counter decremented by is_session_valid
        return JsonResponse({"error": "Session has expired"}, status=status.HTTP_403_FORBIDDEN)

    person = Profile.objects.get(user=session.user)
    return JsonResponse({
        "name": person.name,
        "roll": person.roll,
        "department": person.department,
        "degree": person.degree,
        "passing_year": person.passing_year
    }, status=200)

@login_required
def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('manage_projects')
    return redirect('project_details', project_id=project_id)