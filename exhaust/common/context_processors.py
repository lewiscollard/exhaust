def settings(request):
    '''Adds "settings" to our context.

    This is safe because the only templates that this will load are written
    by me. This would obviously be a terrible thing to do if you were ever
    loading untrusted templates.
    '''

    # this import needs to be here - settings will just be a function if you
    # try and do it at the top level!
    import django.conf  # pylint:disable=import-outside-toplevel

    return {
        'settings': django.conf.settings,
    }
