from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import PrinterConfig


@admin.register(PrinterConfig)
class PrinterConfigAdmin(admin.ModelAdmin):
    list_display = (
        "printer_type",
        "ip_address",
        "port",
        "printer_name",
        "paper_width",
        "school_name",
    )
    fieldsets = (
        ("Printer Mode", {
            "fields": ("printer_type", "paper_width"),
            "description": "Choose how receipts will be printed.",
        }),
        ("Network Printer (ESC/POS)", {
            "fields": ("ip_address", "port"),
            "description": "Use when printer is connected via LAN (IP:Port). Usually port is 9100.",
        }),
        ("Windows Printer", {
            "fields": ("printer_name",),
            "description": "Use when printer is installed in Windows and shared/available by name.",
        }),
        ("Receipt Header", {
            "fields": ("logo_text", "school_name", "school_address", "school_phone"),
        }),
    )

    def has_add_permission(self, request):
        # Singleton: only allow add if no config exists
        return not PrinterConfig.objects.filter(id=1).exists()

    def has_delete_permission(self, request, obj=None):
        # Singleton: prevent deleting
        return False

    def changelist_view(self, request, extra_context=None):
        """
        Redirect the changelist to the single object edit page.
        """
        config = PrinterConfig.get_config()
        return HttpResponseRedirect(
            reverse("admin:printers_printerconfig_change", args=(config.id,))
        )