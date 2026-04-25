# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def by_attr(req) -> 'HttpResponse':
    """ Direct structured search by attribute key/value pair.
    """
    key = req.POST['key']
    value = loads(req.POST['value'])

    response = req.zato.client.invoke('zato.arena.logs.by-attr', {
        'key': key,
        'value': value,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################

@method_allowed('POST')
def by_range(req) -> 'HttpResponse':
    """ Numeric range query on an integer attribute.
    """
    key = req.POST['key']
    min_val = int(req.POST['min'])
    max_val = int(req.POST['max'])

    response = req.zato.client.invoke('zato.arena.logs.by-range', {
        'key': key,
        'min': min_val,
        'max': max_val,
    })

    return HttpResponse(dumps(response.data), content_type='application/json')

# ################################################################################################################################
# ################################################################################################################################
