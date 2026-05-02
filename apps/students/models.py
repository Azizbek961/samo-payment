from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class ClassGrade(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g., "1-A"
    default_fee_plan = models.ForeignKey('FeePlan', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class FeePlan(models.Model):
    name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.name} ({self.amount} UZS)"

class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    class_grade = models.ForeignKey(ClassGrade, on_delete=models.PROTECT, related_name='students')
    enrollment_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    override_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text="Custom monthly fee for this student (if any)")

    class Meta:
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return self.full_name

    @property
    def monthly_fee(self):
        if self.override_fee is not None:
            return self.override_fee
        if self.class_grade.default_fee_plan:
            return self.class_grade.default_fee_plan.amount
        return Decimal('0')



class Debt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='debts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)  # ixtiyoriy
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.full_name} - {self.amount} UZS"