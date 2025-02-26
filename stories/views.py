from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
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
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

    # all_stories = Story.objects.all().order_by('-last_updated')
    page_number = request.GET.get('page', 1)
    
    # tags are passed like this:  ?tags=tag1&tags=tag2&tags=tag3 so use GETLIST not get
    # be sure to pass the tags to the template so the tag filter can be displayed
    # and tags get passed to story_detail to set up prev/next links

    tags = request.GET.getlist('tags', None)
    print(f"story list request got page:{page_number} tags:{tags}")

    uid = request.GET.get('uid', None)  # filter by this user id ?uid=2
    print("story list request got uid: ", uid)

    # make sure the uid has permission to view the stories
    if uid:
        if uid == str(request.user.id) or request.user.is_superuser:
            pass
        else:
            messages.error(request, "You do not have permission to view this user's stories.")
            return redirect('stories:story_list')
    
    # build query set adding in filters as needed
    lazy_stories = Story.objects.all() # start with all
    if tags:
        lazy_stories = lazy_stories.filter(tags__name__in=tags) # filter by tags
    if uid:
        lazy_stories = lazy_stories.filter(user__id=uid) # filter by user

    lazy_stories = lazy_stories.distinct().order_by('-last_updated')
    
    # todo - support tags that have embedded commas??
    # negative sort order means largest value first, which is the most recent (largest date value)
    # if tags or uid:
    #     #paginator = Paginator(Story.objects.filter(tags__name__in=tags).distinct().order_by('-last_updated'),6)
    #     paginator = Paginator(lazy_stories, 6)
    #     print("tagged paginator count: ", paginator.count)
    # else:
    #     paginator = Paginator(Story.objects.all().order_by('-last_updated'), 6)
    paginator = Paginator(lazy_stories, 6)

    page_obj = paginator.get_page(page_number)

    # prepare the tags url extension to avoid doing it in the template language
    if tags:
        tags_url = "&".join([f"tags={tag}" for tag in tags])
    else:
        tags_url = ""

    if request.htmx:
        print("story_list got HTMX request for page, tags = ", page_number, tags)
        return render(request, 'stories/story_list_all_stories.html',
                       {'tags':tags, 'tags_url':tags_url, 'uid':uid, 'page_obj': page_obj})
    
    else:
        print("got regular request for INITIAL page = ", page_number)
        print("story_list non htmx render has tags: ", tags)
        print("story_list non htmx render has total pages, count: ", paginator.num_pages, paginator.count) 
        return render(request, 'stories/story_list.html', 
                  {'tags':tags, 'tags_url':tags_url, 'uid':uid, 'page_obj': page_obj}) # test just ret 1 page


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
            form.save_m2m() # save the many-to-many tag relationships
            messages.success(request, msg)
            return redirect('stories:story_list')

    return render(request, 'stories/add_story.html', {'form': form })

