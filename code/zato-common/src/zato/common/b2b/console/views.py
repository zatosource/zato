# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import Http404
from django.shortcuts import render

# Zato
from zato.common.b2b.console.data import sections
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest, HttpResponse
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_sections_by_slug = {section['slug']: section for section in sections}

# ################################################################################################################################
# ################################################################################################################################

def _find_item(section:'anydict', item_id:'str') -> 'anydict':

    for item in section['items']:
        if item['id'] == item_id:
            return item

    raise Http404(f'No item `{item_id}` in `{section["slug"]}`')

# ################################################################################################################################
# ################################################################################################################################

def console_view(req:'HttpRequest', section_slug:'str') -> 'HttpResponse':
    """ One section of the console - its listing, and next to it either the selected item or the create form.
    """
    if not (section := _sections_by_slug.get(section_slug)):
        raise Http404(f'No section `{section_slug}`')

    is_new = 'new' in req.GET

    if item_id := cast_('str', req.GET.get('id', '')):
        item = _find_item(section, item_id)
    else:
        item = section['items'][0]

    context = {
        'sections': sections,
        'section': section,
        'item': item,
        'is_new': is_new,
    }

    out = render(req, 'b2b-console/console.html', context)
    return out

# ################################################################################################################################
# ################################################################################################################################
