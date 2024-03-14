from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-user/', views.register_user_view, name='register'),
    path('user/change-password/', views.changepassword, name='changepassword'),
    path('users/all', views.users_list, name='users'),


]
