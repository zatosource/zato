# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.settings.config import sbom_page_config

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    # The interpreter lives at <repo>/code/bin/python, so the SBOM directory is a sibling of the code directory ..
    bin_dir = os.path.dirname(sys.executable)
    code_dir = os.path.dirname(bin_dir)
    sbom_path = os.path.join(code_dir, '..', 'sbom', 'zato.cdx.json')
    sbom_path = os.path.abspath(sbom_path)

    # .. read the document if it exists, otherwise tell the user how to generate one.
    if os.path.exists(sbom_path):
        with open(sbom_path) as sbom_file:
            sbom_text = sbom_file.read()
    else:
        sbom_text = sbom_page_config['no_sbom_message']

    return TemplateResponse(req, 'zato/settings/sbom/index.html', {
        'page_config': sbom_page_config,
        'textarea_content': sbom_text,
    })

# ################################################################################################################################
# ################################################################################################################################
