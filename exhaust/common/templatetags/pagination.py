from copy import deepcopy

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_url(context, page_number):
    '''
    Returns a URL for the given page number, assuming that

    1) you are trying to paginate for the current view

    2) the view name for the paginated version is the same as the name of the
       current view

    3) the view takes a 'page' kwarg (Django generic list views do)

    If the page number is 1, then it won't pass the 'page' kwarg at all,
    because it is not necessary and could result in duplicate URLs.
    '''
    resolver_match = context['request'].resolver_match
    view_name = resolver_match.url_name
    namespace = resolver_match.namespace
    view_args = resolver_match.args
    view_kwargs = deepcopy(resolver_match.kwargs)

    if 'page' in view_kwargs:
        del view_kwargs['page']

    if not page_number == 1:
        view_kwargs['page'] = page_number

    return reverse(f'{namespace}:{view_name}', args=view_args, kwargs=view_kwargs)
