# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import wraps
from logging import getLogger

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import resolve_url

# Zato
from zato.common.typing_ import cast_
from zato.rule_engine_dashboard.app.user_rules import UserManagementError

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

def signed_in_required(view:'any_') -> 'any_':
    """ Only signed-in users reach the wrapped view - everyone else goes to the sign-in screen first.
    """
    @wraps(view)
    def wrapper(req:'any_', *args:'any_', **kwargs:'any_') -> 'any_':

        if not req.user.is_authenticated:
            out = redirect_to_login(req.get_full_path(), settings.LOGIN_URL)
            return out

        out = view(req, *args, **kwargs)
        return out

    return wrapper

# ################################################################################################################################

def admin_required(view:'any_') -> 'any_':
    """ Only signed-in admins reach the wrapped view.
    """
    @wraps(view)
    @signed_in_required
    def wrapper(req:'any_', *args:'any_', **kwargs:'any_') -> 'any_':

        if not req.user.is_superuser:
            return HttpResponseForbidden(b'Admins only')

        out = view(req, *args, **kwargs)
        return out

    return wrapper

# ################################################################################################################################

def check_rule(req:'any_', rule:'any_', *args:'any_') -> 'bool':
    """ Calls one permission rule with the requesting user as the actor,
    turning its error into a form message. Returns whether the action may go ahead.
    """
    try:
        rule(req.user, *args)
    except UserManagementError as e:
        messages.error(req, str(e))
        out = False
    else:
        out = True

    return out

# ################################################################################################################################

def find_user(req:'any_', username:'str') -> 'any_':
    """ Returns the user of that name or None, leaving a message when there is none -
    the row may have been deleted in another browser after the list was rendered.
    """
    out = User.objects.filter(username=username).first()

    if out is None:
        messages.error(req, f'User `{username}` does not exist')

    return out

# ################################################################################################################################

def set_display_name(user:'any_', display_name:'str') -> 'None':
    """ Stores a display name in the same split form external provisioning uses.
    """
    first_name, _, last_name = display_name.partition(' ')
    user.first_name = first_name
    user.last_name = last_name

# ################################################################################################################################

def default_screen(user:'any_') -> 'str':
    """ The screen a person lands on by default - the users list for admins, the profile for everyone else.
    """
    if user.is_superuser:
        out = resolve_url('users')
    else:
        out = resolve_url('profile')

    return out

# ################################################################################################################################
# ################################################################################################################################
