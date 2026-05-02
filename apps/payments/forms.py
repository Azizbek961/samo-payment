from django import forms
from datetime import date
from django_select2.forms import ModelSelect2Widget

from .models import Payment
from apps.students.models import Student


class StudentWidget(ModelSelect2Widget):
    model = Student

    # Change these fields to match your Student model
    search_fields = [
        "full_name__icontains",

    ]

    def label_from_instance(self, obj):
        return f"{obj.full_name} — {obj.phone}"


class PaymentForm(forms.ModelForm):
    month_year = forms.DateField(
        widget=forms.DateInput(attrs={"type": "month"}),
        input_formats=["%Y-%m"],
        help_text="First day of the month payment covers, e.g. 2024-01-01",
    )

    class Meta:
        model = Payment
        fields = ["student", "month_year", "amount", "method", "notes", "is_adjustment"]
        widgets = {
            "student": StudentWidget(
                attrs={
                    "data-placeholder": "O'quvchini qidirish",
                    "data-minimum-input-length": 2,
                }
            )
        }

    def clean_month_year(self):
        d = self.cleaned_data["month_year"]
        return date(d.year, d.month, 1)