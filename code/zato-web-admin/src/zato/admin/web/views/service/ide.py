# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64decode

# Django
from django.template.response import TemplateResponse


# Pygments
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Zato
from zato.admin.web.views import  method_allowed
from zato.common.api import SourceCodeInfo
from zato.common.odb.model import Service

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

@method_allowed('GET')
def ide(req, service_name):

    service = Service(name=service_name)
    input_dict = {
        'cluster_id': req.zato.cluster_id,
        'name': service_name
    }

    response = req.zato.client.invoke('zato.service.get-source-info', input_dict, needs_exception=False)

    if response.has_data:
        service.id = response.data.service_id

        source = b64decode(response.data.source) if response.data.source else ''
        if source:
            source_html = highlight(source, PythonLexer(stripnl=False), HtmlFormatter(linenos='table'))

            service.source_info = SourceCodeInfo()
            service.source_info.source = source
            service.source_info.source_html = source_html
            service.source_info.path = response.data.source_path
            service.source_info.hash = response.data.source_hash
            service.source_info.hash_method = response.data.source_hash_method
            service.source_info.server_name = response.data.server_name

    return_data = {
        'cluster_id':req.zato.cluster_id,
        'service':service,
        }

    return TemplateResponse(req, 'zato/service/ide.html', return_data)

# ################################################################################################################################
