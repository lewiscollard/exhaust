# Generated by Django 3.2.9 on 2021-12-05 18:01

import markdownx.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exogram', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gram',
            name='text',
            field=markdownx.models.MarkdownxField(blank=True, null=True),
        ),
    ]