from datetime import date, timedelta

from django.db.models import Sum

from apps.payments.models import Payment
from apps.students.models import Student

DEBT_START_MONTH = date(2026, 3, 1)


def _get_debt_months(end_month):
    months = []
    current = DEBT_START_MONTH
    while current <= end_month:
        months.append(current)
        current += timedelta(days=32)
        current = current.replace(day=1)
    return months


def calculate_total_debt():
    students = Student.objects.filter(status='active')
    current_month = date.today().replace(day=1)

    payments = Payment.objects.filter(
        student__in=students,
        month_year__gte=DEBT_START_MONTH,
        month_year__lte=current_month,
    ).values('student_id', 'month_year').annotate(total=Sum('amount'))

    paid_dict = {}
    for payment in payments:
        student_id = payment['student_id']
        month = payment['month_year']
        paid_dict.setdefault(student_id, {})[month] = payment['total']

    total_debt = 0
    for student in students:
        monthly_fee = student.monthly_fee
        for month in _get_debt_months(current_month):
            paid = paid_dict.get(student.id, {}).get(month, 0)
            if paid < monthly_fee:
                total_debt += monthly_fee - paid

    return total_debt


def get_top_debtors(limit=5):
    students = Student.objects.filter(status='active').select_related('class_grade')
    current_month = date.today().replace(day=1)

    payments = Payment.objects.filter(
        student__in=students,
        month_year__gte=DEBT_START_MONTH,
        month_year__lte=current_month,
    ).values('student_id', 'month_year').annotate(total=Sum('amount'))

    paid_dict = {}
    for payment in payments:
        student_id = payment['student_id']
        month = payment['month_year']
        paid_dict.setdefault(student_id, {})[month] = payment['total']

    debtors = []
    for student in students:
        total_debt = 0
        monthly_fee = student.monthly_fee
        for month in _get_debt_months(current_month):
            paid = paid_dict.get(student.id, {}).get(month, 0)
            if paid < monthly_fee:
                total_debt += monthly_fee - paid
        if total_debt > 0:
            debtors.append({
                'student': student,
                'total_debt': total_debt,
            })

    debtors.sort(key=lambda item: item['total_debt'], reverse=True)
    return debtors[:limit]
