# Generated by Django 2.0 on 2017-12-29 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0006_auto_20171219_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='text',
            field=models.TextField(blank=True, max_length=280, null=True),
        ),
    ]