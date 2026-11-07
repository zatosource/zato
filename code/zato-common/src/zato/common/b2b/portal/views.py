# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT

# Django
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.static import serve

# Zato
from zato.common.b2b.portal.config import Local_Organization, Logo_Env_Variable, Logo_Path, Logo_URL, \
    Navigation_Collapsed_Cookie, Navigation_Collapsed_Value, Navigation_Width_Cookie, Static_Dir, Static_URL
from zato.common.b2b.portal.sample.common import Details_Segment, New_Segment, Path_Messages, Path_Partners
from zato.common.b2b.portal.sample.sections import Navigation, Sections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from django.http.response import HttpResponseBase
    from zato.common.typing_ import anydict, anylist, strlist

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

def _pick_key(tabs:'anylist', requested:'str') -> 'str':
    """ The key of the tab the address names, or the key of the first tab when the address names none of them.
    """
    out = tabs[0]['key']

    for each in tabs:
        if each['key'] == requested:
            out = requested

    return out

# ################################################################################################################################

def _segment(segments:'strlist', index:'int') -> 'str':
    """ The segment of the address at the given position, or an empty string when the address is shorter.
    """
    out = ''

    if index < len(segments):
        out = segments[index]

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

def _navigation_width(req:'HttpRequest') -> 'str':
    """ The width of the navigation pane in pixels, as the browser kept it after the pane was last resized,
    or an empty string when the pane has never been resized.
    """
    out = ''

    if width := req.COOKIES.get(Navigation_Width_Cookie):
        if width.isdigit():
            out = width

    return out

# ################################################################################################################################

def _is_navigation_collapsed(req:'HttpRequest') -> 'bool':
    """ Whether the navigation pane was left collapsed on an earlier page.
    """
    value = req.COOKIES.get(Navigation_Collapsed_Cookie)

    out = value == Navigation_Collapsed_Value
    return out

# ################################################################################################################################
# ################################################################################################################################

def home_view(req:'HttpRequest') -> 'HttpResponseBase':
    _ = req
    out = HttpResponseRedirect(Path_Messages)
    return out

# ################################################################################################################################

def section_view(req:'HttpRequest', section_slug:'str', rest:'str'='') -> 'HttpResponseBase':
    """ One listing of the portal, the details of one of its items, or the wizard that adds a new item to it,
    each segment of the address after the section naming what is open - the partner of a section listed by partner,
    then either the wizard and its step, or the item, its tab, and what it keeps apart from its tabs with the tab of that.
    """
    if section_slug not in Sections:
        raise Http404(f'No section `{section_slug}`')

    section = Sections[section_slug]
    segments:'strlist' = []

    if rest:
        segments = rest.split('/')

    # A section listed by partner is shown for one partner only, and without a partner the partners are shown instead
    if section['scopes']:

        if not segments:
            out = HttpResponseRedirect(Path_Partners)
            return out

        scope_key = segments.pop(0)

        if scope_key not in section['scopes']:
            raise Http404(f'No partner `{scope_key}` in `{section_slug}`')

        section = section['scopes'][scope_key]

    first = _segment(segments, 0)
    is_new = first == New_Segment

    item = None
    active_tab = ''
    details_tab = ''
    wizard_step = ''

    if is_new:
        if not section['wizard']:
            raise Http404(f'No wizard in `{section_slug}`')
        wizard_step = _pick_key(section['wizard']['steps'], _segment(segments, 1))

    elif first:
        item = _find_item(section, first)
        active_tab = _pick_key(item['tabs'], _segment(segments, 1))

        # .. what an item keeps apart from its tabs is opened only for an item that keeps anything apart ..
        if _segment(segments, 2) == Details_Segment:
            if item['details']:
                details_tab = _pick_key(item['details'], _segment(segments, 3))

    context = {
        'organization': Local_Organization,
        'has_logo': bool(Logo_Path),
        'logo_url': Logo_URL,
        'navigation': _navigation(section_slug),
        'navigation_width': _navigation_width(req),
        'navigation_width_cookie': Navigation_Width_Cookie,
        'is_navigation_collapsed': _is_navigation_collapsed(req),
        'navigation_collapsed_cookie': Navigation_Collapsed_Cookie,
        'navigation_collapsed_value': Navigation_Collapsed_Value,
        'section': section,
        'item': item,
        'active_tab': active_tab,
        'details_tab': details_tab,
        'is_new': is_new,
        'wizard_step': wizard_step,
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

def logo_view(req:'HttpRequest') -> 'HttpResponseBase':
    """ The logo of the organization, read from the file the environment variable points to.
    """
    _ = req

    if not Logo_Path:
        raise Http404(f'No {Logo_Env_Variable} environment variable')

    logo_file = open(Logo_Path, 'rb')

    out = FileResponse(logo_file)
    out['Cache-Control'] = 'no-cache'
    return out

# ################################################################################################################################

def empty_view(req:'HttpRequest') -> 'HttpResponse':
    _ = req
    out = HttpResponse(status=NO_CONTENT)
    return out

# ################################################################################################################################
# ################################################################################################################################
