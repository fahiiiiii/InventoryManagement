# Generated by Django 4.0.10 on 2024-12-04 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0016_alter_location_slug"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="location",
            name="slug",
        ),
    ]
