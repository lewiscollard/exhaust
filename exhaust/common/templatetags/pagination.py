from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_url(context, page_number):
    '''
    Returns a URL for the given page number.

    It will not append a page number when the requested page is 1 (because
    that's the same as doing it with no paginator page). It will also preserve
    any query strings that are present.
    '''
    request = context['request']
    url = request.path
    params = request.GET.copy()
    if page_number == 1:
        params.pop(context.get('pagination_key', 'page'), None)
    else:
        params[context.get('pagination_key', 'page')] = page_number
    if params:
        url += '?{}'.format(params.urlencode())
    return url
