# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from django.template.response import TemplateResponse

from zato.admin.web.views import method_allowed

@method_allowed('GET')
def index(req):
    return TemplateResponse(req, 'zato/in-app-updates/index.html', {
        'current_version': '4.1.0',
        'latest_version': '4.2.0'
    })
