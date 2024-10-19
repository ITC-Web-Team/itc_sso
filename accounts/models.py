from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    passing_year = models.PositiveIntegerField()
    course = models.CharField(max_length=100)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.roll
    

class Projects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    redirect_url = models.URLField()

    def __str__(self):
        return self.name

class LoginSession(models.Model):
    id = models.UUIDField(primary_key=True , default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.OneToOneField(Projects, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

