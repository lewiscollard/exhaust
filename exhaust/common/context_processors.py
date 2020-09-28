from django.db import connection


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


def query_count(request):
    '''
    Not needed most of the time; this is my helper for too-many-DB-reads
    debugging.
    '''
    return {
        'query_count': lambda: len(connection.queries),
        'queries': lambda: connection.queries
    }
