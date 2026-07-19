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

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Static data for now - each key is a destination type, each value lists the connections
# of that type that a destination row can point to. The real implementation will read
# these from the server, one call per page open, the shape staying exactly the same.
_static_connection_list = {
    'rest': [
        {'name': 'demo.rest.billing'},
        {'name': 'demo.rest.crm'},
        {'name': 'demo.rest.payments'},
    ],
    'hl7-mllp': [
        {'name': 'demo.hl7.forward.ehr'},
        {'name': 'demo.hl7.forward.lab'},
    ],
    'hl7-fhir': [
        {'name': 'demo.fhir.ehr'},
    ],
    'smtp': [
        {'name': 'demo.smtp.notifications'},
    ],
}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_connection_list(req:'any_') -> 'HttpResponse':
    """ Returns connections that channel destinations can be pointed at, grouped by destination type.
    """
    data = dumps(_static_connection_list)
    data = data.encode('utf-8')

    out = HttpResponse(data, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
