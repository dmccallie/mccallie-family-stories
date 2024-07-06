# manually created migration file to create FTS table

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0012_auto_create_fts_table'),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS stories_story_fts;'),
        migrations.RunSQL('''
            CREATE VIRTUAL TABLE stories_story_fts
            USING fts5(title, content, tokenize="unicode61");
        '''),
    ]