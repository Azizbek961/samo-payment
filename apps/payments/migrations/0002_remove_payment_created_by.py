from django.db import migrations


def remove_created_by_column(apps, schema_editor):
    table_name = "payments_payment"
    with schema_editor.connection.cursor() as cursor:
        description = schema_editor.connection.introspection.get_table_description(cursor, table_name)
        columns = {column.name for column in description}
        if "created_by_id" not in columns:
            return

        cursor.execute("DROP INDEX IF EXISTS payments_payment_created_by_id_28f0e284;")
        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN created_by_id;")


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(remove_created_by_column, migrations.RunPython.noop),
    ]
