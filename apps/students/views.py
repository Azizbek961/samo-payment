from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.http import HttpResponse
from .models import Student, ClassGrade
import csv
from datetime import date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Debt
from .forms import DebtForm
import openpyxl
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from datetime import datetime
from apps.payments.models import Payment
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from apps.students.models import Student
from apps.payments.models import Payment
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

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
            # To'lovlarni ham o'chirish
            self.object.payments.all().delete()  # agar related_name='payments' bo'lsa
            self.object.delete()
            messages.success(request, f"{self.object.full_name} va unga tegishli barcha to'lovlar o'chirildi.")
            return HttpResponseRedirect(self.success_url)

        elif action == 'delete_only_student':
            # Faqat o'quvchini o'chirish, to'lovlarni student_id = NULL qilish
            # SET_NULL amal qiladi, shuning uchun o'quvchi o'chirilganda to'lovlar avtomatik NULL bo'ladi
            self.object.delete()
            messages.success(request, f"{self.object.full_name} o'chirildi. To'lovlar saqlanib qoldi.")
            return HttpResponseRedirect(self.success_url)

        else:
            # Agar action kelmagan bo'lsa, eski usulda tekshirish (xavfsizlik uchun)
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
        # Fayl kengaytmasiga qarab ishlash
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
                # class_grade nomi bo'yicha topish
                class_grade_name = row.get('class_grade') or row.get('Sinf')
                if not class_grade_name:
                    errors.append(f"Qatorda sinf ko'rsatilmagan: {row}")
                    continue
                class_grade = ClassGrade.objects.get(name=class_grade_name)

                # Sana formatini moslashtirish
                enrollment_date = row.get('enrollment_date') or row.get("Qabul sanasi")
                if isinstance(enrollment_date, str):
                    enrollment_date = datetime.strptime(enrollment_date, '%Y-%m-%d').date()
                # Agar Excel dan kelgan bo'lsa, datetime obyekti bo'ladi

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




class DebtListView(LoginRequiredMixin, TemplateView):
    template_name = 'debts/debt_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aktiv o‘quvchilar
        students = Student.objects.filter(status='active').select_related('class_grade')
        today = datetime.now().date()
        start_date = today.replace(day=1)  # joriy oyning birinchi kuni

        # Oylar ro‘yxati (masalan, 2026-fevral)
        months_list = []
        current = start_date
        while current <= today:
            months_list.append(current)
            current += relativedelta(months=1)

        # Har bir o‘quvchi va oy uchun jami to‘lov summalari
        payments_sum = Payment.objects.filter(
            student__in=students,
            month_year__gte=start_date
        ).values('student_id', 'month_year').annotate(total=Sum('amount'))

        # student_id -> {month_year: total} lug'at
        paid_dict = {}
        for p in payments_sum:
            sid = p['student_id']
            month = p['month_year']
            paid_dict.setdefault(sid, {})[month] = p['total']

        debtors = []
        for student in students:
            unpaid_months = []
            total_debt = 0
            monthly_fee = student.monthly_fee

            for month in months_list:
                paid = paid_dict.get(student.id, {}).get(month, 0)
                if paid < monthly_fee:
                    # To'liq to'lanmagan – qarz bor
                    unpaid_months.append(month)
                    total_debt += monthly_fee - paid

            if unpaid_months:
                debtors.append({
                    'student': student,
                    'unpaid_months': unpaid_months,
                    'total_debt': total_debt,
                    'monthly_fee': monthly_fee,
                    'extra_debts': student_debts,
                })

        # Qarz miqdoriga qarab kamayish tartibida saralash
        debtors.sort(key=lambda x: x['total_debt'], reverse=True)
        context['debtors'] = debtors
        return context
class DebtCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'students/debt_form.html'
    success_url = reverse_lazy('student-debts')  # qarzdorlar ro'yxatiga qaytadi
    permission_required = 'students.add_debt'   # ruxsat

class DebtListView(LoginRequiredMixin, TemplateView):
    template_name = 'debts/debt_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = Student.objects.filter(status='active').select_related('class_grade')
        today = datetime.now().date()
        start_date = today.replace(day=1)

        # Oylar ro'yxati (joriy oy)
        months_list = [start_date]

        # To'lovlar summasi
        payments_sum = Payment.objects.filter(
            student__in=students,
            month_year__gte=start_date
        ).values('student_id', 'month_year').annotate(total=Sum('amount'))

        paid_dict = {}
        for p in payments_sum:
            paid_dict.setdefault(p['student_id'], {})[p['month_year']] = p['total']

        # Qarzlar (Debt modeli) - to'lanmagan qarzlar
        debts_qs = Debt.objects.filter(student__in=students, is_paid=False)
        debt_dict = {}
        for d in debts_qs:
            debt_dict.setdefault(d.student_id, []).append(d)

        debtors = []
        for student in students:
            total_debt = 0
            unpaid_months = []
            monthly_fee = student.monthly_fee

            # Oylik to'lov bo'yicha qarz
            for month in months_list:
                paid = paid_dict.get(student.id, {}).get(month, 0)
                if paid < monthly_fee:
                    unpaid_months.append(month)
                    total_debt += monthly_fee - paid

            # Qo'lda kiritilgan qarzlar
            student_debts = debt_dict.get(student.id, [])
            for d in student_debts:
                total_debt += d.amount
                # qarzni alohida ko'rsatish uchun unpaid_months ga qo'shish mumkin yoki description
                # Biz unpaid_months ga qo'shimcha ma'lumot qo'shmaymiz, faqat umumiy qarzga qo'shamiz.

            if total_debt > 0:
                debtors.append({
                    'student': student,
                    'unpaid_months': unpaid_months,
                    'total_debt': total_debt,
                    'monthly_fee': monthly_fee,
                    'extra_debts': student_debts,  # agar template da ko'rsatmoqchi bo'lsangiz
                })

        debtors.sort(key=lambda x: x['total_debt'], reverse=True)
        context['debtors'] = debtors
        return context




# apps/students/views.py (yoki mos papka)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, UpdateView, DeleteView
from .models import Debt
from .forms import DebtForm   # Agar form mavjud bo‘lsa

class DebtDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Bitta qarzning tafsilotlari"""
    model = Debt
    template_name = 'students/debt_detail.html'
    context_object_name = 'debt'
    permission_required = 'students.view_debt'


class DebtUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Qarz ma'lumotlarini tahrirlash"""
    model = Debt
    form_class = DebtForm
    template_name = 'students/debt_form.html'   # Create bilan bir xil shablon
    permission_required = 'students.change_debt'

    def get_success_url(self):
        return reverse_lazy('debt-detail', kwargs={'pk': self.object.pk})


class DebtDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Qarzni o‘chirish (faqat is_paid=False bo‘lsa ruxsat berish mumkin)"""
    model = Debt
    template_name = 'students/debt_confirm_delete.html'
    success_url = reverse_lazy('student-debts')
    permission_required = 'students.delete_debt'

    def form_valid(self, form):
        # Ixtiyoriy: agar to‘langan qarzni o‘chirishni cheklash
        if self.object.is_paid:
            from django.contrib import messages
            messages.error(self.request, "To‘langan qarzni o‘chirib bo‘lmaydi.")
            return redirect('debt-detail', pk=self.object.pk)
        return super().form_valid(form)
