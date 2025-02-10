from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Project
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone

class RegistrationForm(UserCreationForm):
    roll = forms.CharField(max_length=10)
    name = forms.CharField(max_length=100)
    department = forms.ChoiceField(choices=Profile.DEPARTMENT_CHOICES)
    passing_year = forms.IntegerField(min_value=timezone.now().year-2, max_value=timezone.now().year+10)
    degree = forms.ChoiceField(choices=Profile.DEGREE_CHOICES)

    class Meta:
        model = User
        fields = ('name', 'roll', 'department', 'degree', 'passing_year', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add warning message to password field help text
        self.fields['password1'].help_text = (
            '<div class="alert alert-warning" role="alert">'
            '<strong>Warning:</strong> This is not the official IITB SSO. '
            'Using a different password than your LDAP password is recommended.'
            '</div>' + self.fields['password1'].help_text
        )

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
                department=self.cleaned_data["department"],
                passing_year=self.cleaned_data["passing_year"],
                degree=self.cleaned_data["degree"]
            )
        return user
    
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('name', 'department', 'passing_year', 'degree')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Roll Number')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'main_url', 'redirect_url', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }