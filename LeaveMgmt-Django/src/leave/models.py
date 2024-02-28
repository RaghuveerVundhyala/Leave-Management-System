from django.db import models
from .manager import LeaveManager
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.contrib import admin
from employee.models import *

from django.conf import settings
from django.core.mail import send_mail
import certifi

# Create your models here.
SICK = 'sick'
CASUAL = 'casual'
EMERGENCY = 'emergency'
Unpaid = 'Unpaid'

LEAVE_TYPE = (
    (SICK, 'Sick Leave'),
    (CASUAL, 'Casual Leave'),
    (EMERGENCY, 'Emergency Leave'),
    (Unpaid, 'Unpaid Leave'),
)

LeavePerYear = 20


class Leave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    startdate = models.DateField(verbose_name=_('Start Date'), help_text='leave start date is on ..', null=True,
                                 blank=False)
    enddate = models.DateField(verbose_name=_('End Date'), help_text='coming back on ...', null=True, blank=False)
    leavetype = models.CharField(choices=LEAVE_TYPE, max_length=25, default=SICK, null=True, blank=False)
    reason = models.CharField(verbose_name=_('Reason for Leave'), max_length=255,
                              help_text='add additional information for leave', null=True, blank=True)
    defaultdays = models.PositiveIntegerField(verbose_name=_('Leave days per year counter'), default=LeavePerYear,
                                              null=True,
                                              blank=True)

    status = models.CharField(max_length=12, default='pending')  # pending,approved,rejected,cancelled
    is_approved = models.BooleanField(default=False)  # hide

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    # Unpaid = models.PositiveIntegerField(verbose_name=_('unPaidLeave'), default=5,
    #                                      null=True,
    #                                      blank=True)
    # Paid = models.PositiveIntegerField(verbose_name=_('PaidLeave'), default=15,
    #                                    null=True,
    #                                    blank=True)

    objects = LeaveManager()

    Tempdays = 0
    date_of_approved_leave = 0

    class Meta:
        verbose_name = _('Leave')
        verbose_name_plural = _('Leaves')
        ordering = ['-created']  # recent objects

    # def __str__(self):
    # 	return ('{0} - {1}'.format(self.leavetype,self.user))

    @property
    def pretty_leave(self):
        '''
		i don't like the __str__ of leave object - this is a pretty one :-)
		'''
        leave = self.leavetype
        user = self.user
        employee = user.employee_set.first().get_full_name
        return '{0} - {1}'.format(employee, leave)

    def businessDays(self, startdate, enddate):
        from datetime import datetime, timedelta

        # initializing dates ranges
        test_date1, test_date2 = startdate, enddate

        # generating dates
        dates = (test_date1 + timedelta(idx + 1)
                 for idx in range((test_date2 - test_date1).days))

        # summing all weekdays
        res = sum(1 for day in dates if day.weekday() < 5)

        # holidayList = [datetime(2015, 6, 3)]
        if startdate.month == 12:  # dec month
            if startdate.day <= 25 or enddate.day >= 25:  # christmas
                res = res - 1

        if startdate.month == 1:  # Jan month
            if startdate.day <= 1 or enddate.day >= 1:  # new year
                res = res - 1

        return res

    @property
    def leave_days(self):
        days_count = ''
        startdate = self.startdate
        enddate = self.enddate
        if startdate > enddate:
            return
        dates = (enddate - startdate)

        Leave.Tempdays = dates.days
        print("leaves applied", Leave.Tempdays)
        # return [dates.days, self.paidLeave, self.unPaidLeave]

        busineesDay = self.businessDays(startdate, enddate)
        print("busineesDay : ", busineesDay)
        Leave.Tempdays = busineesDay
        Leave.date_of_approved_leave = self.created
        return busineesDay

    @property
    def leave_approved(self):
        return self.is_approved == True

    def approve_leave(self, eObj):
        subject = 'Leave Approved'
        message = f'Hi {eObj.firstname}, Your leave got approved.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [eObj.email]
        send_mail(subject, message, email_from, recipient_list)

        Leave.date_of_approved_leave = self.created
        print(Leave.date_of_approved_leave)
        if not self.is_approved:
            self.is_approved = True
            self.status = 'approved'
            self.save()

    @property
    def unapprove_leave(self):
        if self.is_approved:
            self.is_approved = False
            self.status = 'pending'
            self.save()

    @property
    def leaves_cancel(self):
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.status = 'cancelled'
            self.save()

    def reject_leave(self, eObj):
        subject = 'Leave Rejected'
        message = f'Hi {eObj.firstname}, Your leave got rejected.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [eObj.email]
        send_mail(subject, message, email_from, recipient_list)
        if self.is_approved or not self.is_approved:
            self.is_approved = False
            self.status = 'rejected'
            self.save()

    @property
    def is_rejected(self):
        Leave.Tempdays = -Leave.Tempdays
        print("Leave Tempdays", Leave.Tempdays)
        return self.status == 'rejected'
