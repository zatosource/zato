# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

# ################################################################################################################################
# ################################################################################################################################

def config(req):
    return_data = {
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/monitoring/config.html', return_data)

# ################################################################################################################################
# ################################################################################################################################
