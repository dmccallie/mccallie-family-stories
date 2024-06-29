"""
URL configuration for myapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    # path('accounts/', include('django.contrib.auth.urls')), # django built ins for authentication
    path('', include(('home.urls', 'home'), namespace='home')),  # Including the home app urls (index home page)
    path('stories/', include(('stories.urls', 'stories'), namespace='stories')),  # Including the stories app urls
    path('profiles/', include(('profiles.urls', 'profiles'), namespace='profiles')),  # Including the profiles app urls
    path("__debug__/", include("debug_toolbar.urls")),  # Including the debug toolbar urls
]
# this only generates something for DEBUG = True!
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# see here!
# https://testdriven.io/blog/django-static-files/

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

print(f"From URLs - Debug = {settings.DEBUG} and static points to {static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)}")