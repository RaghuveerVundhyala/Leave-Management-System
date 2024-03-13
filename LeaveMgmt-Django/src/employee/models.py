import datetime
from employee.utility import code_format
from django.db import models
from employee.managers import EmployeeManager
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=125)
    description = models.CharField(max_length=125, null=True, blank=True)

    created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('Updated'), auto_now=True)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name', 'created']

    # object is converted to a string
    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=125)
    description = models.CharField(max_length=125, null=True, blank=True)

    created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('Updated'), auto_now=True)

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['name', 'created']

    # object is converted to a string
    def __str__(self):
        return self.name


class Employee(models.Model):
    FULL_TIME = 'Full-Time'
    PART_TIME = 'Part-Time'
    CONTRACT = 'Contract'
    INTERN = 'Intern'

    EMPLOYEETYPE = (
        (FULL_TIME, 'Full-Time'),
        (PART_TIME, 'Part-Time'),
        (CONTRACT, 'Contract'),
        (INTERN, 'Intern'),
    )

    # PERSONAL DATA
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    firstname = models.CharField(_('Firstname'), max_length=125, null=False, blank=False)
    lastname = models.CharField(_('Lastname'), max_length=125, null=False, blank=False)
    othername = models.CharField(_('Othername (optional)'), max_length=125, null=True, blank=True)
    birthday = models.DateField(_('Birthday'), blank=False, null=False)
    department = models.ForeignKey(Department, verbose_name=_('Department'), on_delete=models.SET_NULL, null=True,
                                   default=None)
    role = models.ForeignKey(Role, verbose_name=_('Role'), on_delete=models.SET_NULL, null=True, default=None)
    startdate = models.DateField(_('Employment Date'), help_text='date of employment', blank=False, null=True)
    employeetype = models.CharField(_('Employee Type'), max_length=15, default=FULL_TIME, choices=EMPLOYEETYPE,
                                    blank=False, null=True)
    employeeid = models.CharField(_('Employee ID Number'), max_length=10, null=True, blank=True)
    Unpaid = models.PositiveIntegerField(verbose_name=_('Unpaid Leave'), default=5,
                                         null=True,
                                         blank=True)
    Paid = models.PositiveIntegerField(verbose_name=_('Paid Leave'), default=15,
                                       null=True,
                                       blank=True)

    email = models.CharField(_('Email'), max_length=50, null=False, blank=False)
    is_deleted = models.BooleanField(_('Is Deleted'), help_text='button to toggle employee deleted and undelete',
                                     default=False)

    created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True, null=True)
    updated = models.DateTimeField(verbose_name=_('Updated'), auto_now=True, null=True)

    objects = EmployeeManager()

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['-created']

    def __str__(self):
        return self.get_full_name

    @property
    def get_full_name(self):
        fullname = ''
        firstname = self.firstname
        lastname = self.lastname
        othername = self.othername

        if (firstname and lastname) or othername is None:
            fullname = firstname + ' ' + lastname
            return fullname
        elif othername:
            fullname = firstname + ' ' + lastname + ' ' + othername
            return fullname
        return

    def save(self, *args, **kwargs):
        get_id = self.employeeid  # grab employee_id number from submitted form field
        data = code_format(get_id)
        self.employeeid = data  # pass the new code to the employee_id as its orifinal or actual code
        super().save(*args, **kwargs)  # call the parent save method
        print(self.employeeid)
