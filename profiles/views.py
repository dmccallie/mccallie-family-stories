from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.core.files.storage import default_storage

# Create your views here.from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from stories.image_utils import resize_and_reorient_image
from .forms import ProfileForm
from .models import Profile

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profiles:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profiles/profile.html', {'form': form})

@login_required
def update_profile(request):
    # in theory profiles get created when user is created so we don't have to creat one
    # but we should check if the user is trying to update their own profile
    # if request.user.id != user_id:
    #     print("User is not updating their own profile!")
    #     # todo add override for admin user?
    #     return HttpResponseRedirect('/')
    user_id = request.user.id
    
    # fetch the profile
    profile = get_object_or_404(Profile, user__id=user_id)

    # if there is a profile image, note it in case it needs to be deleted
    # this happens when user changes the image or removes it
    old_image = profile.profile_image if profile.profile_image else None
    
    if request.method == 'POST':
        
        # pull the form data into the form mix with prior data
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            
            new_profile = form.save(commit=False)
            
            # do we need to delete former image?
            if 'remove_image' in request.POST and request.POST['remove_image'] == '1':
                
                if old_image and default_storage.exists(old_image.url):
                    default_storage.delete(old_image.url)
                    print("deleted default storage for profile old image at path: ", old_image.url)
                
                if old_image:
                    old_image.delete(save=True)
                    print("deleted old image from profile model")
            
            # new image to save?
            if 'profile_image' in request.FILES:
                
                new_profile_image = request.FILES['profile_image']

                # todo consider smaller max size for profile images
                image_file = resize_and_reorient_image(new_profile_image)

                # add resized image to the model
                new_profile.profile_image = image_file
                print(f"Profile Image {image_file} ready to be saved")
            
            new_profile.save()
            return redirect('profiles:update_profile') # todo ????
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'profiles/profile.html', {'form': form})

@login_required
def delete_profile_image(request):
    if request.method == 'POST':
        request.user.profile.profile_image.delete()
        return redirect('profiles:profile')
    return HttpResponseRedirect('/')


@login_required
def profile_detail(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    
    # htmx case uses custom template
    if request.headers.get('HX-Request'):
        return render(request, 'profiles/profile_detail_hx.html',
                      { 'profile':profile } )
    # default case
    return render(request, 'profiles/profile_detail.html',
                   { 'profile':profile } )