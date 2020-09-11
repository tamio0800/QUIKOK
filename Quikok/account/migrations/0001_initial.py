# Generated by Django 2.0.4 on 2020-09-10 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='connects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=191)),
                ('connected_user', models.CharField(max_length=191)),
            ],
        ),
        migrations.CreateModel(
            name='dev_db',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=120)),
                ('password', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=40)),
                ('birth_date', models.DateField()),
                ('is_male', models.BooleanField()),
                ('date_join', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='general_available_time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week', models.IntegerField(max_length=1)),
                ('time', models.CharField(max_length=133)),
            ],
        ),
        migrations.CreateModel(
            name='specific_available_time',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(max_length=20)),
                ('time', models.CharField(max_length=133)),
            ],
        ),
        migrations.CreateModel(
            name='student_profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=128)),
                ('balance', models.IntegerField(default=0)),
                ('withholding_balance', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=40)),
                ('nickname', models.CharField(max_length=40)),
                ('birth_date', models.DateField(null=True)),
                ('is_male', models.BooleanField()),
                ('intro', models.CharField(blank=True, default='', max_length=300)),
                ('role', models.CharField(max_length=40)),
                ('mobile', models.CharField(max_length=12)),
                ('picture_folder', models.CharField(max_length=60)),
                ('info_folder', models.CharField(max_length=100)),
                ('update_someone_by_email', models.CharField(blank=True, max_length=405)),
                ('date_join', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='student_studying_history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='studying_history', to='account.student_profile')),
            ],
        ),
        migrations.CreateModel(
            name='teacher_profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=128)),
                ('balance', models.IntegerField(default=0)),
                ('withholding_balance', models.IntegerField(default=0)),
                ('unearned_balance', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=40)),
                ('nickname', models.CharField(max_length=40)),
                ('birth_date', models.DateField(null=True)),
                ('is_male', models.BooleanField()),
                ('intro', models.CharField(max_length=150)),
                ('mobile', models.CharField(max_length=12)),
                ('picture_folder', models.CharField(max_length=60)),
                ('info_folder', models.CharField(max_length=100)),
                ('tutor_experience', models.CharField(max_length=12)),
                ('subject_type', models.CharField(max_length=400)),
                ('education_1', models.CharField(blank=True, max_length=60)),
                ('education_2', models.CharField(blank=True, max_length=60)),
                ('education_3', models.CharField(blank=True, max_length=60)),
                ('cert_unapproved', models.CharField(max_length=60)),
                ('cert_approved', models.CharField(max_length=60)),
                ('id_approved', models.CharField(max_length=60)),
                ('education_approved', models.CharField(max_length=60)),
                ('work_approved', models.CharField(max_length=60)),
                ('other_approved', models.CharField(max_length=60)),
                ('occupation', models.CharField(blank=True, max_length=60)),
                ('company', models.CharField(blank=True, max_length=60)),
                ('is_approved', models.BooleanField(default=False)),
                ('date_join', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='teacher_teaching_history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teaching_history', to='account.teacher_profile')),
            ],
        ),
        migrations.AddField(
            model_name='specific_available_time',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specific_time', to='account.teacher_profile'),
        ),
        migrations.AddField(
            model_name='general_available_time',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='general_time', to='account.teacher_profile'),
        ),
    ]
