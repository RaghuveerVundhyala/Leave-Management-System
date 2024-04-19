from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserAddForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Eg. raghu2022@my.fit.edu'}))
    username = forms.CharField(
        label="Username",
        max_length=150,
        help_text=" ",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")
        return username


class UserLogin(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'password'}))
