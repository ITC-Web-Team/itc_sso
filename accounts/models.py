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
    DEPARTMENT_CHOICES = [
        ('AE', 'Aerospace Engineering'),
        ('BB', 'Biosciences and Bioengineering'),
        ('CE', 'Chemical Engineering'),
        ('CH', 'Chemistry'),
        ('CE', 'Civil Engineering'),
        ('CSE', 'Computer Science & Engineering'),
        ('ES', 'Earth Sciences'),
        ('EE', 'Electrical Engineering'),
        ('ESE', 'Energy Science and Engineering'),
        ('ESED', 'Environmental Science and Engineering'),
        ('HSS', 'Humanities & Social Science'),
        ('IEOR', 'Industrial Engineering & Operations Research'),
        ('MA', 'Mathematics'),
        ('ME', 'Mechanical Engineering'),
        ('ME', 'Metallurgical Engineering & Materials Science'),
        ('PH', 'Physics'),
        ('IDC', 'Industrial Design Centre'),
        ('SOM', 'Shailesh J. Mehta School of Management'),
        ('Other', 'Other')
    ]

    DEGREE_CHOICES = [
        ('B.Tech', 'B.Tech'),
        ('M.Tech', 'M.Tech'),
        ('PhD', 'PhD'),
        ('MS', 'MS'),
        ('MBA', 'MBA'),
        ('M.Des', 'M.Des'),
        ('M.Sc', 'M.Sc'),
        ('MA', 'MA'),
        ('B.Des', 'B.Des'),
        ('B.Sc', 'B.Sc'),
        ('BA', 'BA'),
        ('Other', 'Other')

    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, default='password')
    department = models.CharField(choices=DEPARTMENT_CHOICES, max_length=100, default='CE')
    passing_year = models.PositiveIntegerField()
    email_verified = models.BooleanField(default=False)
    degree = models.CharField( choices=DEGREE_CHOICES, max_length=100 ,default='B.Tech')
    verification_token = models.CharField(max_length=100, blank=True)
    reset_token = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Return the roll number as a string representation."""
        return self.roll


class Project(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device = models.CharField(max_length=255)  
    session_key = models.CharField(max_length=40, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_session_valid(self):
        if timezone.now() <= self.created_at + timedelta(hours=1):
            self.created_at = timezone.now()
        else:
            self.active = False
        return self.active
    
class LoginSession(models.Model):
    """
    This model tracks login sessions for users for specific Project.

    Fields:
    - id: A unique UUID for each login session.
    - user: A One-to-One relationship linking to the User model.
    - project: A One-to-One relationship linking to a specific project.
    - created_at: The timestamp when the session was created.

    Methods:
    - is_session_valid: Checks if the session is valid based on the time limit (1 hour).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sessionkey = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_session_valid(self):
        """
        Check if the session is still valid (valid for 1 hour after creation).
        Returns True if the current time is within 1 hour of session creation, otherwise False.
        """
        return timezone.now() <= self.created_at + timedelta(hours=1)
