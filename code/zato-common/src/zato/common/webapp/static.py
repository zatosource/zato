# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from mimetypes import guess_type

# Django
from django.contrib.staticfiles.views import serve as serve_static_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# What a file whose suffix names no type is served as.
_default_content_type = 'application/octet-stream'

# ################################################################################################################################
# ################################################################################################################################

def static_file(req:'any_', path:'str') -> 'any_':
    """ Serves one static file of a standalone Zato web application.

    These applications run without a separate web server in front of them, so the staticfiles
    finders answer directly, which is what insecure=True means here. The content type is the one
    the file's own suffix names, and browsers are told not to sniff past it, so a script is
    always served as a script and is never guessed to be anything else.
    """
    out = serve_static_file(req, path, insecure=True)

    # An answer that says the file has not changed carries neither a body nor a content type.
    if out.status_code == OK:
        content_type, _ = guess_type(path)

        # A suffix nothing knows leaves the type to be stated as plain bytes.
        if content_type is None:
            content_type = _default_content_type

        out.headers['Content-Type'] = content_type

    return out

# ################################################################################################################################
# ################################################################################################################################
