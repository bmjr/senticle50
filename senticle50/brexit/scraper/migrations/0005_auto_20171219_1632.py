# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-19 16:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0004_auto_20171219_0019'),
    ]

    operations = [
        migrations.RenameModel("Tweets", "Tweet")
    ]
