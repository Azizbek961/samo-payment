from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("printers", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="printerconfig",
            name="printer_name",
            field=models.CharField(
                blank=True,
                help_text="Windows printer name or Linux CUPS queue name (e.g., 'XP-80C' or 'POS80')",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="printerconfig",
            name="printer_type",
            field=models.CharField(
                choices=[
                    ("network", "Network Printer (IP:Port)"),
                    ("windows", "Windows Shared Printer"),
                    ("linux", "Linux CUPS Printer"),
                ],
                default="network",
                max_length=10,
            ),
        ),
    ]
