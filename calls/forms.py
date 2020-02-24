from django import forms
from calls.models import CallRegister

YEARS = ['2020', '2021']

# class DateInput(forms.DateInput):
#     input_type = 'date'

class CallRegisterForm(forms.ModelForm):
    appointment_date         = forms.DateField(widget=forms.SelectDateWidget(
                                                attrs={
                                                    'class': 'form-control col-md-4'
                                                    },
                                                years=YEARS
                                                    )
                                                )
    # appointment_time         = forms.DateTimeField(widget=forms.SplitDateTimeWidget(
    #                                             # attrs={
    #                                             #     'class': 'form-control col-md-4'
    #                                             #     }
    #                                                 )
    #                                             )

    class Meta:
        model   = CallRegister
        fields  = [
            'complaint_nature',
            'brand',
            'product_name',
            'product_serial',
            'product_coverage',
            'appointment_date',
            'appointment_time'
        ]
        # widgets = {
        #     'appointment_date': DateInput(attrs={'class': 'form-control'})
        # }
