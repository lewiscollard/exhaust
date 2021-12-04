from django.contrib import admin

from exhaust.common.admin import PUBLICATION_FIELDSET
from exhaust.exogram.models import Gram


@admin.register(Gram)
class GramAdmin(admin.ModelAdmin):
    fieldsets = [
        ('', {
            'fields': ['image', 'slug']
        }),
        PUBLICATION_FIELDSET,
    ]
