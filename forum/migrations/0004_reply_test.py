# Generated by Django 2.2.6 on 2019-10-28 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20191028_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='test',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]