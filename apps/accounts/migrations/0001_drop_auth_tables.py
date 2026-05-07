from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("payments", "0002_remove_payment_created_by"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS django_admin_log;
            DROP TABLE IF EXISTS auth_group_permissions;
            DROP TABLE IF EXISTS auth_user_groups;
            DROP TABLE IF EXISTS auth_user_user_permissions;
            DROP TABLE IF EXISTS auth_permission;
            DROP TABLE IF EXISTS auth_group;
            DROP TABLE IF EXISTS auth_user;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
