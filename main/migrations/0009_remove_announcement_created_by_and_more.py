# Generated by Django 5.1.7 on 2025-04-04 14:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_announcement_announcementfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcement',
            name='created_by',
        ),
        migrations.AddField(
            model_name='announcement',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.institution', verbose_name='Institution'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='audience',
            field=models.CharField(choices=[('sitewide', 'Sitewide'), ('institution', 'Selected Institution')], default='sitewide', max_length=20, verbose_name='Audience'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created Date and Time'),
        ),
        migrations.AlterField(
            model_name='announcement',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated Date and Time'),
        ),
    ]
