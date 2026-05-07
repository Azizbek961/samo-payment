from datetime import date, timedelta
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from apps.payments.models import Payment
from apps.payments.services.debt import DEBT_START_MONTH
from apps.students.models import ClassGrade, FeePlan, Student


class DebtListViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        fee_plan = FeePlan.objects.create(name="Standard", amount=Decimal("200000"))
        class_grade = ClassGrade.objects.create(name="5-A", default_fee_plan=fee_plan)

        enrollment_date = date(2026, 2, 4)
        self.student = Student.objects.create(
            full_name="Ali Valiyev",
            phone="+998901234567",
            parent_name="Vali Valiyev",
            parent_phone="+998909876543",
            address="Tashkent",
            class_grade=class_grade,
            enrollment_date=enrollment_date,
            status="active",
        )

    def test_debt_list_shows_previous_unpaid_months(self):
        current_month = timezone.localdate().replace(day=1)
        previous_month = current_month + relativedelta(months=-1)
        debt_start = max(DEBT_START_MONTH, self.student.enrollment_date.replace(day=1))
        unpaid_month_count = 0
        cursor = debt_start
        while cursor < current_month:
            unpaid_month_count += 1
            cursor += relativedelta(months=1)

        Payment.objects.create(
            student=self.student,
            month_year=current_month,
            amount=Decimal("200000"),
            method="cash",
        )

        response = self.client.get(reverse("student-debts"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["debtors"]), 1)

        debtor = response.context["debtors"][0]
        self.assertEqual(debtor["student"], self.student)
        self.assertEqual(debtor["unpaid_months"], [])
        self.assertEqual(debtor["total_debt"], Decimal("200000") * unpaid_month_count)
        self.assertEqual(response.context["months_list"][-1]["value"], debt_start.strftime("%Y-%m"))

    def test_debt_list_allows_switching_month(self):
        current_month = timezone.localdate().replace(day=1)
        previous_month = current_month + relativedelta(months=-1)
        debt_start = max(DEBT_START_MONTH, self.student.enrollment_date.replace(day=1))
        unpaid_month_count = 0
        cursor = debt_start
        while cursor <= previous_month:
            unpaid_month_count += 1
            cursor += relativedelta(months=1)

        response = self.client.get(reverse("student-debts"), {"month": previous_month.strftime("%Y-%m")})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_month"], previous_month.strftime("%Y-%m"))
        self.assertFalse(response.context["next_month_disabled"])

        debtor = response.context["debtors"][0]
        self.assertEqual(debtor["total_debt"], Decimal("200000") * unpaid_month_count)
        self.assertNotIn(current_month, debtor["unpaid_months"])
        self.assertEqual(debtor["unpaid_months"], [previous_month])
