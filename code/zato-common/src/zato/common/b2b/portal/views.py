# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT

# Django
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.static import serve

# Zato
from zato.common.b2b.portal.config import Local_Organization, Static_Dir, Static_URL
from zato.common.b2b.portal.sample.sections import Navigation, Sections
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from django.http.response import HttpResponseBase
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

def _find_item(section:'anydict', item_id:'str') -> 'anydict':

    for item in section['items']:
        if item['id'] == item_id:
            out = item
            break
    else:
        raise Http404(f'No item `{item_id}` in `{section["slug"]}`')

    return out

# ################################################################################################################################

def _active_tab(req:'HttpRequest', item:'anydict') -> 'str':
    """ The tab the address names, or the first tab of the item when the address names none of its tabs.
    """
    keys = [each['key'] for each in item['tabs']]
    out = keys[0]

    if 'tab' in req.GET:
        requested = cast_('str', req.GET['tab'])
        if requested in keys:
            out = requested

    return out

# ################################################################################################################################

def _navigation(section_slug:'str') -> 'anylist':

    out:'anylist' = []

    for entry in Navigation:
        entry = dict(entry)
        entry['is_active'] = entry['slug'] == section_slug
        out.append(entry)

    return out

# ################################################################################################################################
# ################################################################################################################################

def section_view(req:'HttpRequest', section_slug:'str') -> 'HttpResponse':
    """ One listing of the portal, the details of one of its items, or the wizard that adds a new item to it.
    """
    section = Sections[section_slug]
    is_new = 'new' in req.GET

    if is_new:
        if not section['wizard']:
            raise Http404(f'No wizard in `{section_slug}`')
        item = None
        active_tab = ''

    elif 'id' in req.GET:
        item_id = cast_('str', req.GET['id'])
        item = _find_item(section, item_id)
        active_tab = _active_tab(req, item)

    else:
        item = None
        active_tab = ''

    context = {
        'organization': Local_Organization,
        'navigation': _navigation(section_slug),
        'section': section,
        'item': item,
        'active_tab': active_tab,
        'is_new': is_new,
        'static_url': Static_URL,
    }

    out = render(req, 'portal/section.html', context)
    return out

# ################################################################################################################################

def asset_view(req:'HttpRequest', path:'str') -> 'HttpResponseBase':
    """ A stylesheet, a script or a font of the portal, which the browser revalidates on each use.
    """
    out = serve(req, path, document_root=Static_Dir)
    out['Cache-Control'] = 'no-cache'
    return out

# ################################################################################################################################

def empty_view(req:'HttpRequest') -> 'HttpResponse':
    _ = req
    out = HttpResponse(status=NO_CONTENT)
    return out

# ################################################################################################################################
# ################################################################################################################################
