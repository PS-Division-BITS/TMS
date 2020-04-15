from django import forms
from tempus_dominus.widgets import DateTimePicker
from .models import PS2TSTransfer, TS2PSTransfer, UserProfile, DeadlineModel

class PS2TSTransferForm(forms.ModelForm):
    contact = forms.CharField(max_length=20, label="Phone Number", required=True)
    class Meta:  
        model = PS2TSTransfer  
        fields = ['contact', 'applicant', 'supervisor_email', 'hod_email', 'sub_type', 'cgpa', 'thesis_locale', 'thesis_subject', 'name_of_org', 'expected_deliverables']
        labels = {
            "supervisor_email": "Supervisor(on campus)/co-supervisor(off campus) Email",
            "thesis_locale": "Thesis type",
            "hod_email": "HOD Email",
            "cgpa": "CGPA",
            "name_of_org": "Name of Institute/Organization"
        }


class TS2PSTransferForm(forms.ModelForm):
    contact = forms.CharField(max_length=20, label="Phone Number", required=True)
    class Meta:  
        model = TS2PSTransfer  
        fields = ['contact', 'applicant', 'hod_email', 'sub_type', 'cgpa', 'reason_for_transfer', 'name_of_org']
        labels = {
            "hod_email": "HOD Email",
            "cgpa": "CGPA",
            "name_of_org": "Name of Institute/Organization"
        }

class PSDForm(forms.ModelForm):
    deadline_PS2TS = forms.DateTimeField(
        widget=DateTimePicker(
            attrs={
                'append': 'fa fa-calendar'
            }
        ),
        label="PS2TS Deadline Date and Time"
    )
    deadline_TS2PS = forms.DateTimeField(
        widget=DateTimePicker(
            attrs={
                'append': 'fa fa-calendar'
            }
        ),
        label="TS2PS Deadline Date and Time"
    )
    class Meta:
        model = DeadlineModel
        fields = ['is_active_PS2TS', 'deadline_PS2TS', 'is_active_TS2PS', 'deadline_TS2PS', 'message']
        labels = {
            'is_active_PS2TS' : 'Enable PS2TS Form',
            'is_active_TS2PS' : 'Enable TS2PS Form',
            'message': 'Message to be Displayed'
        }
