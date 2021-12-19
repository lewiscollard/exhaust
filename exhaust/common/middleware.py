import os

from django.core.exceptions import MiddlewareNotUsed


class CSPMiddleware:
    '''
    CSPMiddleware adds the bare minimum CSP header that I need for this site;
    something like django-csp seems like overkill for what it actually does.

    For local frontend development (where the Webpack build is proxying stuff
    from 3000 -> 8000, breaking the same-origin policy), the CSP middleware
    can be disabled by setting the EXHAUST_DISABLE_CSP environment variable to
    any non-empty value.
    '''
    policy = {
        'default-src': ["'self'"],
        # Inline style attributes probably won't kill anyone.
        'style-src': ["'self'", "'unsafe-inline'"],
        # Allow YouTube embeds.
        'frame-src': ["'self'", "https://www.youtube-nocookie.com"],
        # Something deep in the guts of Vue wants to use <s>evil</s> eval.
        'script-src': ["'self'", "'unsafe-eval'"],
    }

    def __init__(self, get_response):
        if os.environ.get('EXHAUST_DISABLE_CSP', False):
            raise MiddlewareNotUsed()

        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = self.get_policy_header()
        return response

    def get_policy_header(self):
        return '; '.join([
            f'{key} {" ".join(value)}'
            for key, value in self.policy.items()
        ])
