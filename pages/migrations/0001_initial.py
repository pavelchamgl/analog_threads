# Generated by Django 4.2.3 on 2023-08-21 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1024)),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=1024, null=True)),
                ('date_posted', models.DateTimeField(auto_now_add=True)),
                ('comments_permission', models.CharField(choices=[('anyone', 'anyone'), ('your followers', 'your followers'), ('profiles you follow', 'profiles you follow'), ('mentioned only', 'mentioned only')], max_length=20)),
            ],
        ),
    ]