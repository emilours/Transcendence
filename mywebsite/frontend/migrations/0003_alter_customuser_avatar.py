# Generated by Django 4.2.3 on 2024-09-14 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_game_match_alter_customuser_avatar_playermatch_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.FileField(default='img/avatars/avatar0.jpg', upload_to='img/avatars/'),
        ),
    ]