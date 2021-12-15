# Generated by Django 3.2.9 on 2021-12-05 16:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Gram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('online', models.BooleanField(default=False, help_text='Uncheck this to hide this post on the frontend.')),
                ('public_id', models.CharField(max_length=8)),
                ('slug', models.SlugField(blank=True, help_text='Use this to optimise the URL for search engines.')),
                ('image', models.ImageField(upload_to='')),
                ('text', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]