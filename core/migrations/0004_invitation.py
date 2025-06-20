# Generated by Django 5.2.3 on 2025-06-12 12:06

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_datascope'),
        ('end_customers', '0001_initial'),
        ('major_clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('invitation_type', models.CharField(choices=[('FREIGHT_ADMIN', 'Freight Company Admin'), ('END_CUSTOMER_ADMIN', 'End Customer Admin'), ('END_CUSTOMER_STAFF', 'End Customer Staff')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('accepted', models.BooleanField(default=False)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('end_customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='end_customers.endcustomer')),
                ('freight_company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='major_clients.freightcompany')),
                ('invited_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_invitations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
