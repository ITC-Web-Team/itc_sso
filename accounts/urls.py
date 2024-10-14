# urls.py (in accounts app)
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    # path('registration-success/', views.registration_success, name='registration_success'),
]

