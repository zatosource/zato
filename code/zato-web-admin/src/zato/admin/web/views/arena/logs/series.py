# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_series(req) -> 'HttpResponse':
    """ Returns all entries in a LogArena series.
    """
    series_id = int(req.POST['series_id'])

    response = req.zato.client.invoke('zato.arena.logs.get-series', {
        'series_id': series_id,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################

@method_allowed('POST')
def get_children(req) -> 'HttpResponse':
    """ Returns direct child entries of a LogArena entry.
    """
    entry_id = int(req.POST['entry_id'])

    response = req.zato.client.invoke('zato.arena.logs.get-children', {
        'entry_id': entry_id,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
