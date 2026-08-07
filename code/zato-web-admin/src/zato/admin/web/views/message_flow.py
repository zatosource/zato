# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    HttpRequest = HttpRequest

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'HttpRequest') -> 'TemplateResponse':
    """ The message flow page - one message's whole journey, drawn and read. The page is a shell -
    a search term is resolved and answered by the journey endpoint, and everything on the screen
    is built in the browser out of what it returns.
    """
    return TemplateResponse(req, 'zato/message-flow/index.html', {
        'cluster_id': default_cluster_id,
        'zato_clusters': True,
        'zato_template_name': 'zato/message-flow/index.html',
    })

# ################################################################################################################################

@method_allowed('GET')
def demo(req:'HttpRequest') -> 'TemplateResponse':
    """ The stage-0 demo page, temporarily back for demos - the hardcoded ADM-00004217 journey,
    everything on it coming from data in the browser. To be removed when no longer needed.
    """
    return TemplateResponse(req, 'zato/message-flow/demo.html', {
        'cluster_id': default_cluster_id,
        'zato_clusters': True,
        'zato_template_name': 'zato/message-flow/demo.html',
    })

# ################################################################################################################################
# ################################################################################################################################
