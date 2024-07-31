from django import template
from urllib.parse import urlencode

register = template.Library()


# simple filter to assemble a URL with query parameters
# handles the ? vs & logic

@register.simple_tag
def url_add_query_params(base_url, **params):
    
    # Filter out parameters with None values
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    # doseq=True allows for multiple values for the same key
    query_string = urlencode(filtered_params, doseq=True) 

    return f"{base_url}?{query_string}" if query_string else base_url
