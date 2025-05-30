# Generated by Django 5.1.7 on 2025-04-16 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_alter_programstudi_jenjang_alter_programstudi_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='badan_penyelenggara',
            field=models.CharField(default=1, max_length=255, verbose_name='Badan Penyelenggara'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='institution',
            name='logo_bp',
            field=models.ImageField(blank=True, null=True, upload_to='institutions/bp_logos/', verbose_name='Logo BP'),
        ),
        migrations.AddField(
            model_name='institution',
            name='website_bp',
            field=models.URLField(blank=True, null=True, verbose_name='Website BP'),
        ),
    ]
