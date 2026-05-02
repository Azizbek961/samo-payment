from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.students.models import Student

User = get_user_model()

class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Transfer'),
    ]
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='payments')
    month_year = models.DateField(help_text="First day of the month payment covers, e.g. 2024-01-01")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=20, unique=True, blank=True)
    is_adjustment = models.BooleanField(default=False, help_text="Allow duplicate month if needed")

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['student', 'month_year'])]

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def generate_receipt_number(self):
        from django.utils.timezone import now
        date_str = now().strftime('%Y%m%d')
        # Get last receipt number today to increment
        last = Payment.objects.filter(receipt_number__startswith=f'RCPT-{date_str}').order_by('receipt_number').last()
        if last:
            last_num = int(last.receipt_number[-4:])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'RCPT-{date_str}-{new_num:04d}'

    def __str__(self):
        return f"{self.receipt_number} - {self.student} - {self.amount}"