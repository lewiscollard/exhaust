from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from reversion.admin import VersionAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(VersionAdmin, MarkdownxModelAdmin):
    exclude = ['author']

    prepopulated_fields = {'slug': ['title', 'text']}

    def save_model(self, request, obj, form, change):
        if not change:
            # Set the author on original creation only.
            obj.author = request.user
        super().save_model(request, obj, form, change)
