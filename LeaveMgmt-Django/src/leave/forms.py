from django import forms
from .models import Leave
import datetime


# form for leave application
class LeaveCreationForm(forms.ModelForm):
    reason = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    class Meta:
        model = Leave
        exclude = ['user', 'defaultdays', 'hrcomments', 'status', 'is_approved', 'updated', 'created']
        widgets = {
            'startdate': forms.DateInput(attrs={'type': 'date'}),
            'enddate': forms.DateInput(attrs={'type': 'date'})
        }

    # validation for the selection of dates
    def clean_enddate(self):
        enddate = self.cleaned_data['enddate']
        startdate = self.cleaned_data['startdate']
        today_date = datetime.date.today()
        if (startdate or enddate) < today_date:  # both dates must not be in the past
            raise forms.ValidationError("Selected dates are incorrect,please select again")

        elif startdate >= enddate:  # TRUE -> FUTURE DATE > PAST DATE,FALSE otherwise
            raise forms.ValidationError("Selected dates are wrong")

        return enddate
