# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST
from logging import getLogger

# Django
from django.http import JsonResponse

# Pygments
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

formatter = HtmlFormatter(nowrap=True, cssclass='highlight')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def highlight_code(req) -> 'JsonResponse':
    """ Highlights code using Pygments.
    """
    try:
        body = loads(req.body)
    except Exception as e:
        logger.warning('Invalid request body: %s', e)
        return JsonResponse({'error': 'Invalid request body'}, status=BAD_REQUEST)

    code = body.get('code', '')
    language = body.get('language', '')

    if not code:
        return JsonResponse({'error': 'Code is required'}, status=BAD_REQUEST)

    try:
        if language:
            lexer = get_lexer_by_name(language, stripall=True)
        else:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                lexer = get_lexer_by_name('python', stripall=True)
    except ClassNotFound:
        lexer = get_lexer_by_name('text', stripall=True)

    try:
        highlighted = highlight(code, lexer, formatter)
    except Exception:
        highlighted = code

    out = {
        'html': highlighted
    }

    return JsonResponse(out)

# ################################################################################################################################

def get_pygments_css(req) -> 'JsonResponse':
    """ Returns Pygments CSS for syntax highlighting.
    """
    css = HtmlFormatter(style='monokai').get_style_defs('code.highlighted')

    out = {
        'css': css
    }

    return JsonResponse(out)

# ################################################################################################################################
# ################################################################################################################################
