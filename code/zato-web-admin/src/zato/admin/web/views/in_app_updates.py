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
        'update_available': True,
        'update_version': '4.2.0',
        'download_url': 'https://zato.io/downloads/latest'
    })
