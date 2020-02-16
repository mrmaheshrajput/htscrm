from django import forms
from engineers.models import Engineer

class EngineerAddForm(forms.ModelForm):
    class Meta:
        model       = Engineer
        fields      = [
            'engineer_name',
            'mobile'
        ]
