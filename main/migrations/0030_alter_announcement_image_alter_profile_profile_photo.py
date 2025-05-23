# Generated by Django 5.1.7 on 2025-04-19 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_profile_sinta_name_match_profile_sinta_name_scraped'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='announcements/images/'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='profiles/photos/'),
        ),
    ]
