# Generated by Django 4.2.7 on 2023-12-20 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_s3model_telegramapi'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TelegramApi',
            new_name='TelegramApirec',
        ),
    ]