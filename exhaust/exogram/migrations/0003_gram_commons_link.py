# Generated by Django 4.0 on 2021-12-19 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exogram', '0002_alter_gram_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='gram',
            name='commons_link',
            field=models.URLField(blank=True, verbose_name='Wikimedia Commons link'),
        ),
    ]
