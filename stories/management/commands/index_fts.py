# stories/management/commands/index_fts.py

# stories/management/commands/index_fts.py

from django.core.management.base import BaseCommand
from django.db import connection
from stories.models import Story

class Command(BaseCommand):
    help = 'Index existing stories into the FTS table'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            for story in Story.objects.all():
            
                print("ready to index story id: ", story.id)
                try:
                    # Delete existing record if it exists
                    cursor.execute('DELETE FROM stories_story_fts WHERE rowid = %s', [story.id])
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to delete existing index for story id {story.id}: {e}'))
                    
                try:
                    # Insert new record
                    # fake the content for now 

                    cursor.execute('''
                        INSERT INTO stories_story_fts (rowid, title, content) VALUES (%s, %s, %s)
                    ''', [story.id, story.title, story.content])
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully indexed story id {story.id}'))
                
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to index story id {story.id}: {e}'))
                    print(f"Story ID: {story.id}, Title: {story.title}, Content: {story.content[0:100]}")


