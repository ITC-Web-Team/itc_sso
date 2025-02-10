import uuid
from django.core.mail import send_mail
from django.urls import reverse
import environ
import os
from pathlib import Path
from .models import SSOSession
import hashlib
import base64
import uuid
from datetime import datetime
from .models import LoginSession
import time
from .email_utils import send_email
from django.template.loader import render_to_string


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env'))

def send_verification_email(user):
    """
    Send email verification link to the user
    """
    # Generate a unique verification token
    token = str(uuid.uuid4())
    
    # Update user's profile with the verification token
    profile = user.profile
    profile.verification_token = token
    profile.save()
    
    # Construct verification link
    verification_link = f"{env('HOST_URL')}{reverse('confirm_email', kwargs={'token': token})}"
    
    # Render HTML email template
    html_message = render_to_string('emails/verification_email.html', {
        'user': user,
        'verification_link': verification_link
    })
    
    # Send email
    subject = 'Verify Your Email - ITC SSO'
    message = f'Click the following link to verify your email: {verification_link}'
    
    return send_email(
        subject, 
        message, 
        [user.email], 
        html_message=html_message
    )

def send_reset_password_email(user):
    """
    Send password reset link to the user
    """
    # Generate a unique reset token
    token = str(uuid.uuid4())
    
    # Update user's profile with the reset token
    profile = user.profile
    profile.reset_token = token
    profile.save()
    
    # Construct reset link
    reset_link = f"{env('HOST_URL')}{reverse('resetpassword', kwargs={'token': token})}"

    # Render HTML email template
    html_message = render_to_string('emails/reset_password_email.html', {
        'user': user,
        'reset_link': reset_link
    })
    
    # Send email
    subject = 'Password Reset - ITC SSO'
    message = f'Click the following link to reset your password: {reset_link}'
    
    return send_email(
        subject, 
        message, 
        [user.email], 
        html_message=html_message
    )


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


def generate_encrypted_id(user_id, project_id):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    raw_string = f"{user_id}-{project_id}-{timestamp}"
    hash_object = hashlib.sha256(raw_string.encode())
    encrypted_id = base64.urlsafe_b64encode(hash_object.digest()).decode('utf-8')
    if LoginSession.objects.filter(sessionkey=encrypted_id).exists():
        time.sleep(1)
        return generate_encrypted_id(user_id, project_id)
    return encrypted_id
