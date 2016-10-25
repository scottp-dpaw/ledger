# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-25 07:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0006_campground_bookable_per_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(max_length=255)),
                ('description', models.TextField()),
                ('opening_hours', models.TextField()),
                ('other_services', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='campground',
            name='regulations',
        ),
        migrations.AddField(
            model_name='campground',
            name='fees',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='campground',
            name='key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='campground',
            name='othertransport',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='park',
            name='entry_fee_required',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='feature',
            name='image',
            field=models.ImageField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='campground',
            name='customer_contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='parkstay.CustomerContact'),
        ),
    ]