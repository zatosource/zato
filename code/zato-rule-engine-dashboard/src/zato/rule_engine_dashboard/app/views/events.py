# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.core.paginator import Paginator
from django.shortcuts import render

# Zato
from zato.rule_engine_dashboard.app.models import UserAction, UserEvent
from zato.rule_engine_dashboard.app.views.common import admin_required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How many events one page shows
_page_size = 50

# Every action the filter dropdown offers
_actions = [
    UserAction.Create,
    UserAction.Update,
    UserAction.Delete,
    UserAction.Enable,
    UserAction.Disable,
    UserAction.Password_Change,
]

# ################################################################################################################################
# ################################################################################################################################

@admin_required
def events_list(req:'any_') -> 'any_':
    """ The user management event trail - newest first, paged, filterable by actor, subject and action.
    """
    events = UserEvent.objects.order_by('-created_at', '-id')

    # Each filter is optional in the request, hence the boundary checks ..
    if actor := req.GET.get('actor', ''):
        events = events.filter(actor__icontains=actor)

    if subject := req.GET.get('subject', ''):
        events = events.filter(subject__icontains=subject)

    if action := req.GET.get('action', ''):
        events = events.filter(action=action)

    # .. the paginator turns anything that is not a valid page number into the first page ..
    paginator = Paginator(events, _page_size)
    page = req.GET.get('page')
    events_page = paginator.get_page(page)

    # .. and the current filters travel into the template so the form and the page links keep them.
    context = {
        'events': events_page,
        'actor': actor,
        'subject': subject,
        'action': action,
        'actions': _actions,
    }

    out = render(req, 'events.html', context)
    return out

# ################################################################################################################################
# ################################################################################################################################
