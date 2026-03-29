from django import forms
from .models import ConsentRecord, DataBreachReport


# Consent Form
class ConsentForm(forms.ModelForm):
    class Meta:
        model = ConsentRecord
        fields = ['full_name', 'email', 'purpose', 'consent_given']
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 4}),
        }


# Data Breach Report Form
class DataBreachForm(forms.ModelForm):
    class Meta:
        model = DataBreachReport
        fields = ['title', 'description', 'severity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }