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
def by_text(req) -> 'HttpResponse':
    """ Full-text search across all string attributes.
    """
    text = req.POST['text']

    response = req.zato.client.invoke('zato.arena.logs.by-text', {
        'text': text,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
