import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font
# from weasyprint import HTML
from django.template.loader import render_to_string
from apps.payments.models import Payment
from apps.students.models import Student, ClassGrade

@staff_member_required
def reports_page(request):
    classes = ClassGrade.objects.all()
    return render(request, 'reports/reports.html', {'classes': classes})

@staff_member_required
def export_payments_excel(request):
    # filter by GET params (date range, class, method, cashier)
    payments = Payment.objects.select_related('student', 'created_by').all()
    # apply filters...
    wb = Workbook()
    ws = wb.active
    ws.title = "Payments"
    headers = ['Receipt', 'Date', 'Student', 'Class', 'Month', 'Amount', 'Method', 'Cashier']
    ws.append(headers)
    for p in payments:
        ws.append([
            p.receipt_number,
            p.timestamp.date(),
            p.student.full_name,
            p.student.class_grade.name,
            p.month_year.strftime('%Y-%m'),
            float(p.amount),
            p.get_method_display(),
            p.created_by.username
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=payments.xlsx'
    wb.save(response)
    return response

@staff_member_required
def export_payments_pdf(request):
    payments = Payment.objects.select_related('student').all()
    html_string = render_to_string('reports/payments_pdf.html', {'payments': payments})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=payments.pdf'
    return response