# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def import_demo_config(req:'any_') -> 'HttpResponse':
    """ Runs the HL7 demo import on the server - the demo connections, the alert
    rules, the seeded week of audit history and the live traffic burst.

    It creates all of that, so it is a POST and is covered by the cross-site request
    checks that a GET would sit outside of.
    """
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'import_demo_hl7'})

    out = HttpResponse()
    out.content = str(response.data)

    return out

# ################################################################################################################################
# ################################################################################################################################
