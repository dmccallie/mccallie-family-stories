from django.shortcuts import render
from django.conf import settings

# home page
# be sure to add the 'home' app to the INSTALLED_APPS list in config/settings.py

def index(request):
    tags = settings.STANDARD_TAGS
    return render(request, 'home/index.html', {'tags': tags})
    # note that the path is relative to the templates directory!!! not the app directory
    # return render(request, 'home/templates/home/index.html')

