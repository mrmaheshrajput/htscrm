# Generated by Django 3.0.2 on 2020-02-17 06:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customers', '0002_auto_20200213_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientdetails',
            name='edit_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientdetails',
            name='edited_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_edited_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='clientdetails',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customer_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
