from django.forms import ModelForm

from .models import PostImage


class ImageUploadForm(ModelForm):
    class Meta:
        fields = ['image']
        model = PostImage
