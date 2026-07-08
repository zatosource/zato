# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed

@method_allowed('POST')
def check_attr_exists(req):
    entity_type = req.POST['entity_type']
    attr_name = req.POST['attr_name']
    value = req.POST['value']

    # An optional scoping filter, present only for checks that are unique within a sub-group
    # (e.g. a username is unique per sec_type rather than globally) ..
    filter_name = req.POST.get('filter_name', '')
    filter_value = req.POST.get('filter_value', '')

    # Optional context for channel url_path checks - the server compares these
    # the same way the create service does in ensure_channel_is_unique ..
    soap_action = req.POST.get('soap_action', '')
    method = req.POST.get('method', '')
    http_accept = req.POST.get('http_accept', '')

    response = req.zato.client.invoke('zato.server.invoker', {
        'func_name': 'check_attr_exists',
        'entity_type': entity_type,
        'attr_name': attr_name,
        'value': value,
        'filter_name': filter_name,
        'filter_value': filter_value,
        'soap_action': soap_action,
        'method': method,
        'http_accept': http_accept,
    })
    data = response.data
    if isinstance(data, dict):
        data = dumps(data)
    else:
        data = str(data)
    return HttpResponse(data, content_type='application/json')
