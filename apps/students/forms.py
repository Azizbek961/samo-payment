from django import forms
from .models import Debt

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['student', 'amount', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }