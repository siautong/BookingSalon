# Generated by Django 5.0.3 on 2024-07-03 01:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mysalon', '0011_tbbooking_alamat_tbbooking_nama_tbbooking_nohp_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tbbooking',
            old_name='user',
            new_name='username',
        ),
    ]
