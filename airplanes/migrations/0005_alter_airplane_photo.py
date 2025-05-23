# Generated by Django 5.2 on 2025-05-06 12:06

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('airplanes', '0004_airplanetype_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airplane',
            name='photo',
            field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='JPEG', keep_meta=True, null=True, quality=-1, scale=None, size=[300, 300], upload_to='airplanes/'),
        ),
    ]
