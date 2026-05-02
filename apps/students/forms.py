from django import forms
from .models import Debt
from django import forms

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['student', 'amount', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

from .models import ClassGrade  # yoki sizdagi model nomi

class ClassGradeForm(forms.ModelForm):
    class Meta:
        model = ClassGrade
        fields = ["name"]  # sizdagi fieldlar