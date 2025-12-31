# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

# ################################################################################################################################
# ################################################################################################################################

def health(req):
    return_data = {
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/monitoring/wizard/health.html', return_data)

# ################################################################################################################################
# ################################################################################################################################
