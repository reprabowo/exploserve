# Generated by Django 5.1.7 on 2025-04-18 23:09

import main.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_alter_institution_akreditasi'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to=main.models.profile_photo_upload_path, verbose_name='Profile Photo'),
        ),
    ]
