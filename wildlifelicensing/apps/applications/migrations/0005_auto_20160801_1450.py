# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-01 06:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wl_applications', '0004_auto_20160623_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='invoice_number',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='application',
            name='order_number',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
