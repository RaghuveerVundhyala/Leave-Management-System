# Import necessary modules
from django.urls import path
from . import views  # Import views from the current directory

# Define the app namespace
app_name = 'accounts'

# Define URL patterns for the accounts app
urlpatterns = [

    # URL pattern for user login
    path('login/', views.login_view, name='login'),

    # URL pattern for user logout
    path('logout/', views.logout_view, name='logout'),

    # URL pattern for user registration
    path('create-user/', views.register_user_view, name='register'),

    # URL pattern for changing user password
    path('user/change-password/', views.changepassword, name='changepassword'),

    # URL patterns for listing all users
    path('users/all', views.users_list, name='users'),
]
