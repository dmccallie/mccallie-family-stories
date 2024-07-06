# manually created migration file to create FTS table

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0011_story_image_url'),
    ]

    operations = [
        migrations.RunSQL('''
            CREATE VIRTUAL TABLE stories_story_fts
            USING fts5(title, content, tokenize="porter");
        '''),
    ]