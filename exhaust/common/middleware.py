class CSPMiddleware:
    '''
    CSPMiddleware adds the bare minimum CSP header that I need for this site;
    something like django-csp seems like overkill for what it actually does.
    '''
    policy = {
        'default-src': ["'self'"],
        # Inline style attributes probably won't kill anyone.
        'style-src': ["'self'", "'unsafe-inline'"],
        # Allow YouTube embeds.
        'frame-src': ["'self'", "https://www.youtube-nocookie.com"],
    }

    def __init__(self, get_response):
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
