class PublishedModelViewMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        # Allow staff users (me) to view unpublished things to see what they
        # will look like on the front end.
        if not self.request.user.is_staff:
            queryset = queryset.select_published()
        return queryset
