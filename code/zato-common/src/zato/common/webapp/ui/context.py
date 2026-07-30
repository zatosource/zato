# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Django
from django.templatetags.static import static

# Zato
from zato.common.webapp.ui.themes.tokens import default_theme

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

_ui_dir = os.path.dirname(os.path.abspath(__file__))
_themes_dir = os.path.join(_ui_dir, 'static', 'webapp', 'css', 'themes')

# ################################################################################################################################

def _shipped_themes() -> 'strlist':
    """ The themes a page can really be drawn in, one generated css file each.
    """
    out = sorted(os.path.splitext(name)[0] for name in os.listdir(_themes_dir))
    return out

# ################################################################################################################################

_theme_slugs = _shipped_themes()

# ################################################################################################################################

def theme(req:'HttpRequest') -> 'strdict':
    """ The theme a page is drawn in before anybody has picked one, named in
    zato.common.webapp.ui.themes.tokens and nowhere else, and the themes a
    picked one is checked against.
    """
    out = {
        'default_theme': default_theme,
        'default_theme_css': static(f'webapp/css/themes/{default_theme}.css'),
        'theme_slugs_json': json.dumps(_theme_slugs),
    }
    return out

# ################################################################################################################################
# ################################################################################################################################
