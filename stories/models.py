from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from taggit.managers import TaggableManager

# a silly demo of how to do custom validations.
# displays the error message in the form if the word 'good' is not in the summary
def validate_contains_good(value):
    pass
    # if 'good' not in value:
    #     raise ValidationError(
    #         'The story must contain the word "good" in it!'
    #     )

class Story(models.Model):
    
    title = models.CharField(max_length=80)
    
    summary = models.TextField(max_length=512, validators=[validate_contains_good])  # Custom validator tested here
    
    # content will be stored as raw markdown text
    content = models.TextField(max_length=100000, blank=False, null=False)
    
    # this is the main story image, outside of any markdown images
    # this requires upload of the image which is then resized and saved to AWS S3
    # note this gets deleted in the override delete below
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    # this is a pure image url, mostly used for testing to avoid spamming S3
    # NOTE that you must use the "get_image_url" method to get the image url in templates!!
    # no need to delete, as we assume we don't own these images

    image_url = models.URLField(blank=True, null=True)

    # todo rename this to author
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    published = models.BooleanField(default=False)
    published_datetime = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    # tags
    tags = TaggableManager()


    def __str__(self):
        return self.title
    
    # see which kind of image storage and return the right URL
    def get_image_url(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        else:
            return None
        
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete() # should remove from s3 we hope
        super().delete(*args, **kwargs)

    # assuming reverse chrono list display, "next" is older, "previous" is newer
    # TODO these are wrong if we are using tag filters!
    # no longer used!!
    def get_next_story(self):
        next_story = Story.objects.filter(last_updated__gt=self.last_updated).order_by('last_updated').first()
        return next_story
    
    def get_previous_story(self):
        previous_story = Story.objects.filter(last_updated__lt=self.last_updated).order_by('-last_updated').first()
        return previous_story
    

class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'Comment:{self.content[0:25]} by {self.author} on {self.story.title[0:30]}'

def fetch_nested_comments(comment):
    nested_comments = []
    replies = comment.replies.all()

    for reply in replies:
        nested_comments.append({
            'comment': reply,
            'replies': fetch_nested_comments(reply)
        })

    return nested_comments

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Image URL {self.image.url} uploaded by {self.uploaded_by} on {self.uploaded_at}'