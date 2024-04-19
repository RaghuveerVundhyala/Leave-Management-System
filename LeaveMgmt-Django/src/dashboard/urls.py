from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('welcome/', views.dashboard, name='dashboard'),

    # endpoint paths for viewing, applying, approving, cancelling leaves
    path('employees/all/', views.dashboard_employees, name='employees'),
    path('employee/create/', views.dashboard_employees_create, name='employeecreate'),
    path('leave/apply/', views.leave_creation, name='createleave'),
    path('leaves/pending/all/', views.leaves_list, name='leaveslist'),
    path('leaves/approved/all/', views.leaves_approved_list, name='approvedleaveslist'),
    path('leaves/cancel/all/', views.cancel_leaves_list, name='canceleaveslist'),
    path('leaves/all/view/<int:id>/', views.leaves_view, name='userleaveview'),
    path('leaves/view/table/', views.view_my_leave_table, name='staffleavetable'),
    path('leave/approve/<int:id>/', views.approve_leave, name='userleaveapprove'),
    path('leave/unapprove/<int:id>/', views.unapprove_leave, name='userleaveunapprove'),
    path('leave/cancel/<int:id>/', views.cancel_leave, name='userleavecancel'),
    path('leave/uncancel/<int:id>/', views.uncancel_leave, name='userleaveuncancel'),
    path('leaves/rejected/all/', views.leave_rejected_list, name='leavesrejected'),
    path('leave/reject/<int:id>/', views.reject_leave, name='reject'),
    path('leave/unreject/<int:id>/', views.unreject_leave, name='unreject'),
    path('check_email/', views.check_email, name='check_email'),


]
