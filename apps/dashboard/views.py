from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.formats import date_format
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta   # install python-dateutil if needed
from decimal import Decimal

from apps.students.models import Student, ClassGrade
from apps.payments.models import Payment
from apps.payments.services.debt import calculate_total_debt, get_top_debtors

@login_required
def dashboard(request):
    today = timezone.now().date()
    current_month_start = today.replace(day=1)

    # Allowed range: 12 months before today – 12 months after today
    min_allowed_month = current_month_start + relativedelta(months=-12)
    max_allowed_month = current_month_start + relativedelta(months=12)

    # Get selected month from GET, default to current month
    selected_month_str = request.GET.get('month')
    if selected_month_str:
        try:
            year, month = map(int, selected_month_str.split('-'))
            selected_month = date(year, month, 1)
            # Clamp to allowed range
            if selected_month < min_allowed_month:
                selected_month = min_allowed_month
            elif selected_month > max_allowed_month:
                selected_month = max_allowed_month
        except (ValueError, TypeError):
            selected_month = current_month_start
    else:
        selected_month = current_month_start

    # Previous and next months (as date objects)
    prev_month = selected_month + relativedelta(months=-1)
    next_month = selected_month + relativedelta(months=1)

    # Disable buttons when out of allowed range
    prev_month_disabled = prev_month < min_allowed_month
    next_month_disabled = next_month > max_allowed_month

    current_month_name = date_format(selected_month, format='F Y')

    # --- KPI calculations (unchanged) ---
    total_collected_today = Payment.objects.filter(timestamp__date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    total_collected_month = Payment.objects.filter(month_year=selected_month).aggregate(Sum('amount'))['amount__sum'] or 0
    paid_students_this_month = Payment.objects.filter(month_year=selected_month).values_list('student', flat=True).distinct()
    unpaid_students_count = Student.objects.filter(status='active').exclude(id__in=paid_students_this_month).count()
    total_debt = calculate_total_debt()

    recent_payments = Payment.objects.select_related('student').order_by('-timestamp')[:10]
    top_debtors = get_top_debtors(limit=5)
    unpaid_this_month = Student.objects.filter(status='active').exclude(id__in=paid_students_this_month)[:10]

    # --- Monthly revenue chart (last 12 months) – unchanged ---
    last_12_months = []
    monthly_data = []
    for i in range(11, -1, -1):
        month = current_month_start + relativedelta(months=-i)
        month_end = month + relativedelta(months=1) - timedelta(days=1)
        total = Payment.objects.filter(
            timestamp__date__gte=month,
            timestamp__date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        last_12_months.append(month.strftime('%b %Y'))
        monthly_data.append(float(total))

    # --- Class chart for selected month – unchanged ---
    class_labels = []
    class_data = []
    for cls in ClassGrade.objects.all():
        total = Payment.objects.filter(
            student__class_grade=cls,
            month_year=selected_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        if total > 0:
            class_labels.append(cls.name)
            class_data.append(float(total))

    # --- Months dropdown: 12 months before today to 12 months after today ---
    months_list = []
    for offset in range(-12, 13):   # inclusive
        m = current_month_start + relativedelta(months=offset)
        months_list.append({
            'value': m.strftime('%Y-%m'),
            'label': m.strftime('%B %Y')
        })
    # Sort descending (latest first)
    months_list.sort(key=lambda x: x['value'], reverse=True)

    context = {
        'total_collected_today': total_collected_today,
        'total_collected_month': total_collected_month,
        'current_month_name': current_month_name,
        'unpaid_students_count': unpaid_students_count,
        'total_debt': total_debt,
        'recent_payments': recent_payments,
        'top_debtors': top_debtors,
        'unpaid_this_month': unpaid_this_month,
        'monthly_labels': last_12_months,
        'monthly_data': monthly_data,
        'class_labels': class_labels,
        'class_data': class_data,
        'months_list': months_list,
        'selected_month': selected_month.strftime('%Y-%m'),
        'prev_month': prev_month.strftime('%Y-%m'),
        'next_month': next_month.strftime('%Y-%m'),
        'prev_month_disabled': prev_month_disabled,
        'next_month_disabled': next_month_disabled,
    }
    return render(request, 'dashboard/dashboard.html', context)