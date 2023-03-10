# Generated by Django 4.0.5 on 2022-12-20 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_customerinfo_emergency_contact_customerinfo_id_num_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(default=123, max_length=255, unique=True, verbose_name='email address'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='password',
            field=models.CharField(default=123, max_length=128, verbose_name='password'),
            preserve_default=False,
        ),
    ]
