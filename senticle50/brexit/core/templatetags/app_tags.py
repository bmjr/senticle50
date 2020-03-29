import urllib
from urllib.parse import urlparse

from django import template

register = template.Library()


@register.simple_tag()
def query_replace(url, parameter, value):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query_params = urllib.parse.parse_qs(query)
    query_params[parameter] = value
    query_string = urllib.parse.urlencode(query_params, safe='/-',
                                          doseq=True)
    url_with_replaced_parameter = urllib.parse.urlunparse(
        (scheme, netloc, path, params, query_string, fragment))
    return url_with_replaced_parameter
