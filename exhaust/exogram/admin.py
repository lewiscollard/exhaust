from django.contrib import admin
from reversion.admin import VersionAdmin

from exhaust.common.admin import PUBLICATION_FIELDSET
from exhaust.exogram.models import Gram


@admin.register(Gram)
class GramAdmin(VersionAdmin):
    fieldsets = [
        ('', {
            'fields': ['image', 'slug', 'text'],
        }),
        PUBLICATION_FIELDSET,
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields['online'].initial = True
        return form
