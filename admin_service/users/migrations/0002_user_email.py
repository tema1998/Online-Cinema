# Generated by Django 5.0.6 on 2024-10-31 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(default=0, max_length=255, unique=True, verbose_name='Email'),
            preserve_default=False,
        ),
    ]