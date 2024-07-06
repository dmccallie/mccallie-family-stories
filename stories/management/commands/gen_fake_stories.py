
import faker
import random

from django.core.management.base import BaseCommand
from stories.models import Story, Comment, Image
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    help = 'Index existing stories into the FTS table'

    def handle(self, *args, **kwargs):

        # for now, user will be just 1
        user = User.objects.get(pk=1)

        # create a faker object
        fake = faker.Faker()

        # create stories
        for i in range(20):
            url = f"https://picsum.photos/seed/{i+1}/600"
            
            # randomize the published status so that 90% are published
            published = True if random.random() > 0.1 else False
            # if published set the published date and time to now
            published_datetime = timezone.now() if published else None

            # random add two tags from settings.STANDARD_TAGS
            tagset = set()
            tagset.add(random.choice(settings.STANDARD_TAGS))
            tagset.add(random.choice(settings.STANDARD_TAGS))
            tags = list(tagset)
            
            story = Story.objects.create(
                title=fake.sentence(nb_words=8),
                summary=fake.sentence(nb_words=20),
                content=fake.text(max_nb_chars=3000),
                user=user,
                image_url = url,
                published=published,
                published_datetime=published_datetime
            )
            
            story.tags.add(*tags)

            print(f"Created fake story {story.title} with tags {tags} and published {published}")

            # # create 3 comments for each story
            # for j in range(3):
            #     comment = Comment(
            #         content=fake.text(),
            #         author=user,
            #         story=story
            #     )
            #     comment.save()


