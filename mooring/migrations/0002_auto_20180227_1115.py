# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-27 03:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mooring', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mooringarea',
            old_name='campground_map',
            new_name='mooring_map',
        ),
    ]