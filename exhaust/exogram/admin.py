from django.contrib import admin
from django.contrib.admin.decorators import display
from django.utils.html import format_html
from reversion.admin import VersionAdmin
from sorl.thumbnail import get_thumbnail

from exhaust.common.admin import PUBLICATION_FIELDSET
from exhaust.exogram.models import Gram


@admin.register(Gram)
class GramAdmin(VersionAdmin):
    list_display = ['get_thumbnail', '__str__', 'date', 'online']
    list_display_links = ['get_thumbnail', '__str__']

    fieldsets = [
        ('', {
            'fields': ['image', 'slug', 'text'],
        }),
        PUBLICATION_FIELDSET,
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        # Having `online` set to False by default works well for blog posts,
        # in which I am often writing at length a little bit at a time. It
        # makes less sense for something that is basically an image.
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields['online'].initial = True
        return form

    @display(description='Image')
    def get_thumbnail(self, obj):
        thumbnail = get_thumbnail(obj.image, '150x150', crop='center')
        return format_html('<img src="{}" width="150" height="150">', thumbnail.url)
