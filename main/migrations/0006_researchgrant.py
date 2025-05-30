# Generated by Django 5.1.7 on 2025-04-03 10:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_profile_program_studi'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ResearchGrant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('offered_to', models.CharField(choices=[('all', 'Sitewide'), ('institution', 'Own Institution')], default='all', max_length=20, verbose_name='Offered To')),
                ('start_year', models.PositiveIntegerField(verbose_name='Start Year')),
                ('end_year', models.PositiveIntegerField(verbose_name='End Year')),
                ('qualification_criteria', models.TextField(blank=True, null=True, verbose_name='Qualification Criteria')),
                ('identitas_usulan', models.TextField(blank=True, null=True, verbose_name='Identitas Usulan')),
                ('substansi_dan_luaran', models.TextField(blank=True, null=True, verbose_name='Substansi dan Luaran')),
                ('rab', models.TextField(blank=True, null=True, verbose_name='RAB')),
                ('dokumen_pendukung', models.FileField(blank=True, null=True, upload_to='grants/documents/', verbose_name='Dokumen Pendukung')),
                ('konfirmasi_usulan', models.TextField(blank=True, null=True, verbose_name='Konfirmasi Usulan')),
                ('approved_by_pt', models.BooleanField(default=False, verbose_name='Approved by Pimpinan PT')),
                ('approved_by_ppm', models.BooleanField(default=False, verbose_name='Approved by Unit Pengelola PPM')),
                ('review_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Review Score')),
                ('final_decision', models.CharField(blank=True, max_length=50, null=True, verbose_name='Final Decision')),
                ('announcement', models.TextField(blank=True, null=True, verbose_name='Announcement')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grants_created', to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.institution', verbose_name='Institution')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grants_review', to=settings.AUTH_USER_MODEL, verbose_name='Assigned Reviewer')),
            ],
        ),
    ]
