# Generated by Django 2.2.6 on 2019-11-09 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_auto_20191107_0925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='author',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='messages',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='message',
            name='read_status',
        ),
        migrations.AddField(
            model_name='message',
            name='chat_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chat.Chat'),
        ),
    ]
