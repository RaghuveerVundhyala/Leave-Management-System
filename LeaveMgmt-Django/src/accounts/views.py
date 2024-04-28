from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from employee.models import *  # Importing models from employee app
from .forms import UserLogin, UserAddForm  # Importing forms from current directory


# Function to handle password change request
def changepassword(request):
    # Redirect to home if user is not authenticated
    if not request.user.is_authenticated:
        return redirect('/')

    # Handling POST request for password change
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            update_session_auth_hash(request, user)

            # Display success message and redirect to password change page
            messages.success(request, 'Password changed successfully',
                             extra_tags='alert alert-success alert-dismissible show')
            return redirect('accounts:changepassword')
        else:
            # Display error message and redirect to password change page
            messages.error(request, 'Error changing password', extra_tags='alert alert-warning alert-dismissible show')
            return redirect('accounts:changepassword')

    # Display password change form
    form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password_form.html', {'form': form})


# Function to handle user registration
def register_user_view(request):
    # Handling POST request for user registration
    if request.method == 'POST':
        form = UserAddForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            username = form.cleaned_data.get("username")

            # Display success message and redirect to registration page
            messages.success(request, 'Account created for {0} !!!'.format(username),
                             extra_tags='alert alert-success alert-dismissible show')
            return redirect('accounts:register')
        else:
            # Display error message and redirect to registration page
            messages.error(request, 'Username Already Taken(Please try again)',
                           extra_tags='alert alert-warning alert-dismissible show')
            return redirect('accounts:register')

    # Display user registration form
    form = UserAddForm()
    dataset = dict()
    dataset['form'] = form
    dataset['title'] = 'Register Users'
    return render(request, 'accounts/register.html', dataset)


# Function to handle user login
def login_view(request):
    if request.method == 'POST':
        form = UserLogin(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticating user
            user = authenticate(request, username=username, password=password)
            if user and user.is_active:
                login(request, user)

                return redirect('dashboard:dashboard')
            else:
                # Display error message and redirect to login page
                messages.error(request, 'Account is invalid', extra_tags='alert alert-error alert-dismissible show')
                return redirect('accounts:login')

        else:
            messages.error(request, 'Invalid form data', extra_tags='alert alert-error alert-dismissible show')
            return redirect('accounts:login')

    else:
        form = UserLogin()

    dataset = {'form': form}
    return render(request, 'accounts/login.html', dataset)


# Function to handle user logout
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# Function to display list of users
def users_list(request):
    if request.user.username == "Raghuveer":
        employees = Employee.objects.filter(department_id=3)
        pass
    if request.user.username == "Akhil":
        employees = Employee.objects.filter(department_id=4)
        pass
    if request.user.username == "Vasu":
        employees = Employee.objects.filter(department_id=2)
        pass
    # employees = Employee.objects.all()
    return render(request, 'accounts/users_table.html', {'employees': employees, 'title': 'Employee List'})


def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'exists': User.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

