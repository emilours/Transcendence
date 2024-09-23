# Generated by Django 4.2.3 on 2024-09-23 10:02

from django.db import migrations, models
import frontend.models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_customuser_is_api_authenticated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(max_length=100, validators=[frontend.models.validate_no_special_characters]),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(max_length=100, validators=[frontend.models.validate_no_special_characters]),
        ),
    ]
