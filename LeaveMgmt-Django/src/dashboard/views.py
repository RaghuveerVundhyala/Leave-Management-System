from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from employee.forms import EmployeeCreateForm
from leave.models import Leave
from employee.models import *
from leave.forms import LeaveCreationForm
from django.core.mail import send_mail
from datetime import datetime
from copy import copy

status = 0
date = 0
pastLeaveObj = None
pastStatus = None


# Function to compare dates
def compare_dates(date1, date2):
    """
        Compare two dates.

        Args:
        date1 (datetime): First date.
        date2 (datetime): Second date.

        Returns:
        bool: True if date1 is later than date2, False otherwise.
        """
    flag = False
    if date1.date() > date2.date():
        flag = True
    elif date1.date() == date2.date():
        if date1.time() > date2.time():
            flag = True
        else:
            flag = False

    return flag


# Dashboard view function
def dashboard(request):
    global status
    global date
    global pastLeaveObj
    global pastStatus
    dataset = dict()
    user = request.user
    # Redirect to login page if user is not authenticated
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    employees = Employee.objects.all()
    if request.user.username == "Raghuveer":
        employees = Employee.objects.filter(department_id=3)
        pass
    if request.user.username == "Akhil":
        employees = Employee.objects.filter(department_id=4)
        pass
    if request.user.username == "Vasu":
        employees = Employee.objects.filter(department_id=2)
        pass
    leaves = Leave.objects.all_pending_leaves()
    staff_leaves = Leave.objects.filter(user=user)

    dateupdated = datetime(2000, 1, 1, 0, 0, 0)
    currLeaveObj = None
    for leave in staff_leaves:
        if compare_dates(leave.updated, dateupdated):
            dateupdated = leave.updated
            currLeaveObj = leave

    try:
        e = Employee.objects.get(user=user)
        exp = False
        try:
            if currLeaveObj == pastLeaveObj and currLeaveObj.status != pastLeaveObj.status:
                exp = True
        except:
            pass

        if currLeaveObj != pastLeaveObj or exp:
            pastLeaveObj = copy(currLeaveObj)
            pastStatus = pastLeaveObj.status
            if currLeaveObj.status == "approved":
                if currLeaveObj.leavetype == 'Unpaid':
                    e.Unpaid = e.Unpaid - currLeaveObj.leave_days
                else:
                    e.Paid = e.Paid - currLeaveObj.leave_days
            elif currLeaveObj.status == "cancelled":
                if currLeaveObj.leavetype == 'Unpaid':
                    e.Unpaid = e.Unpaid + currLeaveObj.leave_days
                else:
                    e.Paid = e.Paid + currLeaveObj.leave_days
            e.save()

        print("dashboard/views", e.Paid, e.Unpaid)
        dataset['remLeavePaid'] = e.Paid
        dataset['remLeaveUnpaid'] = e.Unpaid
    except Employee.DoesNotExist:
        pass
    dataset['employees'] = employees

    dataset['leaves'] = leaves

    dataset['staff_leaves'] = staff_leaves

    dataset['title'] = 'summary'

    return render(request, 'dashboard/dashboard_index.html', dataset)


def dashboard_employees(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect('/')

    dataset = dict()
    departments = Department.objects.all()
    # employees = Employee.objects.all()

    if request.user.username == "Raghuveer":
        employees = Employee.objects.filter(department_id=3)
        pass
    if request.user.username == "Akhil":
        employees = Employee.objects.filter(department_id=4)
        pass
    if request.user.username == "Vasu":
        employees = Employee.objects.filter(department_id=2)
        pass

    # pagination
    query = request.GET.get('search')
    if query:
        employees = employees.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query)
        )

    paginator = Paginator(employees, 10)  # show 10 employee lists per page

    page = request.GET.get('page')
    employees_paginated = paginator.get_page(page)

    return render(request, 'dashboard/employee_app.html', dataset)


