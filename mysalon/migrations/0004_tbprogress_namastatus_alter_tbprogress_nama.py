# Generated by Django 5.0.3 on 2024-06-29 06:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysalon', '0003_remove_tbprogress_staff_tbprogress_nama'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbprogress',
            name='namastatus',
            field=models.CharField(choices=[], default='Belum di ACC', max_length=20),
        ),
        migrations.AlterField(
            model_name='tbprogress',
            name='nama',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='mysalon.staff'),
        ),
    ]
