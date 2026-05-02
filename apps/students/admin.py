from django.contrib import admin
from .models import Student, ClassGrade, FeePlan


@admin.register(FeePlan)
class FeePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "amount")
    search_fields = ("name",)
    ordering = ("amount",)


@admin.register(ClassGrade)
class ClassGradeAdmin(admin.ModelAdmin):
    list_display = ("name", "default_fee_plan")
    search_fields = ("name",)
    list_filter = ("default_fee_plan",)
    autocomplete_fields = ("default_fee_plan",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "class_grade",
        "status",
        "monthly_fee_display",
        "phone",
        "parent_phone",
        "enrollment_date",
    )
    list_filter = ("status", "class_grade")
    search_fields = ("full_name", "phone", "parent_name", "parent_phone")
    autocomplete_fields = ("class_grade",)
    list_select_related = ("class_grade",)
    date_hierarchy = "enrollment_date"
    ordering = ("full_name",)

    fieldsets = (
        ("Student Info", {
            "fields": ("full_name", "class_grade", "status", "enrollment_date")
        }),
        ("Parent Info", {
            "fields": ("parent_name", "parent_phone", "phone", "address")
        }),
        ("Fee Settings", {
            "fields": ("override_fee",),
            "description": "If override_fee is empty, default class fee will be used."
        }),
    )

    def monthly_fee_display(self, obj):
        return f"{obj.monthly_fee} UZS"
    monthly_fee_display.short_description = "Monthly Fee"