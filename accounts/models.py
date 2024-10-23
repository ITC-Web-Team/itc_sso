from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    """
    This model extends the built-in User model with additional fields such as:
    - roll: The student's unique roll number.
    - name: The full name of the user.
    - branch: The academic branch or department.
    - passing_year: The year the student graduated.
    - course: The academic course the student pursued.
    - email_verified: A flag indicating whether the user's email has been verified.
    - verification_token: A token used for email verification.
    - reset_token: A token used for password reset.

    Relationships:
    - user: One-to-One relationship with the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, default='password')
    branch = models.CharField(max_length=100)
    passing_year = models.PositiveIntegerField()
    course = models.CharField(max_length=100)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    reset_token = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Return the roll number as a string representation."""
        return self.roll


class Projects(models.Model):
    """
    This model represents a project that users can log in to using SSO.
    
    Fields:
    - id: A unique UUID for each project.
    - name: The name of the project.
    - redirect_url: The URL where users are redirected after logging in.
    - description: A short description of the project.
    - logo: An image representing the project (e.g., a logo).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    main_url = models.URLField(blank=True, null=True)
    redirect_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='project_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

    
class SSOSession(models.Model):
    """
    This model tracks Single Sign-On (SSO) sessions for users.

    Fields:
    - id: A unique UUID for each SSO session.
    - user: A ForeignKey linking the session to a specific user.
    - device: The user's device (or browser) information from the user-agent string.
    - session_key: The session key used to authenticate the user.
    - active: A boolean flag indicating if the session is currently active.
    - created_at: The timestamp when the session was created.

    Methods:
    - is_session_valid: Determines if the session is still valid based on when it was created.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.CharField(max_length=255)  
    session_key = models.CharField(max_length=40, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_session_valid(self):
        return self.created_at

    def is_session_valid(self):
        """
        Returns the session's creation time. 
        Additional validation logic can be added to check if the session is valid 
        based on expiration time.
        """
        return self.created_at

class LoginSession(models.Model):
    """
    This model tracks login sessions for users for specific projects.

    Fields:
    - id: A unique UUID for each login session.
    - user: A One-to-One relationship linking to the User model.
    - project: A One-to-One relationship linking to a specific project.
    - created_at: The timestamp when the session was created.

    Methods:
    - is_session_valid: Checks if the session is valid based on the time limit (1 hour).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sessionkey = models.CharField(max_length=100, null=True)
    project = models.OneToOneField(Projects, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_session_valid(self):
        """
        Check if the session is still valid (valid for 1 hour after creation).
        Returns True if the current time is within 1 hour of session creation, otherwise False.
        """
        return timezone.now() <= self.created_at + timedelta(hours=1)
