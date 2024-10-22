import uuid
from django.core.mail import send_mail
from django.urls import reverse
import environ
import os
from pathlib import Path
from .models import SSOSession

# Initialize environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

def send_verification_email(user):
    """
    Sends a verification email to the specified user.

    Args:
        user (User): The user object to whom the verification email will be sent.

    Returns:
        None
    """
    token = str(uuid.uuid4())
    user.profile.verification_token = token
    user.profile.password = user.password
    user.profile.save()

    # Use the environment variable for the host URL
    host_url = env('HOST_URL')  
    verification_link = reverse('confirm_email', args=[token])
    full_link = f'{host_url}{verification_link}'
    
    subject = 'Email Verification'
    message = f'Click the link to verify your email for registration at ITC SSO: {full_link}'

    send_mail(subject, message, 'from@example.com', [f'{user.username}@iitb.ac.in'])

def send_reset_password_email(user):
    """
    Sends a reset password email to the specified user.

    Args:
        user (User): The user object to whom the reset password email will be sent.

    Returns:
        None
    """
    token = str(uuid.uuid4())
    user.profile.reset_token = token
    user.profile.save()

    # Use the environment variable for the host URL
    host_url = env('HOST_URL')  
    reset_link = reverse('reset_password', args=[token])
    full_link = f'{host_url}{reset_link}'
    
    subject = 'Reset Password'
    message = f'Click the link to reset your password at ITC SSO: {full_link}'

    send_mail(subject, message, 'from@example.com', [f'{user.username}@iitb.ac.in'])


def check_sso_session(request):
    if 'sso_token' in request.COOKIES:
        sso_token = request.COOKIES['sso_token']
        try:
            session = SSOSession.objects.get(id=sso_token, active=True)
            return session
        except SSOSession.DoesNotExist:
            return None
    return None

def get_user_from_sso(request):
    session = check_sso_session(request)
    if session:
        return session.user
    return None
