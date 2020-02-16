from django import forms
from customers.models import ClientDetails

class ClientForm(forms.ModelForm):
    class Meta:
        model       = ClientDetails
        fields      = [
            'name',
            'calling_number',
            'contact_number',
            'address',
            'city',
            'state',
            'pin'
        ]
