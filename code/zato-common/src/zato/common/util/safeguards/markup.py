# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from re import compile as re_compile, DOTALL, IGNORECASE

# Zato
from zato.common.typing_ import any_
from zato.common.util.safeguards.common import add_signal, Kind_Markup, SafeguardResult
from zato.common.util.safeguards.walk import walk_strings

# ################################################################################################################################
# ################################################################################################################################

# Script and style elements are removed with everything inside them.
Script_Elements = re_compile(r'<script\b.*?</script\s*>', DOTALL | IGNORECASE)
Style_Elements  = re_compile(r'<style\b.*?</style\s*>', DOTALL | IGNORECASE)

# Event handler attributes - onclick, onerror, onload and the rest of the on* family.
Event_Handlers = re_compile(r'\s+on\w+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)', IGNORECASE)

# javascript: URIs in HTML link and source attributes.
Javascript_Attributes = re_compile(r'\s+(?:href|src)\s*=\s*(?:"javascript:[^"]*"|\'javascript:[^\']*\')', IGNORECASE)

# javascript: URIs in markdown link targets - the link text survives, the target does not.
# The target may itself contain one level of parentheses, e.g. a call like alert(1).
Markdown_Javascript_Links = re_compile(r'\[([^\]]*)\]\(\s*javascript:(?:[^()]|\([^()]*\))*\)', IGNORECASE)

# Each rule is a pattern and its replacement, applied in order - elements with their content first,
# then attributes, then markdown link targets.
Markup_Rules = (
    (Script_Elements, ''),
    (Style_Elements, ''),
    (Event_Handlers, ''),
    (Javascript_Attributes, ''),
    (Markdown_Javascript_Links, r'[\1]()'),
)

# ################################################################################################################################
# ################################################################################################################################

def sanitize_markup(value:'any_', result:'SafeguardResult') -> 'any_':
    """ Strips script and style elements with their content, event handler attributes
    and javascript: URIs from HTML and markdown in string values.
    """

    def visit(text:'str', path:'str') -> 'str':

        # Apply every rule, keeping count of what was removed - and since a removal can splice
        # new markup together out of what surrounded it, the rules run until nothing more matches.
        # Every round with matches strictly shrinks the text, so this always terminates ..
        total = 0

        while True:
            round_count = 0

            for pattern, replacement in Markup_Rules:
                text, count = pattern.subn(replacement, text)
                round_count += count

            total += round_count

            if not round_count:
                break

        # .. and record the finding - active markup in a payload is a potential sign of an attack.
        if total:
            result.markup_items_removed += total
            add_signal(result.signals, Kind_Markup, total, path)

        out = text

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################
