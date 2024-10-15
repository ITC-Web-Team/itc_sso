from django.urls import path
from .views import home, register, email_sent, confirm_email, user_login, edit_profile, CustomPasswordResetView, CustomPasswordResetDoneView, documentation

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('email-sent/', email_sent, name='email_sent'),
    path('confirm-email/<str:token>/', confirm_email, name='confirm_email'),
    path('login/', user_login, name='login'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('reset-password/', CustomPasswordResetView.as_view(), name='reset_password'),
    path('password-reset-done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('docs/', documentation, name='docs'),
]
