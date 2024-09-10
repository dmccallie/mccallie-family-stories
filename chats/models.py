from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    topic = models.CharField(max_length=255) # what is the chat about?
    starter = models.ForeignKey(User, on_delete=models.CASCADE) # the user that started the chat
    # maybe add more info about the topic?  A starter message?
    # message = models.TextField()
    # do we want an image? Maybe later
    published = models.BooleanField(default=False) # is chat visible to all users?
    published_datetime = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # maybe add tags later
    # tags = TaggableManager()

    def __str__(self):
        return self.topic

# contributions to the topic are called Blurbs
# blurbs can be added by any user, using markdown at some point, and can contain images or uploads
# blurbs are not threaded, but are displayed in order of creation
# we might add links to allow "replying" to a blurb, in future

class Blurb(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE) # which chat is this blurb part of?
    author = models.ForeignKey(User, on_delete=models.CASCADE) # who is the user that added the blurb?
    
    # plan to have contest in markdown
    content = models.TextField(max_length=5000, blank=False, null=False) # the actual content of the blurb
    # do we want an image? Maybe later
    published = models.BooleanField(default=False) # is blurb visible to all users?
    # order will be by creation dttm, not publish dttm
    created_datetime = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        show_len = max(100, len(self.content))
        return f"Blurb from {self.author}: {self.content[0:show_len]}"
    