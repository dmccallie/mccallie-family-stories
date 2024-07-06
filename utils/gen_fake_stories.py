# run this from the django shell / cut and paste into the shell
import faker
import random

from stories.models import Story, Comment, Image
from django.contrib.auth.models import User
from django.utils import timezone

# for now, user will be just 1
user = User.objects.get(pk=1)

# create a faker object
fake = faker.Faker()

# create stories
for i in range(20):
    url = f"https://picsum.photos/seed/{i+1}/600"
    
    # randomize the published status so that 80% are published
    published = True if random.random() > 0.2 else False
    # if published set the published date and time to now
    published_datetime = timezone.now() if published else None
    
    story = Story(
        title=fake.sentence(nb_words=8),
        summary=fake.sentence(nb_words=20),
        content=fake.text(max_nb_chars=3000),
        user=user,
        image_url = url,
        published=published,
        published_datetime=published_datetime
    )
    
    story.save()
    print(f"Created fake story {story.title}")

    # # create 3 comments for each story
    # for j in range(3):
    #     comment = Comment(
    #         content=fake.text(),
    #         author=user,
    #         story=story
    #     )
    #     comment.save()


