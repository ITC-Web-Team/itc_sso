from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(UserCreationForm):
    roll = forms.CharField(max_length=10)
    name = forms.CharField(max_length=100)
    branch = forms.CharField(max_length=100)
    passing_year = forms.IntegerField()
    course = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ('name', 'roll', 'password1', 'password2', 'branch', 'passing_year', 'course')

    def clean_roll(self):
        roll = self.cleaned_data.get('roll')
        if User.objects.filter(username=roll).exists():
            raise forms.ValidationError("A user with that roll number already exists.")
        return roll

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["roll"]
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                roll=self.cleaned_data["roll"],
                name=self.cleaned_data["name"],
                branch=self.cleaned_data["branch"],
                passing_year=self.cleaned_data["passing_year"],
                course=self.cleaned_data["course"]
            )
        return user
    
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('name', 'branch', 'passing_year', 'course')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Roll Number')