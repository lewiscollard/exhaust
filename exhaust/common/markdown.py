import bleach
from bs4 import BeautifulSoup
from commonmark.blocks import Parser
from commonmark.render.html import HtmlRenderer
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import resolve, reverse
from django.urls.exceptions import Resolver404

from ..posts.models import PostImage
from .images import render_multiformat_image


class ExhaustHtmlRenderer(HtmlRenderer):
    '''
    A Markdown renderer that handles images differently; it will render
    them with our nice image multi-renderer in the case where our images look
    like they are referencing a posts.models.PostImage.
    '''
    def __init__(self, options={}):  # pylint:disable=dangerous-default-value
        super().__init__(options=options)
        # Possible micro-optimisation: store our image prefix. Get an
        # imaginary image (we don't want to hard-code the path)...
        imaginary = reverse('posts:image_redirect', kwargs={'pk': 1})
        # ...and so long as our URLs always end with a forward slash,
        # everything but the last two characters will be our image prefix :)
        self.post_image_prefix = imaginary[:-2]

        # Once we enter an image node, we want to keep track of any string
        # literals that are emitted so that we have an alt text for the image
        # when we render on node exit. The alt for an image can in fact be
        # further markdown nodes, rather than plain text! But we're never
        # going to have HTML inside of a alt attribute, so we don't have to
        # worry about that case.
        #
        # The base implementation handles subnodes by only emitting the
        # closing ' />' for the tag when the node visit is exited. That's
        # unpleasant, and makes it harder to render using a template. This
        # way is much nicer.
        self.expecting_alt_text = False
        self.alt_text = ''

    def image(self, node, entering):
        # Does it look like a PostImage redirect link?
        if not node.destination.startswith(self.post_image_prefix):
            return super().image(node, entering)
        if entering:
            self.expecting_alt_text = True
            self.alt_text = ''
            return self.lit('')

        self.expecting_alt_text = False

        try:
            _, _, kwargs = resolve(node.destination)
        except Resolver404:  # probs should never happen
            return self.lit('')

        try:
            image = PostImage.objects.get(pk=kwargs['pk'])
        except PostImage.DoesNotExist:
            return self.lit('')
        return self.lit(
            render_multiformat_image(image.image, alt_text=self.alt_text, title=node.title, width=1280)
        )

    def text(self, node, entering=None):
        if not self.expecting_alt_text:
            super().text(node, entering)
            return
        # Coverage-skipped because it's unclear if that branch can ever be
        # reached by normal means.
        self.alt_text += node.literal  # pragma: no cover


def markdown_to_html(text):
    parser = Parser()
    ast = parser.parse(text)

    html = ExhaustHtmlRenderer().render(ast)
    soup = BeautifulSoup(html, 'html.parser')
    # Swap out our custom <youtube> tag for a temporary no-JS placeholder
    # (which is also an RSS placeholder). This itself will later get swapped
    # out by a Vue component.
    for tag in soup.find_all('youtube'):
        tag.replace_with(BeautifulSoup(render_to_string('youtube_video.html', {
            'id': tag.get('id')
        }), 'html.parser'))
    return bleach.clean(str(soup), **settings.BLEACH_CONFIG)
