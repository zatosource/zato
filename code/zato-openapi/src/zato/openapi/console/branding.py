# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# Users drop their own files into this directory to rebrand the console - anything not found there
# falls back to the built-in Zato branding.
_branding_dir = os.environ.get('Zato_OpenAPI_Console_Branding_Dir', '/opt/hot-deploy/openapi-console/branding')

# The default title shown when there is no custom title file
_default_title = 'API Console'

# Files that users may provide, mapped to the content types they are served with
Branding_Files = {
    'logo.png': 'image/png',
    'logo.svg': 'image/svg+xml',
    'favicon.ico': 'image/x-icon',
    'custom.css': 'text/css',
}

# ################################################################################################################################
# ################################################################################################################################

def get_branding_file_path(file_name:'str') -> 'strnone':
    """ Returns the full path to a custom branding file if the user provided one, otherwise None.
    """
    if file_name not in Branding_Files:
        return None

    full_path = os.path.join(_branding_dir, file_name)

    if os.path.exists(full_path):
        return full_path

# ################################################################################################################################

def get_branding_context() -> 'stranydict':
    """ Builds the template context that describes the branding in effect - custom files when present,
    the built-in Zato branding otherwise.
    """
    title_path = os.path.join(_branding_dir, 'title.txt')

    if os.path.exists(title_path):
        with open(title_path, 'r') as title_file:
            title = title_file.read().strip()
    else:
        title = _default_title

    logo_svg_path = get_branding_file_path('logo.svg')
    logo_png_path = get_branding_file_path('logo.png')

    # An SVG logo is preferred over a PNG one when both are present
    if logo_svg_path:
        logo_url = '/openapi/console/branding/logo.svg'
    elif logo_png_path:
        logo_url = '/openapi/console/branding/logo.png'
    else:
        logo_url = '/static/console/zato-logo.svg'

    if get_branding_file_path('favicon.ico'):
        favicon_url = '/openapi/console/branding/favicon.ico'
    else:
        favicon_url = '/static/console/favicon.ico'

    has_custom_css = bool(get_branding_file_path('custom.css'))

    out = {
        'title': title,
        'logo_url': logo_url,
        'favicon_url': favicon_url,
        'has_custom_css': has_custom_css,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
