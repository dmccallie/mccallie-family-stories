# Generated by Django 5.0.6 on 2024-07-01 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0010_alter_story_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