@login_required
def story_detail(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    print("story detail request = ", request.GET)

    # are we in search mode? If so, no need for tags or uid
    mode = request.GET.get('mode', None)
    if mode and mode == 'search':
        tags = None
        uid = None
        lazy_stories = None
        previous_story = None
        next_story = None   

    else:

        tags = request.GET.getlist('tags', None)
        print("story detail gets tags = ", tags)
        uid = request.GET.get('uid', None)  # filter by this user id ?uid=2
        print("story detail got uid: ", uid)

        # make sure the uid has permission to view the stories
        if uid:
            if uid == str(request.user.id) or request.user.is_superuser:
                pass
            else:
                messages.error(request, "You do not have permission to view this user's stories.")
                return redirect('stories:story_list')
            
        # build query set adding in filters as needed
        # TODO consolodate this function with story_list code?
        lazy_stories = Story.objects.all() # start with all
        if tags:
            lazy_stories = lazy_stories.filter(tags__name__in=tags) # filter by tags
        if uid:
            lazy_stories = lazy_stories.filter(user__id=uid) # filter by user

        lazy_stories = lazy_stories.distinct().order_by('-last_updated')

        # find the index of the current story
        story_index = list(lazy_stories).index(story) # order is newer (larger date) to older (smaller)
        
        # get the next and previous stories. Next means older (smaller date). Prev means newer (larger date)
        # todo is there better name than next/prev? Yes we are using Newer (prev) and Older (next)
        previous_story = lazy_stories[story_index - 1] if story_index > 0 else None
        next_story = lazy_stories[story_index + 1] if story_index < len(lazy_stories) - 1 else None

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

    # prepare the tags url extension to avoid doing it in the template language
    # each next/prev has to pass this forward to calc next/prev ids
    if tags:
        tags_url = "&".join([f"tags={tag}" for tag in tags])
    else:
        tags_url = ""

    return render(request, 'stories/story_detail.html', {'story': story, 'content_html': content_html,
                            'comment_tree': comment_tree, 'form': form, 'tags':tags, 'uid':uid,
                            'next_story': next_story, 'previous_story': previous_story, 'tags_url': tags_url,
                            'mode': mode})

@login_required
def unpublish_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    story.published = False
    story.save()
    messages.success(request, "Story unpublished.")
    if request.htmx:
        print("got htmx UNPUBLISH request for story id = ", story_id)
        return render(request, 'stories/story_list_one_story.html', {'story': story})

    return redirect('stories:story_list')

@login_required
def publish_story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    story.published = True
    story.published_datetime = timezone.now()
    story.save()
    messages.success(request, "Story published.")
    if request.htmx:
        print("got htmx PUBLISH request for story id = ", story_id)
        return render(request, 'stories/story_list_one_story.html', {'story': story})

    return redirect('stories:story_list')

@login_required
def delete_story(request, story_id):
    # coming from htmx-delete 
    print("got delete request for story id = ", story_id, request.method)
    if request.method == 'DELETE':
        # add check for user ownership or superuser
        story = get_object_or_404(Story, pk=story_id)
        if request.user == story.user or request.user.is_superuser:
            # print("ready to delete story: ", story.title, story.id)
            story.delete()
            messages.success(request, "Story deleted.")
            # print("deleted story, redirecting to story_list")
            # for htmx success delete, return empty html and status = 200
            return HttpResponse(status=200)
            # return redirect('stories:story_list')
            # return render(request, 'stories/story_list_one_story.html', {'story': story})
        else:
            return HttpResponseBadRequest("Unauthorized to delete this story", status=204) # htmx 204 = no swap

    return HttpResponseBadRequest("Invalid request method", status=204)


@login_required
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

@login_required
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

@login_required
def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT rowid, highlight(stories_story_fts, 0, '<b>', '</b>') as title,
                           highlight(stories_story_fts, 1, '<b>', '</b>') as content,
                    bm25(stories_story_fts, 10.0, 1.0) as rank
                FROM stories_story_fts
                WHERE stories_story_fts MATCH %s
                ORDER BY rank;
            ''', [query])
            results = cursor.fetchall()

    # Paginate the results
    paginator = Paginator(results, 8) # results per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # post process the results to extract snippets
    # results = (rowid, title, content, rank)
    # can't modify tuples, so create a new list of modified results
    # add username to each result
    # TODO cache the author name?
    modified_results = []
    for result in page_obj.object_list:
        # get author name for a story
        try:
            story = Story.objects.get(pk=int(result[0])) # rowid = story.id
            if story.user:
                author_name = story.user.username
            else:
                author_name = "Author unknown"
        except:
            author_name = "Author unknown"

        modified_result = (result[0], result[1], create_snippet_text(result[2], 4), result[3], author_name)
        modified_results.append(modified_result)

    # Replace the object_list in the first_page with the modified results
    page_obj.object_list = modified_results

    return render(request, 'stories/search_results.html', {
        'results': page_obj,
        'query': query,
    })

import re

# crude snippet extraction created with copilot
# needs to do extraction of n words before and after the highlighted phrase better
#  such as stopped at a period or terminator

def extract_snippets(text, N):
    # Regular expression to find all highlighted phrases between <b> tags
    highlighted_phrases = re.finditer(r'<b>(.*?)</b>', text)
    
    # merge matches together that are close together
    # if the end of match 1 is within M letters of the start of match 2, merge them
    match_spans = [matches.span() for matches in highlighted_phrases]
    
    # print("match_spans: ", match_spans)
    merged_match_spans = []
    M = 30 # characters allowed between merged matches
    cur = match_spans.pop(0) if match_spans else None 
    next = match_spans.pop(0) if match_spans else None

    if cur is None:
        return []
    
    while cur is not None and next is not None:
        if next[0] - cur[1] < M:
            cur = (cur[0], next[1])
            next = match_spans.pop(0) if match_spans else None
        else:
            merged_match_spans.append(cur)
            cur = next
            next = match_spans.pop(0) if match_spans else None
    
    merged_match_spans.append(cur)

    print("merged_match_spans: ", merged_match_spans)

    snippets = []
    for span in merged_match_spans:
        start, end = span

        # Extract N words before and after the highlighted phrase
        pre_text = text[:start].split(' ')[-N:]
        post_text = text[end:].split(' ')[:N]
        
        # construct the snippet
        snippets.append(' '.join(pre_text) + ' ' +  text[start:end] + ' ' + (' '.join(post_text)).strip())
    
    return snippets

def create_snippet_text(text, N):
    snippets = extract_snippets(text, N)
    if not snippets or len(snippets) == 0:
        return ''
    return '... | ...'.join(snippets)
