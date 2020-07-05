from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from reversion.admin import VersionAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(VersionAdmin, MarkdownxModelAdmin):

    prepopulated_fields = {'slug': ['title', 'text']}

    fieldsets = [
        ('', {
            'fields': ['title', 'slug', 'online'],
        }),
        ('Content', {
            'fields': ['text', ('image', 'alt_text')],
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
