from django.contrib import admin
from django.contrib.admin.decorators import display
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from markdownx.admin import MarkdownxModelAdmin
from reversion.admin import VersionAdmin

from exhaust.common.admin import PUBLICATION_FIELDSET
from exhaust.posts.models import Attachment, Category, Post

SEO_FIELDSET = ('SEO', {
    'fields': ['seo_title', 'meta_description'],
    'classes': ['collapse'],
})


class QualityControlListFilter(admin.SimpleListFilter):
    '''
    A filter to do quality control on posts, so I can quickly find out what
    posts can have SEO improvements.
    '''
    title = 'quality control errors'

    parameter_name = 'quality_control'

    def lookups(self, request, model_admin):
        return (
            ('no_meta_description', 'No meta description'),
            ('no_categories', 'No categories'),
            ('no_alt_text', 'Image with no alt text'),
            ('no_alt_text_body', 'Images with no alt text (in body)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'no_meta_description':
            return queryset.filter(Q(meta_description=None) | Q(meta_description=''))
        if self.value() == 'no_categories':
            return queryset.filter(categories=None)
        if self.value() == 'no_alt_text':
            return queryset.exclude(image='').filter(alt_text=None)
        # This is slightly terrible. But it's much simpler than denormalising
        # this out of the body into something else on save. What we're trying
        # to find is this Markdown, which might be the _only_ way to represent
        # an image without alt text in Markdown (without using the HTML <img>
        # tag):
        #
        # ![](/some-image/)
        #
        # Those first four characters are unlikely enough _in the body of a
        # blog post written in Markdown_ that it is a good enough detection
        # method, and it's not really all that slow on a blog the size of
        # mine.
        if self.value() == 'no_alt_text_body':
            return queryset.filter(text__contains='![](')
        return queryset


@admin.register(Post)
class PostAdmin(VersionAdmin, MarkdownxModelAdmin):

    prepopulated_fields = {'slug': ['title', 'text']}

    filter_horizontal = ['categories']

    list_display = ['__str__', 'get_categories', 'online', 'date']

    list_filter = [QualityControlListFilter]

    fieldsets = [
        ('', {
            'fields': ['title', 'slug'],
        }),
        PUBLICATION_FIELDSET,
        ('Content', {
            'fields': ['text', ('image', 'alt_text'), 'link', 'categories'],
        }),
        SEO_FIELDSET,
        ('Open Graph', {
            'fields': ['opengraph_title', 'opengraph_description', 'opengraph_image'],
            'classes': ['collapse'],
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            # Set the author on original creation only.
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        # Optimisation for "get_categories" above.
        return super().get_queryset(request).prefetch_related('categories')

    @display(description='categories')
    def get_categories(self, obj):
        # Make it easier to find uncategorised articles at a glance, and add a
        # handy edit link to the categories too.
        return format_html_join(
            ', ',
            '<a href="{}">{}</a>',  # noqa:FS003
            [
                (reverse('admin:posts_category_change', args=[category.pk]), category.title)
                for category in obj.categories.all()
            ]
        )


@admin.register(Category)
class CategoryAdmin(VersionAdmin, MarkdownxModelAdmin):
    list_display = ['__str__', 'description']
    prepopulated_fields = {'slug': ['title']}

    fieldsets = [
        ('', {
            'fields': ['title', 'slug', 'description'],
        }),
        SEO_FIELDSET,
    ]


@admin.register(Attachment)
class AttachmentAdmin(VersionAdmin):
    fields = ['file']

    list_display = ['__str__', 'link']

    def link(self, obj):
        return format_html(
            '<a target="_blank" href="{}">Here</a>', obj.file.url
        )
