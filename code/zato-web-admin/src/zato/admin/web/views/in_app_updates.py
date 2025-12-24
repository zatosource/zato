# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.updates import find_file_in_parents

@method_allowed('GET')
def index(req):
    current_version = '4.1.0'
    
    zato_path = os.path.sep.join(['code', 'bin', 'zato'])
    zato_binary = find_file_in_parents(zato_path)
    
    if zato_binary:
        try:
            result = subprocess.run(
                [zato_binary, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                current_version = result.stdout.strip()
        except Exception:
            pass
    
    return TemplateResponse(req, 'zato/in-app-updates/index.html', {
        'current_version': current_version,
        'latest_version': '4.2.0'
    })
