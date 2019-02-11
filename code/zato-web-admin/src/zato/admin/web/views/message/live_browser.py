# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.util.json_ import dumps

logger = logging.getLogger(__name__)

# ################################################################################################################################

@method_allowed('GET')
def index(req):

    return_data = {
        'zato_clusters': req.zato.clusters,
        'search_form':req.zato.search_form,
        'cluster_id': req.zato.cluster_id,
        'meta': True # So that the search box is shown
    }

    return TemplateResponse(req, 'zato/message/live-browser.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def get_connection_details(req):
    return HttpResponse(dumps(req.zato.client.invoke('zato.message.live-browser.get-web-admin-connection-details').data))

# ################################################################################################################################
