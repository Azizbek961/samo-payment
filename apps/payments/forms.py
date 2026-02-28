from django import forms
from datetime import date

from .models import Payment


class PaymentForm(forms.ModelForm):
    month_year = forms.DateField(
        widget=forms.DateInput(attrs={"type": "month"}),
        input_formats=["%Y-%m"],  # 2026-02 formatni qabul qiladi
        help_text="First day of the month payment covers, e.g. 2024-01-01",
    )

    class Meta:
        model = Payment
        fields = ["student", "month_year", "amount", "method", "notes", "is_adjustment", ]

    def clean_month_year(self):
        d = self.cleaned_data["month_year"]
        # type=month kelganda d odatda 1-kun qilib parse bo‘ladi,
        # lekin baribir 1-kunga normalize qilib qo‘yamiz:
        return date(d.year, d.month, 1)