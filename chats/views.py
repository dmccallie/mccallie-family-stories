from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from chats.models import Chat, Blurb
from chats.forms import ChatForm, BlurbForm

@login_required
def chat_list(request):
    # chats = { 'chats': get_list_or_404(Chat, user=request.user) }
    chats = { 'chats': [] }
    return render(request, 'chats/chat_list.html', chats)

@login_required
# start a "new chat"
def add_chat(request, chat_id=None):
    # POST means we are submitting the form
    if request.method == 'POST':
        # Handling the form submission
        chat_form = ChatForm(request.POST)
        blurb_form = BlurbForm(request.POST)
        
        if chat_form.is_valid():
            # Save the Chat
            chat = chat_form.save(commit=False)
            chat.starter = request.user  # Assign the current user as the starter of the chat
            chat.save()
            
            # Optionally handle the Blurb if the form is valid and not empty
            if blurb_form.is_valid() and blurb_form.cleaned_data.get('content'):
                blurb = blurb_form.save(commit=False)
                blurb.chat = chat  # Assign the blurb to the newly created chat
                blurb.author = request.user  # Assign the current user as the author of the blurb    
                blurb.save()

            # Redirect to the chat's detail page (or any other page)
            return redirect('chats:chat_detail', chat_id=chat.id)

    else:
        # Initial GET request to render the empty forms
        chat_form = ChatForm()
        blurb_form = BlurbForm()

    return render(request, 'chats/add_chat.html', {
        'chat_form': chat_form,
        'blurb_form': blurb_form,
    })



# @login_required
def add_blurb(request, chat_id):
    pass

@login_required
def chat_detail(request, chat_id):
    
    #if method is POST, then we are submitting a new blurb to the chat
    if request.method == 'POST':
        # Handling the form submission
        blurb_form = BlurbForm(request.POST)
        
        if blurb_form.is_valid():
            # Save the Blurb
            blurb = blurb_form.save(commit=False)
            blurb.chat = get_object_or_404(Chat, id=chat_id)
            blurb.author = request.user
            blurb.save()

        # redirect to chat detail page (that's us, but uses GET not POST to avoid resubmission)
        return redirect('chats:chat_detail', chat_id=chat_id)
    
    # otherwise this is a GET request, so we are just viewing the chat
    # Get the Chat instance
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Get all blurbs related to this chat, ordered by creation time (ascending)
    blurbs = Blurb.objects.filter(chat=chat).order_by('created_datetime') 

    blurb_form = BlurbForm()
    
    return render(request, 'chats/chat_detail.html', {
        'chat': chat,
        'blurbs': blurbs,
        'blurb_form': blurb_form,
    })