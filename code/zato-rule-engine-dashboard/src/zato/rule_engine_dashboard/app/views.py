# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import wraps
from logging import getLogger

# Django
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import redirect, render

# Zato
from zato.common.typing_ import cast_
from zato.common.webapp.request import client_address
from zato.rule_engine_dashboard.app import user_rules
from zato.rule_engine_dashboard.app.models import add_event, UserAction
from zato.rule_engine_dashboard.app.user_rules import Root_Username, UserManagementError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The stubs type transaction.atomic too narrowly for use as a context manager
atomic = cast_('any_', transaction.atomic)

# ################################################################################################################################
# ################################################################################################################################

def admin_required(view:'any_') -> 'any_':
    """ Only signed-in admins reach the wrapped view.
    """
    @wraps(view)
    def wrapper(req:'any_', *args:'any_', **kwargs:'any_') -> 'any_':

        if not req.user.is_authenticated:
            return HttpResponseForbidden(b'Not signed in')

        if not req.user.is_superuser:
            return HttpResponseForbidden(b'Admins only')

        out = view(req, *args, **kwargs)
        return out

    return wrapper

# ################################################################################################################################
# ################################################################################################################################

@admin_required
def users_list(req:'any_') -> 'any_':
    """ All the application's users, with per-row actions for the ones the actor may manage.
    """
    users = User.objects.order_by('username')

    context = {
        'users': users,
        'root_username': Root_Username,
    }

    out = render(req, 'users.html', context)
    return out

# ################################################################################################################################

def _find_user(req:'any_', username:'str') -> 'any_':
    """ Returns the user of that name or None, leaving a message when there is none -
    the row may have been deleted in another browser after the list was rendered.
    """
    out = User.objects.filter(username=username).first()

    if out is None:
        messages.error(req, f'User `{username}` does not exist')

    return out

# ################################################################################################################################

@admin_required
def user_set_active(req:'any_', username:'str', is_active:'bool') -> 'any_':
    """ Enables or disables a user from the list.
    """
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # The permission rules decide first ..
    try:
        user_rules.ensure_can_set_active(req.user, username)
    except UserManagementError as e:
        messages.error(req, str(e))
        return redirect('users')

    # .. the row may be gone by now ..
    user = _find_user(req, username)
    if user is None:
        return redirect('users')

    if is_active:
        action = UserAction.Enable
        verb = 'enabled'
    else:
        action = UserAction.Disable
        verb = 'disabled'

    # .. the change and its event land in one transaction ..
    with atomic():
        user.is_active = is_active
        user.save()
        _ = add_event(req.user.username, action, username, client_address(req), f'is_active={is_active}')

    # .. and the list shows the outcome.
    messages.success(req, f'User `{username}` {verb}')

    out = redirect('users')
    return out

# ################################################################################################################################

@admin_required
def user_delete(req:'any_', username:'str') -> 'any_':
    """ Deletes a user from the list - the confirmation happens in the browser before the request is sent.
    """
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # The permission rules decide first ..
    try:
        user_rules.ensure_can_delete(req.user, username)
    except UserManagementError as e:
        messages.error(req, str(e))
        return redirect('users')

    # .. the row may be gone by now ..
    user = _find_user(req, username)
    if user is None:
        return redirect('users')

    # .. the change and its event land in one transaction ..
    with atomic():
        details = f'is_admin={user.is_superuser} is_active={user.is_active}'
        _ = user.delete()
        _ = add_event(req.user.username, UserAction.Delete, username, client_address(req), details)

    # .. and the list shows the outcome.
    messages.success(req, f'User `{username}` deleted')

    out = redirect('users')
    return out

# ################################################################################################################################
# ################################################################################################################################
