# Generated by Django 3.1.2 on 2021-05-04 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='object_accessed_info',
            name='user_agent',
            field=models.CharField(blank=True, max_length=550, null=True),
        ),
    ]
