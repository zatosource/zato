# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import mimetypes
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The path to an image file shown instead of the Zato logo
    Env_Logo_File = 'Zato_OpenAPI_Console_Logo_File'

    # The text shown instead of the Zato logo, used when there is no logo file
    Env_Logo_Text = 'Zato_OpenAPI_Console_Logo_Text'

    # The directory with the favicon and the stylesheet that replace the built-in ones
    Env_Branding_Dir = 'Zato_OpenAPI_Console_Branding_Dir'

    Default_Branding_Dir      = '/opt/hot-deploy/openapi-console/branding'
    Default_Logo_URL          = '/static/console/zato-logo.svg'
    Default_Logo_Content_Type = 'application/octet-stream'
    Default_Favicon_URL       = '/static/console/favicon.ico'
    Default_Title             = 'Zato'

    Logo_URL           = '/openapi/console/branding/logo'
    Custom_Favicon_URL = '/openapi/console/branding/favicon.ico'

# ################################################################################################################################
# ################################################################################################################################

_branding_dir = os.environ.get(ModuleCtx.Env_Branding_Dir, ModuleCtx.Default_Branding_Dir)

# Files that users may place in the branding directory, mapped to the content types they are served with
Branding_Files = {
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

def get_logo_file() -> 'strnone':
    """ Returns the path to the custom logo file, or None if no custom logo is configured.
    """
    out = os.environ.get(ModuleCtx.Env_Logo_File)
    return out

# ################################################################################################################################

def get_logo_content_type(logo_path:'str') -> 'str':
    """ Returns the content type a logo file is served with, derived from its extension.
    """
    out, _ = mimetypes.guess_type(logo_path)

    # An extension with no registered type is served as binary data
    if out is None:
        out = ModuleCtx.Default_Logo_Content_Type

    return out

# ################################################################################################################################

def get_branding_context() -> 'stranydict':
    """ Builds the template context that describes the branding in effect - a custom logo file or text when configured,
    the Zato logo otherwise.
    """
    # Our response to produce
    out:'stranydict' = {
        'logo_url': '',
        'logo_text': '',
        'title': ModuleCtx.Default_Title,
    }

    # A logo file takes precedence over a logo text ..
    if get_logo_file():
        out['logo_url'] = ModuleCtx.Logo_URL

    # .. a text replaces the logo and names the page too ..
    elif logo_text := os.environ.get(ModuleCtx.Env_Logo_Text):
        out['logo_text'] = logo_text
        out['title'] = logo_text

    # .. and with neither, the Zato logo is shown.
    else:
        out['logo_url'] = ModuleCtx.Default_Logo_URL

    if get_branding_file_path('favicon.ico'):
        out['favicon_url'] = ModuleCtx.Custom_Favicon_URL
    else:
        out['favicon_url'] = ModuleCtx.Default_Favicon_URL

    out['has_custom_css'] = bool(get_branding_file_path('custom.css'))

    return out

# ################################################################################################################################
# ################################################################################################################################
