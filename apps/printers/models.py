from django.db import models

class PrinterConfig(models.Model):
    TYPE_CHOICES = [
        ('network', 'Network Printer (IP:Port)'),
        ('windows', 'Windows Shared Printer'),
    ]
    printer_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='network')
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="Required for network printer")
    port = models.IntegerField(default=9100, help_text="Port for network printer")
    printer_name = models.CharField(max_length=255, blank=True, help_text="Windows printer name (e.g., 'Xprinter XP-80C')")
    paper_width = models.IntegerField(default=80, help_text="Paper width in mm")
    logo_text = models.CharField(max_length=255, default="My School", help_text="Header text")
    school_name = models.CharField(max_length=255, default="Private School")
    school_address = models.CharField(max_length=255, blank=True)
    school_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Printer Configuration"
        # enforce singleton
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name="single_printer_config")]

    def save(self, *args, **kwargs):
        self.id = 1  # force singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        return cls.objects.get_or_create(id=1)[0]