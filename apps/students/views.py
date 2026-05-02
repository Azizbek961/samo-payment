from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum
from .models import Student, ClassGrade, Debt
from .forms import ClassGradeForm, DebtForm
from apps.payments.models import Payment
from apps.payments.services.debt import DEBT_START_MONTH
import csv
import openpyxl
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import calendar
from decimal import Decimal


# ---------- CRUD ----------
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Student
    fields = ['full_name', 'phone', 'parent_name', 'parent_phone', 'address',
              'class_grade', 'enrollment_date', 'status', 'override_fee']
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')
    permission_required = 'students.add_student'


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Student
    fields = ['full_name', 'phone', 'parent_name', 'parent_phone', 'address',
              'class_grade', 'enrollment_date', 'status', 'override_fee']
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student-list')
    permission_required = 'students.change_student'


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')
    permission_required = 'students.delete_student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_payments'] = Payment.objects.filter(student=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')

        if action == 'delete_with_payments':
            self.object.payments.all().delete()
            self.object.delete()
            messages.success(request, f"{self.object.full_name} va unga tegishli barcha to'lovlar o'chirildi.")
            return HttpResponseRedirect(self.success_url)

        elif action == 'delete_only_student':
            self.object.delete()
            messages.success(request, f"{self.object.full_name} o'chirildi. To'lovlar saqlanib qoldi.")
            return HttpResponseRedirect(self.success_url)

        else:
            if Payment.objects.filter(student=self.object).exists():
                messages.error(request, "To'lovlarni ham o'chirish variantini tanlang.")
                return redirect('student-delete', pk=self.object.pk)
            else:
                self.object.delete()
                messages.success(request, "O'quvchi o'chirildi.")
                return HttpResponseRedirect(self.success_url)


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'


# ---------- IMPORT ----------
@login_required
def import_students(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            decoded = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)
        elif file.name.endswith(('.xlsx', '.xls')):
            wb = openpyxl.load_workbook(file)
            sheet = wb.active
            headers = [cell.value for cell in sheet[1]]
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                rows.append(dict(zip(headers, row)))
            reader = rows
        else:
            messages.error(request, "Faqat CSV yoki Excel fayllari qabul qilinadi.")
            return redirect('student-import')

        created_count = 0
        errors = []
        for row in reader:
            try:
                class_grade_name = row.get('class_grade') or row.get('Sinf')
                if not class_grade_name:
                    errors.append(f"Qatorda sinf ko'rsatilmagan: {row}")
                    continue
                class_grade = ClassGrade.objects.get(name=class_grade_name)

                enrollment_date = row.get('enrollment_date') or row.get("Qabul sanasi")
                if isinstance(enrollment_date, str):
                    enrollment_date = datetime.strptime(enrollment_date, '%Y-%m-%d').date()

                student = Student(
                    full_name=row.get('full_name') or row.get('F.I.O.'),
                    phone=row.get('phone') or row.get('Telefon'),
                    parent_name=row.get('parent_name') or row.get('Ota-ona'),
                    parent_phone=row.get('parent_phone') or row.get('Ota-ona telefoni'),
                    address=row.get('address') or row.get('Manzil', ''),
                    class_grade=class_grade,
                    enrollment_date=enrollment_date,
                    status=row.get('status') or row.get('Holati', 'active'),
                    override_fee=row.get('override_fee') or row.get('Maxsus to\'lov') or None,
                )
                student.save()
                created_count += 1
            except ClassGrade.DoesNotExist:
                errors.append(f"Sinf topilmadi: {class_grade_name}")
            except Exception as e:
                errors.append(f"Xatolik: {e}")

        if created_count:
            messages.success(request, f"{created_count} ta o'quvchi muvaffaqiyatli import qilindi.")
        if errors:
            messages.warning(request, f"Quyidagi xatolar yuz berdi: {', '.join(errors[:5])}")

        return redirect('student-list')

    return render(request, 'students/student_import.html')


# ---------- EXPORT ----------
@login_required
def export_students(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'

    writer = csv.writer(response)
    writer.writerow(['F.I.O.', 'Telefon', 'Ota-ona', 'Ota-ona telefoni', 'Manzil', 'Sinf', 'Qabul sanasi', 'Holati', 'Maxsus to\'lov'])

    for student in Student.objects.select_related('class_grade').all():
        writer.writerow([
            student.full_name,
            student.phone,
            student.parent_name,
            student.parent_phone,
            student.address,
            student.class_grade.name,
            student.enrollment_date,
            student.status,
            student.override_fee or '',
        ])

    return response


# ---------- DEBTS ----------
class DebtListView(LoginRequiredMixin, TemplateView):
    template_name = 'debts/debt_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = Student.objects.filter(status='active').select_related('class_grade')
        today = datetime.now().date()
        current_month = today.replace(day=1)
        earliest_student = students.order_by('enrollment_date').first()
        enrollment_floor = earliest_student.enrollment_date.replace(day=1) if earliest_student else current_month
        min_allowed_month = max(DEBT_START_MONTH, enrollment_floor)

        selected_month_str = self.request.GET.get('month')
        if selected_month_str:
            try:
                year, month = map(int, selected_month_str.split('-'))
                selected_month = date(year, month, 1)
            except (ValueError, TypeError):
                selected_month = current_month
        else:
            selected_month = current_month

        if selected_month < min_allowed_month:
            selected_month = min_allowed_month
        if selected_month > current_month:
            selected_month = current_month

        payments_sum = Payment.objects.filter(
            student__in=students,
            month_year__lte=selected_month
        ).values('student_id', 'month_year').annotate(total=Sum('amount'))

        paid_dict = {}
        for p in payments_sum:
            paid_dict.setdefault(p['student_id'], {})[p['month_year']] = p['total']

        debts_qs = Debt.objects.filter(student__in=students, is_paid=False)
        debt_dict = {}
        for d in debts_qs:
            debt_dict.setdefault(d.student_id, []).append(d)

        debtors = []
        for student in students:
            total_debt = Decimal('0')
            unpaid_months = []
            monthly_fee = student.monthly_fee
            enrollment_month = max(student.enrollment_date.replace(day=1), DEBT_START_MONTH)
            month = enrollment_month
            selected_month_unpaid = False

            while month <= selected_month:
                paid = paid_dict.get(student.id, {}).get(month, Decimal('0'))
                if paid < monthly_fee:
                    total_debt += monthly_fee - paid
                    if month == selected_month:
                        selected_month_unpaid = True
                month += relativedelta(months=1)

            if selected_month_unpaid:
                unpaid_months.append(selected_month)

            student_debts = debt_dict.get(student.id, [])
            for d in student_debts:
                total_debt += d.amount

            if total_debt > 0:
                debtors.append({
                    'student': student,
                    'unpaid_months': unpaid_months,
                    'total_debt': total_debt,
                    'monthly_fee': monthly_fee,
                    'extra_debts': student_debts,
                })

        debtors.sort(key=lambda x: x['total_debt'], reverse=True)
        months_list = []
        month_cursor = current_month
        while month_cursor >= min_allowed_month:
            months_list.append({
                'value': month_cursor.strftime('%Y-%m'),
                'label': month_cursor.strftime('%B %Y'),
            })
            month_cursor += relativedelta(months=-1)

        context['debtors'] = debtors
        context['months_list'] = months_list
        context['selected_month'] = selected_month.strftime('%Y-%m')
        context['current_month_name'] = selected_month.strftime('%B %Y')
        context['prev_month'] = (selected_month + relativedelta(months=-1)).strftime('%Y-%m')
        context['next_month'] = (selected_month + relativedelta(months=1)).strftime('%Y-%m')
        context['prev_month_disabled'] = selected_month <= min_allowed_month
        context['next_month_disabled'] = selected_month >= current_month
        return context


class DebtCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'students/debt_form.html'
    success_url = reverse_lazy('student-debts')
    permission_required = 'students.add_debt'


class DebtDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Debt
    template_name = 'students/debt_detail.html'
    context_object_name = 'debt'
    permission_required = 'students.view_debt'


class DebtUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Debt
    form_class = DebtForm
    template_name = 'students/debt_form.html'
    permission_required = 'students.change_debt'

    def get_success_url(self):
        return reverse_lazy('debt-detail', kwargs={'pk': self.object.pk})


class DebtDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Debt
    template_name = 'students/debt_confirm_delete.html'
    success_url = reverse_lazy('student-debts')
    permission_required = 'students.delete_debt'

    def form_valid(self, form):
        if self.object.is_paid:
            messages.error(self.request, "To'langan qarzni o'chirib bo'lmaydi.")
            return redirect('debt-detail', pk=self.object.pk)
        return super().form_valid(form)


# ---------- CLASS GRADES ----------
@login_required
def class_list(request):
    classes = ClassGrade.objects.all().order_by("name")
    return render(request, "students/class_list.html", {"classes": classes})


@login_required
def class_create(request):
    if request.method == "POST":
        form = ClassGradeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("class_list")
    else:
        form = ClassGradeForm()
    return render(request, "students/class_form.html", {"form": form})
