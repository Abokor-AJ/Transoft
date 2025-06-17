from django.db import migrations
from django.contrib.auth.models import User

def create_user_profiles(apps, schema_editor):
    UserProfile = apps.get_model('core', 'UserProfile')
    for user in User.objects.all():
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'END_CUSTOMER_ADMIN'
            }
        )

def reverse_create_user_profiles(apps, schema_editor):
    UserProfile = apps.get_model('core', 'UserProfile')
    UserProfile.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user_profiles, reverse_create_user_profiles),
    ] 