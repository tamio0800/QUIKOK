# Generated by Django 3.1.5 on 2021-03-16 21:12

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='article_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_id', models.IntegerField()),
                ('main_picture', models.ImageField(default='articles/default_main_picture.png', upload_to='articles/%Y/%m/%d/')),
                ('title', models.CharField(max_length=100)),
                ('content', tinymce.models.HTMLField()),
                ('category', models.CharField(max_length=100)),
                ('hashtag', models.TextField()),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('last_edited_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='author_profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_user_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('hightlight', models.CharField(max_length=20)),
                ('intro', models.TextField()),
                ('thumbnail', models.ImageField(default='authors/default_thumbnail.png', upload_to='authors/%Y/%m/%d/')),
                ('hashtag', models.TextField()),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('last_edited_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='uploaded_pictures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='articles/%Y/%m/%d/')),
                ('description', models.CharField(max_length=40)),
                ('special_tag', models.CharField(max_length=40)),
                ('created_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]