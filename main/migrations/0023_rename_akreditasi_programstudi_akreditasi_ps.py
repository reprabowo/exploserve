# Generated by Django 5.1.7 on 2025-04-15 06:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_remove_institution_sinta_scorego_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='programstudi',
            old_name='akreditasi',
            new_name='akreditasi_ps',
        ),
    ]
