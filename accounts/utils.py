import uuid
from django.core.mail import send_mail
from django.urls import reverse

def send_verification_email(user):
    token = str(uuid.uuid4())
    user.profile.verification_token = token
    user.profile.save()

    verification_link = reverse('confirm_email', args=[token])
    subject = 'Email Verification'
    message = f'Click the link to verify your email: http://localhost:8000{verification_link}'

    send_mail(subject, message, 'from@example.com', [user.username + '@iitb.ac.in'])
