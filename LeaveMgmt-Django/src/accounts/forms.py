from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# Form for adding a new user, extends UserCreationForm
class UserAddForm(UserCreationForm):
    # Field for email with placeholder text
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Eg. raghu2022@my.fit.edu'}))

    class Meta:
        model = User
        # Define fields to include in the form
        fields = ['username', 'email', 'password1', 'password2']


# Form for user login
class UserLogin(forms.Form):
    # Field for username with placeholder text
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}))
    # Field for password with placeholder text
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
