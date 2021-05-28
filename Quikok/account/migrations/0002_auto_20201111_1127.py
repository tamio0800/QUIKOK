# Generated by Django 3.1.2 on 2020-11-11 03:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite_lessons',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student_profile',
            name='info_folder',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='student_profile',
            name='thumbnail_dir',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='student_profile',
            name='user_folder',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='teacher_profile',
            name='info_folder',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='teacher_profile',
            name='subject_type',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='teacher_profile',
            name='thumbnail_dir',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='teacher_profile',
            name='user_folder',
            field=models.TextField(blank=True),
        ),
    ]
