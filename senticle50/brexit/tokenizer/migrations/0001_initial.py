# Generated by Django 2.0 on 2018-01-08 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scraper', '0007_auto_20171229_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenizedTweet',
            fields=[
                ('id', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='scraper.Tweet')),
                ('tokens', models.TextField(blank=True, max_length=280)),
            ],
            options={
                'db_table': 'Tokenized_Tweet',
                'managed': True,
                'verbose_name': 'Tokenized_Tweet',
            },
        ),
    ]
