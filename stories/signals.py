from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from stories.models import Story
from django.db import connection
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain

@receiver(post_save, sender=Story)
def update_fts_table(sender, instance, **kwargs):
    print('updating fts table for story id:', instance.id)
    
    plain_renderer = MarkdownIt(renderer_cls = RendererPlain)

    with connection.cursor() as cursor:

        # delete old record if exists
        try:
            # Delete existing record if it exists
            cursor.execute('DELETE FROM stories_story_fts WHERE rowid = %s', [instance.id])
        except Exception as e:
                pass
        
        # insert new record 
        # remove markdown markup first
        plain_content = plain_renderer.render(instance.content)

        cursor.execute('''
            INSERT INTO stories_story_fts (rowid, title, content) VALUES (%s,%s,%s)
        ''', [instance.id, instance.title, plain_content])

@receiver(post_delete, sender=Story)
def delete_from_fts_table(sender, instance, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM stories_story_fts WHERE rowid=%s;', [instance.id])