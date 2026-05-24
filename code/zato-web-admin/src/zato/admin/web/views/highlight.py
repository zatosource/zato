# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pygments
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, HtmlLexer, JsonLexer, TextLexer, XmlLexer

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.content_type import get_content_type

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_Lexer_Whitelist = frozenset({
    'graphql',
    'json',
    'pytb',
})

# ################################################################################################################################
# ################################################################################################################################

_mime_to_pygments_lexer = {
    'application/json':      JsonLexer,
    'text/json':             JsonLexer,
    'application/geo+json':  JsonLexer,
    'application/ld+json':   JsonLexer,
    'application/vnd.api+json': JsonLexer,
    'text/xml':              XmlLexer,
    'application/xml':       XmlLexer,
    'application/soap+xml':  XmlLexer,
    'application/rss+xml':   XmlLexer,
    'application/atom+xml':  XmlLexer,
    'image/svg+xml':         XmlLexer,
    'text/html':             HtmlLexer,
    'application/xhtml+xml': HtmlLexer,
}

# ################################################################################################################################
# ################################################################################################################################

def get_pygments_lexer(content_type:'str') -> 'any_':
    if lexer_class := _mime_to_pygments_lexer.get(content_type):
        out = lexer_class()
    else:
        out = TextLexer()

    return out

# ################################################################################################################################
# ################################################################################################################################

_nowrap_formatter = HtmlFormatter(nowrap=True)

# ################################################################################################################################
# ################################################################################################################################

def highlight_data_previews(rows:'anylist') -> 'None':
    """ Adds a 'data_preview_highlighted' key to each row dict
    with Pygments-highlighted HTML of the data_preview field.
    """
    for row in rows:
        text = row['data_preview']
        if text.strip():
            content_type = get_content_type(text)
            lexer = get_pygments_lexer(content_type)
            row['data_preview_highlighted'] = pygments_highlight(text, lexer, _nowrap_formatter)
        else:
            row['data_preview_highlighted'] = text

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
    if forced_lexer_name := request.POST.get('lexer'):
        if forced_lexer_name in _Lexer_Whitelist:
            lexer = get_lexer_by_name(forced_lexer_name)

        # .. anything not in the whitelist uses plain text.
        else:
            lexer = TextLexer()

    # .. otherwise, auto-detect.
    else:
        content_type = get_content_type(text)
        lexer = get_pygments_lexer(content_type)

    formatter = HtmlFormatter(nowrap=True)
    highlighted = pygments_highlight(text, lexer, formatter)
    lexer_name = type(lexer).__name__

    out = JsonResponse({'html': highlighted, 'lexer': lexer_name})
    return out

# ################################################################################################################################
# ################################################################################################################################
