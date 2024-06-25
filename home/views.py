from django.shortcuts import render

# home page
# be sure to add the 'home' app to the INSTALLED_APPS list in config/settings.py

def index(request):
    return render(request, 'home/index.html')
    # note that the path is relative to the templates directory!!! not the app directory
    # return render(request, 'home/templates/home/index.html')

