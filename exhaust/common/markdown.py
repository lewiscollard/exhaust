from commonmark.blocks import Parser
from commonmark.render.html import HtmlRenderer
from django.urls import NoReverseMatch, resolve, reverse

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

    def image(self, node, entering):
        # Does it look like a PostImage redirect link?
        if not node.destination.startswith(self.post_image_prefix):
            return super().image(node, entering)

        if not entering:
            # AFAIK this never actually happens...
            return self.lit('')
        try:
            _, _, kwargs = resolve(node.destination)
        except NoReverseMatch:  # probs should never happen
            return self.lit('')

        try:
            image = PostImage.objects.get(pk=kwargs['pk'])
        except PostImage.DoesNotExist:
            return self.lit('')
        return self.lit(
            render_multiformat_image(image.image, alt_text=node.title, max_width=1280)
        )


def markdown_to_html(text):
    parser = Parser()
    ast = parser.parse(text)
    return ExhaustHtmlRenderer().render(ast)
