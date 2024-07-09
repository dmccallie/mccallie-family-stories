# some context that needs to be available to all pages, via the _base.html template
# maybe there's a simpler way but this could be useful for other things too
# remember to add this to the TEMPLATES context_processors list

from django.conf import settings

def base_context(request):
    # Fetching some settings from settings.py
    standard_tags = getattr(settings, 'STANDARD_TAGS', [])
    return {
        'standard_tags': standard_tags,
    }
