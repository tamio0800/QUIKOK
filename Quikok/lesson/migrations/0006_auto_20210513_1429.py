# Generated by Django 3.1.5 on 2021-05-13 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0005_auto_20210513_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson_completed_record',
            name='tuition_fee',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='lesson_sales_sets',
            name='price_per_10_minutes',
            field=models.FloatField(null=True),
        ),
    ]
