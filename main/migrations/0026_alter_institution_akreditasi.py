# Generated by Django 5.1.7 on 2025-04-17 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_institution_badan_penyelenggara_institution_logo_bp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institution',
            name='akreditasi',
            field=models.CharField(blank=True, choices=[('internasional', 'Internasional'), ('unggul', 'Unggul'), ('baik_sekali', 'Baik Sekali'), ('baik', 'Baik'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('tidak_terakreditasi', 'Tidak Terakreditasi')], max_length=50, null=True, verbose_name='Akreditasi'),
        ),
    ]
