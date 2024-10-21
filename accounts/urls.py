from django.urls import path
from .views import (
    home, 
    register, 
    email_sent, 
    confirm_email, 
    login_view, 
    logout_view, 
    project_ssocall, 
    edit_profile, 
    documentation, 
    return_user_data
)

# URL patterns for the application
urlpatterns = [
    # Home page
    path('', home, name='home'),

    # User registration
    path('register/', register, name='register'),

    # Email sent confirmation
    path('email-sent/', email_sent, name='email_sent'),

    # Email confirmation with token
    path('confirm-email/<str:token>/', confirm_email, name='confirm_email'),

    # User login and logout
    path('login/', login_view, name='login'),
    path('accounts/login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout'),

    # SSO project call with project ID
    path('project/<str:id>/ssocall/', project_ssocall, name='project_ssocall'),

    # Edit user profile
    path('edit-profile/', edit_profile, name='edit_profile'),

    # Documentation page
    path('docs/', documentation, name='docs'),

    # API for retrieving user data via SSO session
    path('project/getuserdata', return_user_data, name='return_user_data'),
]
