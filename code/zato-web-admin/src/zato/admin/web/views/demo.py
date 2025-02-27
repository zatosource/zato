# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

def index(req):
    template_name = 'zato/demo/index.html'
    return_data = {}
    return TemplateResponse(req, template_name, return_data)
