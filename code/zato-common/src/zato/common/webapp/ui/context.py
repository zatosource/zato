# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.templatetags.static import static

# Zato
from zato.common.webapp.ui.themes.tokens import default_theme

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

def theme(req:'HttpRequest') -> 'strdict':
    """ The theme a page is drawn in before anybody has picked one, named in
    zato.common.webapp.ui.themes.tokens and nowhere else.
    """
    out = {
        'default_theme': default_theme,
        'default_theme_css': static(f'webapp/css/themes/{default_theme}.css'),
    }
    return out

# ################################################################################################################################
# ################################################################################################################################
