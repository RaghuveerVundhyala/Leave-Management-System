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

# Type of reasons for leave
SICK = 'sick'
CASUAL = 'casual'
EMERGENCY = 'emergency'
Unpaid = 'Unpaid'
Other = 'Other'

LEAVE_TYPE = (
    (SICK, 'Sick Leave'),
    (CASUAL, 'Casual Leave'),
    (EMERGENCY, 'Emergency Leave'),
    (Unpaid, 'Unpaid Leave'),
    (Other, 'Other')
)


# Leave Model
class Leave(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    startdate = models.DateField(verbose_name=_('Start Date'), help_text='leave start date is on ..', null=True,
                                 blank=False)
    enddate = models.DateField(verbose_name=_('End Date'), help_text='comes back on', null=True, blank=False)
    leavetype = models.CharField(choices=LEAVE_TYPE, max_length=25, default=SICK, null=True, blank=False)
    reason = models.CharField(verbose_name=_('Reason for Leave'), max_length=255,
                              help_text='add additional information for leave', null=True, blank=True)

    status = models.CharField(max_length=12, default='pending')  # pending,approved,rejected,cancelled
    is_approved = models.BooleanField(default=False)  # hide

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    objects = LeaveManager()

    Tempdays = 0
    date_of_approved_leave = 0

    class Meta:
        verbose_name = _('Leave')
        verbose_name_plural = _('Leaves')
        ordering = ['-created']  # recent objects

    @property
    def pretty_leave(self):
        leave = self.leavetype
        user = self.user
        employee = user.employee_set.first().get_full_name
        return '{0} - {1}'.format(employee, leave)

    def businessDays(self, startdate, enddate):
        from datetime import timedelta

        # initializing dates ranges
        test_date1, test_date2 = startdate, enddate

        # generating dates
        dates = (test_date1 + timedelta(idx+1) for idx in range((test_date2 - test_date1).days))

        # summing all weekdays removing weekends
        res = sum(1 for day in dates if day.weekday() < 5)

        # holidayList
        holiday_list = [
            (12, 25),  # Christmas
            (7, 4)  # New Year
        ]

        for holiday_month, holiday_day in holiday_list:
            holiday_date = startdate.replace(month=holiday_month, day=holiday_day)
            if startdate <= holiday_date <= enddate:
                res -= 1

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
        # if busineesDay > eObj.
        return busineesDay

    @property
    def leave_approved(self):
        return self.is_approved == True

    # leave approval, deduct leave, send notification
    def approve_leave(self, eObj):
        subject = 'Leave Approved'
        message = f'Hi {eObj.firstname}, your leave got approved.'
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
            self.status = 'cancelled'
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

        if self.is_approved:
            # If the leave is approved, it's being rejected after approval
            # Increase the leave count as it's already been deducted when approved
            if self.leavetype == 'Unpaid':
                eObj.Unpaid += self.leave_days
            else:
                eObj.Paid += self.leave_days
            eObj.save()

            # Update status to 'rejected' regardless of whether the leave was approved or pending
        self.status = 'rejected'
        self.save()
