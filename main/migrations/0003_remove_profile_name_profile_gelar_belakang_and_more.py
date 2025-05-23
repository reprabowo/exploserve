# Generated by Django 5.1.7 on 2025-03-31 18:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_institution_profile_institution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='name',
        ),
        migrations.AddField(
            model_name='profile',
            name='gelar_belakang',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Gelar Belakang'),
        ),
        migrations.AddField(
            model_name='profile',
            name='gelar_depan',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Gelar Depan'),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_reviewer_assigned',
            field=models.BooleanField(default=False, verbose_name='Research Reviewer Assigned'),
        ),
        migrations.AddField(
            model_name='profile',
            name='jabatan_akademik',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Jabatan Akademik'),
        ),
        migrations.AddField(
            model_name='profile',
            name='jenjang_pendidikan',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Jenjang Pendidikan'),
        ),
        migrations.AddField(
            model_name='profile',
            name='nama_lengkap',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nama Lengkap'),
        ),
        migrations.AddField(
            model_name='profile',
            name='nidn_nidk',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='NIDN/NIDK'),
        ),
        migrations.AddField(
            model_name='profile',
            name='no_hp',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='No HP'),
        ),
        migrations.AddField(
            model_name='profile',
            name='orcid_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Orcid ID'),
        ),
        migrations.AddField(
            model_name='profile',
            name='program_studi',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Program Studi'),
        ),
        migrations.AddField(
            model_name='profile',
            name='research_interest',
            field=models.TextField(blank=True, null=True, verbose_name='Research Interest'),
        ),
        migrations.AddField(
            model_name='profile',
            name='sinta_id',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Sinta ID'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='researchers', to='main.institution', verbose_name='Institusi'),
        ),
    ]
