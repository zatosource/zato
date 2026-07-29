# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.contrib.staticfiles.views import serve as serve_static_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def static_file(req:'any_', path:'str') -> 'any_':
    """ Serves one static file of a standalone Zato web application.

    These applications run without a separate web server in front of them, so the staticfiles
    finders answer directly, which is what insecure=True means here.
    """
    out = serve_static_file(req, path, insecure=True)
    return out

# ################################################################################################################################
# ################################################################################################################################
