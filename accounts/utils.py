import uuid
from django.core.mail import send_mail
from django.urls import reverse
from .models import SSOSession

def send_verification_email(user):
    """
    Sends a verification email to the specified user.

    This function generates a unique verification token, saves it to the user's profile,
    and sends an email containing a verification link to the user's email address.

    Args:
        user (User): The user object to whom the verification email will be sent. 
                     The user object must have a profile attribute with a verification_token field.

    Returns:
        None
    """
    token = str(uuid.uuid4())
    user.profile.verification_token = token
    user.profile.save()
    verification_link = reverse('confirm_email', args=[token])
    subject = 'Email Verification'
    message = f'Click the link to verify your email for registration at ITC SSO: http://localhost:8000{verification_link}'

    send_mail(subject, message, 'from@example.com', [user.username + '@iitb.ac.in'])

def send_reset_password_email(user):
    """
    Sends a reset password email to the specified user.

    This function generates a unique reset token, saves it to the user's profile,
    and sends an email containing a link to reset the password.

    Args:
        user (User): The user object to whom the reset password email will be sent.

    Returns:
        None

    Raises:
        Exception: If there is an issue with sending the email.

    Example:
        send_reset_password_email(user)
    """
    token = str(uuid.uuid4())
    user.profile.reset_token = token
    user.profile.save()

    reset_link = reverse('reset_password', args=[token])
    subject = 'Reset Password'
    message = f'Click the link to reset your password at ITC SSO: http://localhost:8000{reset_link}'

    send_mail(subject, message, 'from@example.com', [user.username + '@iitb.ac.in'])


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
