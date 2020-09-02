from django import template

register = template.Library()


@register.inclusion_tag('posts/includes/status.html')
def post_status_html(post):
    if not post.status_text == 'Published':
        text = post.status_text
    else:
        text = ''
    return {
        'text': text
    }
