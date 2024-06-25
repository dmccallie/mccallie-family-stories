from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render

from .image_utils import resize_and_reorient_image
from .models import Image, Story, Comment, fetch_nested_comments
from .forms import CommentForm, StoryForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import StoryForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.core.files.storage import default_storage

# Create your views here.
def story_test(request, id):
    # create a test context here
    context = {
        'story': {
            'title': 'Story Title inside context',
            'content': 'This is a test story.',
            'id': id
        }
    }
    return render(request, 'stories/story_test.html', context)


@login_required
def story_list(request):
    # get the published stories and order them by the published date
    # published = Story.objects.filter(published=True).order_by('-published_datetime')

    # and get unpublished stories, order them by the last updated date
    # unpublished = Story.objects.filter(published=False).order_by('-last_updated')

    all_stories = Story.objects.all().order_by('-last_updated')
    
    return render(request, 'stories/story_list.html', 
                  {'published': None, 'unpublished': None, 'all_stories': all_stories})


@login_required
@never_cache  # Decorator to prevent caching of the view
def add_story(request, story_id=None):
    old_image = None
    # are we editing an existing story? if so fetch it
    if story_id:
        story = get_object_or_404(Story, pk=story_id)
        # save the existing image if it exists
        old_image = story.image if story.image else None
        # pull the post and files data into the form mix with prior data
        form = StoryForm(request.POST or None, request.FILES or None, instance=story)

    else:
        # this is a new story, no prior data
        story = None
        form = StoryForm(request.POST or None, request.FILES or None)

    # was the form submitted?
    if request.method == 'POST':
        # print("got POST in add_story: ", request.POST, request.FILES)
        if form.is_valid(): # this pulls new data into the form
            # print("form is valid")
            story = form.save(commit=False) # pull data into the model
            story.user = request.user # augment the model

            # do we need to remove a prior image?
            # if the image was not changed, the FILES will NOT contain the image
            #   even though it is in the model
            # so we need this flag to know when to remove a prior image

            if 'remove_image' in request.POST and request.POST['remove_image'] == '1':
                print("trying to remove image from model: ", old_image, old_image.url)
                if old_image and default_storage.exists(old_image.url):
                    default_storage.delete(old_image.url)
                    # print("deleted old image at path: ", old_image.path)
                # story.image = None # remove the image from the model
                if old_image:
                    old_image.delete(save=True) # remove the image from the model????
                    # print("deleted old image from model. Now = ", story.image)
            
            # maybe we have a new image to save, but make sure there's not one there already
            # i dont think this can happen, but check anyway
            if 'image' in request.FILES:
                if old_image and default_storage.exists(old_image.url):
                    print("SURPRISED to find an old image still in storage, deleting it: ", old_image.url)
                    default_storage.delete(old_image.url)

                image = request.FILES['image']

                image_file = resize_and_reorient_image(image)

                # Add the resized image to the story model
                story.image = image_file
                
                print("image was in FILES, added to model = ", story.image)
            
            if 'action' in request.POST:
                if request.POST['action'] == 'save':
                    story.published = False
                    msg = "Your story has been saved, but not published yet."
                elif request.POST['action'] == 'publish':
                    story.published = True
                    story.published_datetime = timezone.now()
                    msg = "Your story has been published!"
            
            story.save()
            messages.success(request, msg)
            return redirect('stories:story_list')

    return render(request, 'stories/add_story.html', {'form': form })

def story_detail(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    next_story = story.get_next_story()
    previous_story = story.get_previous_story() 
    #story_form = StoryForm(instance=story) # will expand markdown to html

    # render the content to html
    content_html = md.render(story.content)

    top_level_comments = Comment.objects.filter(story=story, parent__isnull=True).order_by('-published_date')

    comment_tree = []
    for comment in top_level_comments:
        comment_tree.append({
            'comment': comment,
            'replies': fetch_nested_comments(comment)
        })    

    form = CommentForm()
    return render(request, 'stories/story_detail.html', {'story': story, 'content_html': content_html,
                            'comment_tree': comment_tree, 'form': form,
                            'next_story': next_story, 'previous_story': previous_story})

def add_comment(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.story = story
            comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment
            comment.save()
            new_comment_id = comment.id
            print("new comment id: ", new_comment_id)

            top_level_comments = Comment.objects.filter(story=story, parent__isnull=True).order_by('-published_date')
            comment_tree = []
            for comment in top_level_comments:
                comment_tree.append({
                    'comment': comment,
                    'replies': fetch_nested_comments(comment)
                })
            
            return render(request, 'stories/comment_header.html',
                    {'story': story, 'comment_tree': comment_tree, 'new_comment_id': new_comment_id,
                      'form': CommentForm()})
    
    return HttpResponseBadRequest("Invalid request method")

def upload_image(request):
    print("got image upload POST request", request.POST, request.FILES)
    # if request.method == 'POST' and request.FILES['markdown_image']:
    #     image = request.FILES['markdown_image']
    #     image_instance = Image.objects.create(image=image, uploaded_by=request.user)
    #     image_url = image_instance.image.url
    #     # image_url = default_storage.save(image.name, image)
    #     return JsonResponse({'url': image_url})
    # return JsonResponse({'error': 'Invalid request'}, status=400)

    if request.method == 'POST' and request.FILES.get('markdown_image'):
        image = request.FILES['markdown_image']
        
        image_file = resize_and_reorient_image(image)
        
        # Create an instance of your Image model
        image_instance = Image.objects.create(image=image_file, uploaded_by=request.user)
        
        # Get the URL of the saved image
        image_url = image_instance.image.url
        
        return JsonResponse({'url': image_url})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.shortcuts import render
from .markdownit import md  # Import the configured MarkdownIt instance

def markdown_to_html(request):
    # print("got md-to-html request: ", request.method, request.POST)
    html_content = ""
    if request.method == "POST":
        markdown_text = request.POST.get("content", "")
        # print("got markdown text: ", markdown_text)
        html_content = md.render(markdown_text)
    
    return render(request, 'stories/markdown_to_html.html', {'html_content': html_content})

def test_ace_editor(request):
    return render(request, 'stories/test_ace_editor.html')