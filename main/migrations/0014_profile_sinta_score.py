# Generated by Django 5.1.7 on 2025-04-11 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_profile_profile_photo_alter_announcement_audience_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='sinta_score',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Sinta Score'),
        ),
    ]
