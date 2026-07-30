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

# Where the blue Zato icon on a white background lives among the static files
Favicon_Path = 'webapp/assets/favicon.ico'

# ################################################################################################################################
# ################################################################################################################################

def static_file(req:'any_', path:'str') -> 'any_':
    """ Serves one static file of a standalone Zato web application.

    These applications run without a separate web server in front of them, so the staticfiles
    finders answer directly, which is what insecure=True means here.

    The response carries no-cache, which is an instruction to ask every time rather than not to
    store - the file's timestamp still answers most of those questions with 304. Without it a
    browser is free to reuse a script or a stylesheet it already holds, and an edited asset then
    reaches the screen only after the cache is bypassed by hand.
    """
    out = serve_static_file(req, path, insecure=True)
    out['Cache-Control'] = 'no-cache'
    return out

# ################################################################################################################################
# ################################################################################################################################
