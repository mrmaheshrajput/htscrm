from django import forms
from visits.models import CallVisit

YEARS = ['2020', '2021']

class CallVisitForm(forms.ModelForm):
    visit_date_time         = forms.DateTimeField(widget=forms.SelectDateWidget(
                                                attrs={
                                                    'class': 'form-control col-md-4'
                                                    },
                                                years=YEARS
                                                    )
                                                )
    class Meta:
        model   = CallVisit
        fields  = [
            'serviced_by',
            'visit_status',
            'visit_date_time',
            'outcome',
            'call_status_final',
            'call_visit_final_notes'
        ]
