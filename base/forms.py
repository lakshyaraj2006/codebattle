from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User

from .models import Submission

class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ['details']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'password1', 'password2']
