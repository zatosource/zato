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
def search(req) -> 'HttpResponse':
    """ Searches the LogArena with dual-path resolution, ranking, and pagination.
    """
    scope = req.POST['scope']
    input_text = req.POST['input']
    offset = int(req.POST['offset'])
    limit = int(req.POST['limit'])

    response = req.zato.client.invoke('zato.arena.logs.search', {
        'scope': scope,
        'input': input_text,
        'offset': offset,
        'limit': limit,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
