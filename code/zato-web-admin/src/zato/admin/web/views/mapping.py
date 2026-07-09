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
    """ The message mapper page - the mapping artifact itself lives in the browser's localStorage,
    so the view only renders the page shell.
    """
    return TemplateResponse(req, 'zato/mapping/index.html', {
        'cluster_id': default_cluster_id,
        'zato_clusters': True,
        'zato_template_name': 'zato/mapping/index.html',
    })

# ################################################################################################################################
# ################################################################################################################################
