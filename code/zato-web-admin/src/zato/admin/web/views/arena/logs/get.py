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
def get_entry(req) -> 'HttpResponse':
    """ Retrieves a single LogArena entry by ID.
    """
    entry_id = int(req.POST['entry_id'])

    response = req.zato.client.invoke('zato.arena.logs.get', {
        'entry_id': entry_id,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
