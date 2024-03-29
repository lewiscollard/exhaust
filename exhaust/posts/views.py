from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView, RedirectView

from exhaust.common.views import PublishedModelViewMixin
from exhaust.posts.forms import ImageUploadForm
from exhaust.posts.models import Category, Post, PostImage


class PostViewMixin(PublishedModelViewMixin):
    model = Post


class PostListView(PostViewMixin, ListView):
    paginate_by = 8

    def get(self, request, *args, **kwargs):
        # For old pagination compatibility: redirect '?page=1' to '/page/1/'
        if 'page' in request.GET:
            kwargs['page'] = request.GET['page']
            return redirect(
                reverse(f'{request.resolver_match.namespace}:{request.resolver_match.url_name}', kwargs=kwargs),
                permanent=True,
            )
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Prefetch categories so we have a single query for loading categories,
        # rather than N queries for N posts.
        queryset = super().get_queryset().prefetch_related('categories')

        if self.kwargs.get('category'):
            queryset = queryset.filter(categories__slug=self.kwargs['category']).distinct()
        return queryset


class PostCategoryListView(PostListView):
    template_name = 'posts/post_category_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['object'] = get_object_or_404(Category, slug=self.kwargs['category'])
        return context


class PostDetailView(PostViewMixin, DetailView):
    def get(self, request, *args, **kwargs):
        # If the path does not match the canonical URL of the post, then
        # redirect. This handles two situations:
        #
        # 1) that we create a post, add a slug later. We could end up with
        #    two possible URLs for it, e.g. /post/42/ and /post/42-some-slug/,
        #    which we don't really want.
        #
        # 2) that some genius decides to change the second URL above to
        #    /post/42-something-unpleasant/ and it looks like we created that
        #    URL.

        obj = self.get_object()

        if not request.path == obj.get_absolute_url():
            return redirect(obj.get_absolute_url(), permanent=True)
        return super().get(request, args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detail_page'] = True
        return context

    def get_object(self, queryset=None):
        # Re-implementation of the Django default get_object, which cannot
        # handle two arguments when one of the arguments is not `pk`.
        try:
            return self.get_queryset().get(identifier=self.kwargs['identifier'])
        except self.model.DoesNotExist:
            raise Http404(f'{self.model._meta.verbose_name.capitalize()} not found.')  # pylint:disable=raise-missing-from


class BasePostFeedView(PostListView):
    '''An RSS feed for all posts.

    This would, in an idea world, work with Django's feed module. But that API
    is a mess for the common use case of generating a human-readable RSS feed
    to plug in to a reader, as well as looking absolutely nothing like any of
    Django's generic views.
    '''

    template_name = 'posts/post_feed.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # allow previewing in DEBUG mode
        if settings.DEBUG and 'debug' in request.GET:
            response['Content-Type'] = 'text/plain; charset=utf-8'
        else:
            response['Content-Type'] = 'application/rss+xml; charset=utf-8'

        return response


class PostFeedView(BasePostFeedView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['feed_title'] = settings.SITE_NAME
        return context


class PostCategoryFeedView(BasePostFeedView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        category = get_object_or_404(Category, slug=self.kwargs['category'])
        context['feed_title'] = f'{category} - {settings.SITE_NAME}'
        return context


class ImageRedirectView(LoginRequiredMixin, RedirectView):
    '''
    A view that redirects to an image, based on its ID. This uses
    LoginRequiredMixin as it is *only* intended to be used for previewing
    Markdown in the admin. When said markdown is rendered on the front end
    the image will be rendered via a different means (extract the PK from the
    URL, then render it in a bunch of sizes). We don't want to do that in the
    admin because it's quite expensive the first time.
    '''
    def get_redirect_url(self, *args, **kwargs):
        return PostImage.objects.get(pk=self.kwargs['pk']).image.url


class ImageUploadView(LoginRequiredMixin, FormView):
    '''
    A replacement for MarkdownX's upload view. Rather than saving it directly
    to storage, it will store it to the PostImage model.
    '''
    form_class = ImageUploadForm

    def form_invalid(self, form):
        response = JsonResponse({
            'image': 'Image missing or broken.',
        })
        response.status_code = 400
        return response

    def form_valid(self, form):
        form.save()
        return JsonResponse({
            'image_code': f'![]({form.instance.get_absolute_url()})'
        })
