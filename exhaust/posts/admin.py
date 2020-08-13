from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html_join
from markdownx.admin import MarkdownxModelAdmin
from reversion.admin import VersionAdmin

from .models import Category, Post


@admin.register(Post)
class PostAdmin(VersionAdmin, MarkdownxModelAdmin):

    prepopulated_fields = {'slug': ['title', 'text']}

    filter_horizontal = ['categories']

    list_display = ['__str__', 'get_categories', 'online', 'date']

    fieldsets = [
        ('', {
            'fields': ['title', 'date', 'slug', 'online'],
        }),
        ('Content', {
            'fields': ['text', ('image', 'alt_text'), 'categories'],
        }),
        ('SEO', {
            'fields': ['seo_title', 'meta_description'],
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

    def get_categories(self, obj):
        # Make it easier to find uncategorised articles at a glance, and add a
        # handy edit link to the categories too.
        return format_html_join(
            ',',
            '<a href="{}">{}</a>',
            [
                (reverse('admin:posts_category_change', args=[category.pk]), category.title)
                for category in obj.categories.all()
            ]
        )
    get_categories.short_description = 'Categories'


@admin.register(Category)
class CategoryAdmin(VersionAdmin, MarkdownxModelAdmin):
    prepopulated_fields = {'slug': ['title']}