def dashboard_employees_create(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect('/')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            user = request.POST.get('user')
            assigned_user = User.objects.get(id=user)

            instance.user = assigned_user
            instance.firstname = request.POST.get('firstname')
            instance.lastname = request.POST.get('lastname')
            instance.othername = request.POST.get('othername')

            role = request.POST.get('role')
            role_instance = Role.objects.get(id=role)
            instance.role = role_instance

            instance.startdate = request.POST.get('startdate')
            instance.employeetype = request.POST.get('employeetype')
            instance.employeeid = request.POST.get('employeeid')

            instance.save()

            return redirect('dashboard:employees')
        else:
            messages.error(request, 'Trying to create duplicate employees with a single user account ',
                           extra_tags='alert alert-warning alert-dismissible show')
            return redirect('dashboard:employeecreate')

    dataset = dict()
    form = EmployeeCreateForm()
    dataset['form'] = form
    dataset['title'] = 'register employee'
    return render(request, 'dashboard/employee_create.html', dataset)


# ---------------------LEAVE-------------------------------------------
def compDays(startDate, endDate):
    date_format = '%Y-%m-%d'

    # Convert date strings to datetime objects
    date1 = datetime.strptime(startDate, date_format)
    date2 = datetime.strptime(endDate, date_format)

    # Compute the difference in days
    delta = date2 - date1

    # Return the absolute value of the difference in days
    return abs(delta.days)


def leave_creation(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.method == 'POST':
        form = LeaveCreationForm(data=request.POST)
        valid = True
        leaveType = form.data
        leaveAppliedDays = compDays(leaveType["startdate"], leaveType["enddate"])
        eObj = Employee.objects.get(user=request.user)
        leaveType = leaveType["leavetype"]
        if leaveType == "Unpaid":
            if eObj.Unpaid < leaveAppliedDays:
                valid = False
        else:
            if eObj.Paid < leaveAppliedDays:
                valid = False

        if form.is_valid():
            if not valid:
                messages.error(request, 'Insufficient Leave Balance, Contact your ADMIN',
                               extra_tags='alert alert-warning alert-dismissible show')
                return redirect('dashboard:createleave')
            instance = form.save(commit=False)
            user = request.user
            instance.user = user
            instance.save()
            e = Employee.objects.get(user=user)
            dep_id = e.department.name
            messages.success(request, 'Leave Request Sent, wait for Admins response',
                             extra_tags='alert alert-success alert-dismissible show')
            subject = 'New Leave Application'
            message = f'''Hello, this to notify that {e.firstname}, applied leaves.
                      Thanks,
                      Team LMS'''
            email_from = settings.EMAIL_HOST_USER

            recipient_list = []  # Initialize with an empty list

            if dep_id == 'Finance':
                recipient_list = ['rvundhyala2022@my.fit.edu']

            elif dep_id == 'Engineering':
                recipient_list = ['vkola2023@my.fit.edu']
            elif dep_id == 'Sales':
                recipient_list = ['bkuppala2022@my.fit.edu']

            print(recipient_list)  # Check if recipient_list is populated correctly
            send_mail(subject, message, email_from, recipient_list)  # Send email

            return redirect('dashboard:createleave')

        messages.error(request, 'Failed to request a leave, please check entry dates',
                       extra_tags='alert alert-warning alert-dismissible show')
        return redirect('dashboard:createleave')

    dataset = dict()
    form = LeaveCreationForm()
    dataset['form'] = form
    dataset['title'] = 'Apply for Leave'
    return render(request, 'dashboard/create_leave.html', dataset)

    dataset = dict()
    form = LeaveCreationForm()
    dataset['form'] = form
    dataset['title'] = 'Apply for Leave'
    return render(request, 'dashboard/create_leave.html', dataset)


def leaves_list(request):
    if not request.user.is_superuser:
        return redirect('/')
    leaves = Leave.objects.all_pending_leaves()
    return render(request, 'dashboard/leaves_recent.html', {'leave_list': leaves, 'title': 'leaves list - pending'})


def leaves_approved_list(request):
    if not request.user.is_superuser:
        return redirect('/')
    leaves = Leave.objects.all_approved_leaves()  # approved leaves -> calling model manager method
    return render(request, 'dashboard/leaves_approved.html', {'leave_list': leaves, 'title': 'approved leave list'})


def leaves_view(request, id):
    if not request.user.is_authenticated:
        return redirect('/')

    leave = get_object_or_404(Leave, id=id)
    print(leave.user)

    employee = Employee.objects.filter(user=leave.user)
    print(employee)

    return render(request, 'dashboard/leave_detail_view.html',
                  {'leave': leave, 'employee': employee, 'name': leave.user.username,
                   'title': '{0}-{1} leave'.format(leave.user.username,
                                                   leave.status)})


def approve_leave(request, id):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')
    leave = get_object_or_404(Leave, id=id)
    user = leave.user
    # employee = Employee.objects.filter(user=user)[0]
    e = Employee.objects.get(user=user)
    leave.approve_leave(e)

    messages.error(request, 'Leave successfully approved for {0}'.format(e.get_full_name),
                   extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:userleaveview', id=id)


def cancel_leaves_list(request):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')
    leaves = Leave.objects.all_cancel_leaves()
    return render(request, 'dashboard/leaves_cancel.html', {'leave_list_cancel': leaves, 'title': 'Cancel leave list'})


def unapprove_leave(request, id):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect('/')
    leave = get_object_or_404(Leave, id=id)
    leave.unapprove_leave
    return redirect('dashboard:leaveslist')  # redirect to unapproved list


def cancel_leave(request, id):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')
    leave = get_object_or_404(Leave, id=id)
    leave.leaves_cancel

    messages.success(request, 'Leave is canceled', extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:canceleaveslist')  # work on redirecting to instance leave - detail view


# Current section -> here
def uncancel_leave(request, id):
    if not (request.user.is_superuser and request.user.is_authenticated):
        return redirect('/')
    leave = get_object_or_404(Leave, id=id)
    leave.status = 'pending'
    leave.is_approved = False
    leave.save()
    messages.success(request, 'Leave is uncanceled,now in pending list',
                     extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:canceleaveslist')  # work on redirecting to instance leave - detail view


def leave_rejected_list(request):
    dataset = dict()
    leave = Leave.objects.all_rejected_leaves()

    dataset['leave_list_rejected'] = leave
    return render(request, 'dashboard/rejected_leaves_list.html', dataset)


def reject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    user = leave.user
    e = Employee.objects.get(user=user)

    # Check if the leave is approved or pending
    if leave.status == 'approved':
        # For approved leave getting rejected, increment leave count
        print("approve")
        if leave.leavetype == 'Unpaid':
            e.Unpaid += leave.leave_days
        else:
            e.Paid += leave.leave_days
    elif leave.status == 'pending':
        print("rej loop",e.Paid)
        pass
    else:
        # For other cases, do nothing
        pass

    leave.reject_leave(e)
    e.save()

    messages.success(request, 'Leave is rejected', extra_tags='alert alert-success alert-dismissible show')
    return redirect('dashboard:leavesrejected')





def unreject_leave(request, id):
    leave = get_object_or_404(Leave, id=id)
    leave.status = 'pending'
    leave.is_approved = False
    leave.save()
    messages.success(request, 'Leave is now in pending list ', extra_tags='alert alert-success alert-dismissible show')

    return redirect('dashboard:leavesrejected')


#  staffs leaves table user only
def view_my_leave_table(request):
    # work on the logics
    if request.user.is_authenticated:
        user = request.user
        leaves = Leave.objects.filter(user=user)
        employee = Employee.objects.filter(user=user).first()
        print(leaves)
        dataset = dict()
        dataset['leave_list'] = leaves
        dataset['employee'] = employee
        dataset['title'] = 'Leaves List'
    else:
        return redirect('accounts:login')
    return render(request, 'dashboard/staff_leaves_table.html', dataset)
