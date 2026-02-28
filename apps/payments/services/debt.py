from datetime import date, timedelta
from django.db.models import Sum, Q
from apps.students.models import Student
from apps.payments.models import Payment

def calculate_total_debt():
    """
    Barcha aktiv o‘quvchilarning umumiy qarzini hisoblaydi.
    Soddalashtirilgan: har bir o‘quvchi uchun to‘lanmagan oylar soni * oylik to‘lov.
    To‘liq hisoblash uchun murakkabroq mantiq kerak (qisman to‘lovlarni hisobga olish).
    Bu yerda faqat to‘liq to‘lanmagan oylar soni bo‘yicha hisoblanadi.
    """
    students = Student.objects.filter(status='active')
    today = date.today()
    start_date = today.replace(day=1)  # shu oydan boshlab hisoblaymiz
    # Yoki boshidan: start_date = date(2024, 1, 1)

    # Barcha to‘lovlarni olish
    payments = Payment.objects.filter(
        student__in=students,
        month_year__gte=start_date
    ).values('student_id', 'month_year').annotate(total=Sum('amount'))

    # Oylar ro'yxati
    months = []
    current = start_date
    while current <= today:
        months.append(current)
        current += timedelta(days=32)
        current = current.replace(day=1)

    paid_dict = {}
    for p in payments:
        sid = p['student_id']
        month = p['month_year']
        paid_dict.setdefault(sid, {})[month] = p['total']

    total_debt = 0
    for student in students:
        monthly_fee = student.monthly_fee
        for month in months:
            paid = paid_dict.get(student.id, {}).get(month, 0)
            if paid < monthly_fee:
                total_debt += monthly_fee - paid

    return total_debt

def get_top_debtors(limit=5):
    """
    Eng ko'p qarzdor bo'lgan o'quvchilarni qaytaradi.
    Har bir o'quvchi uchun qarzni hisoblab, limit bo'yicha saralaydi.
    Qaytariladigan ma'lumot: {student, total_debt}
    """
    students = Student.objects.filter(status='active').select_related('class_grade')
    today = date.today()
    start_date = today.replace(day=1)  # shu oydan boshlab

    # Oylar ro'yxati
    months = []
    current = start_date
    while current <= today:
        months.append(current)
        current += timedelta(days=32)
        current = current.replace(day=1)

    payments = Payment.objects.filter(
        student__in=students,
        month_year__gte=start_date
    ).values('student_id', 'month_year').annotate(total=Sum('amount'))

    paid_dict = {}
    for p in payments:
        sid = p['student_id']
        month = p['month_year']
        paid_dict.setdefault(sid, {})[month] = p['total']

    debtors = []
    for student in students:
        total_debt = 0
        monthly_fee = student.monthly_fee
        for month in months:
            paid = paid_dict.get(student.id, {}).get(month, 0)
            if paid < monthly_fee:
                total_debt += monthly_fee - paid
        if total_debt > 0:
            debtors.append({
                'student': student,
                'total_debt': total_debt
            })

    debtors.sort(key=lambda x: x['total_debt'], reverse=True)
    return debtors[:limit]