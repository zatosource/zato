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
    response = req.zato.client.invoke('zato.server.invoker', {
        'func_name': 'check_attr_exists',
        'entity_type': entity_type,
        'attr_name': attr_name,
        'value': value,
    })
    return HttpResponse(response.data, content_type='application/json')
