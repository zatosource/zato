# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# pygments
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer, HtmlLexer, JsonLexer, TextLexer, XmlLexer

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_Lexer_Whitelist = frozenset({
    'graphql',
    'json',
    'pytb',
})

# ################################################################################################################################
# ################################################################################################################################

def _guess_pygments_lexer(text:'str') -> 'any_':

    trimmed = text.strip()

    # Check if the text looks like JSON ..
    if (trimmed.startswith('{') and trimmed.endswith('}')) or \
       (trimmed.startswith('[') and trimmed.endswith(']')):
        try:
            json.loads(trimmed)
            return JsonLexer()
        except (ValueError, TypeError):
            pass

    # .. check if the text looks like XML or HTML ..
    if trimmed.startswith('<') and '>' in trimmed:
        text_lower = trimmed.lower()

        if '<!doctype' in text_lower:
            return HtmlLexer()

        if '<html' in text_lower:
            return HtmlLexer()

        return XmlLexer()

    # .. otherwise, let Pygments try to guess.
    try:
        out = guess_lexer(text)
    except ValueError:
        out = TextLexer()

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def highlight(request:'any_') -> 'JsonResponse':
    """ Uses Pygments to syntax-highlight the given text, auto-detecting or using an explicit lexer.
    """

    text = request.POST['text']
    if not text.strip():

        out = JsonResponse({'html': '', 'lexer': 'text'})
        return out

    # Check if an explicit lexer was requested ..
    forced_lexer_name = request.POST.get('lexer', '')

    if forced_lexer_name:
        if forced_lexer_name in _Lexer_Whitelist:
            lexer = get_lexer_by_name(forced_lexer_name)

        # .. anything not in the whitelist uses plain text.
        else:
            lexer = TextLexer()

    # .. otherwise, auto-detect.
    else:
        lexer = _guess_pygments_lexer(text)

    formatter = HtmlFormatter(nowrap=True)
    highlighted = pygments_highlight(text, lexer, formatter)
    lexer_name = type(lexer).__name__

    out = JsonResponse({'html': highlighted, 'lexer': lexer_name})
    return out

# ################################################################################################################################
# ################################################################################################################################
