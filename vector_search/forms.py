from django import forms
from .models import Summary

class SummaryForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ["text", "category"]
