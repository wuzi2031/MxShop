# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-08 12:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodscategorybrand',
            name='desc',
            field=models.CharField(default='', help_text='品牌描述', max_length=300, verbose_name='品牌描述'),
        ),
    ]
