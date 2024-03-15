from django import forms
from django.contrib.auth.models import User
from employee.models import Role, Department, Employee


class EmployeeCreateForm(forms.ModelForm):
    employeeid = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Please enter 5 characters without RGL or slashes eg. A0025'}))
    user = forms.ModelChoiceField(queryset=User.objects.filter(employee=None), empty_label=None)

    class Meta:
        model = Employee
        exclude = ['is_blocked', 'is_deleted', 'created', 'updated']
        widgets = {
            'bio': forms.Textarea(attrs={'cols': 5, 'rows': 5}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'startdate': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeCreateForm, self).__init__(*args, **kwargs)
        self.fields['user'].label = 'Select User'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        if Employee.objects.filter(user=user).exists():
            raise forms.ValidationError("A user can only be assigned to one employee.")
        return cleaned_data
