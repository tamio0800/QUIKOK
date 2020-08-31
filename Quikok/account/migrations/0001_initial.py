from django.db import migrations, models


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
            name='student_profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=40)),
                ('nickname', models.CharField(max_length=40)),
                ('birth_date', models.DateField(null=True)),
                ('is_male', models.BooleanField()),
                ('intro', models.CharField(max_length=150)),
                ('role', models.CharField(max_length=40)),
                ('mobile', models.CharField(max_length=12)),
                ('picture_folder', models.ImageField(blank=True, default='default.png', upload_to='')),
                ('update_someone_by_email', models.CharField(max_length=405)),
                ('date_join', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='teacher_profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=40)),
                ('nickname', models.CharField(max_length=40)),
                ('birth_date', models.DateField(null=True)),
                ('is_male', models.BooleanField()),
                ('intro', models.CharField(max_length=150)),
                ('highlight_1', models.CharField(max_length=10)),
                ('highlight_2', models.CharField(max_length=10)),
                ('highlight_3', models.CharField(max_length=10)),
                ('mobile', models.CharField(max_length=12)),
                ('picture_folder', models.ImageField(blank=True, default='default.png', upload_to='')),
                ('tutor_exp_in_years', models.FloatField(default=0.0)),
                ('student_type', models.CharField(max_length=400)),
                ('subject_type', models.CharField(max_length=400)),
                ('id_cert', models.CharField(max_length=150)),
                ('education_1', models.CharField(max_length=60)),
                ('education_2', models.CharField(max_length=60)),
                ('education_3', models.CharField(max_length=60)),
                ('education_cert_1', models.CharField(max_length=150)),
                ('education_cert_2', models.CharField(max_length=150)),
                ('education_cert_3', models.CharField(max_length=150)),
                ('occupation', models.CharField(max_length=60)),
                ('company', models.CharField(max_length=60)),
                ('occupation_cert', models.CharField(max_length=150)),
                ('date_join', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
