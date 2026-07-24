# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import redirect, render

# Zato
from zato.common.webapp.request import client_address
from zato.rule_engine_dashboard.app import user_rules
from zato.rule_engine_dashboard.app.models import add_event, UserAction
from zato.rule_engine_dashboard.app.user_rules import Root_Username
from zato.rule_engine_dashboard.app.views.common import admin_required, atomic, check_rule, default_screen, find_user, \
     set_display_name, signed_in_required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# What the event trail records when an accepted submit changed no fields
_no_changes_details = 'no_changes=True'

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

@admin_required
def user_create(req:'any_') -> 'any_':
    """ A new user - the form on GET, the creation on POST.
    """
    if req.method == 'GET':
        out = render(req, 'user_create.html')
        return out

    username = req.POST.get('username', '').strip()
    display_name = req.POST.get('display_name', '').strip()
    password = req.POST.get('password', '')
    is_admin = 'is_admin' in req.POST

    # Whatever goes wrong below, the form comes back with what was already typed in
    context = {
        'username': username,
        'display_name': display_name,
        'is_admin': is_admin,
    }

    # The permission rules decide first ..
    if not check_rule(req, user_rules.ensure_can_create, username):
        out = render(req, 'user_create.html', context)
        return out

    # .. the required fields must be filled in ..
    if not username:
        messages.error(req, 'Username is required')
        out = render(req, 'user_create.html', context)
        return out

    if not password:
        messages.error(req, 'Password is required')
        out = render(req, 'user_create.html', context)
        return out

    # .. the username must be free ..
    if User.objects.filter(username=username).exists():
        messages.error(req, f'User `{username}` already exists')
        out = render(req, 'user_create.html', context)
        return out

    # .. the account and its event land in one transaction ..
    with atomic():
        user:'any_' = User(username=username)
        set_display_name(user, display_name)
        user.set_password(password)
        user.is_staff = is_admin
        user.is_superuser = is_admin
        user.save()
        _ = add_event(req.user.username, UserAction.Create, username, client_address(req), f'is_admin={is_admin}')

    # .. and the list shows the outcome.
    messages.success(req, f'User `{username}` created')

    out = redirect('users')
    return out

# ################################################################################################################################

def _collect_edit_changes(req:'any_', user:'any_', is_self:'bool') -> 'strlist | None':
    """ Applies the submitted edit form to the user in memory, returning what changed
    or None when a permission rule said no.
    """

    # What changed is collected for the event trail
    changes:'strlist' = []

    # The display name is editable for everyone this screen lets through ..
    display_name = req.POST.get('display_name', '').strip()
    current_display_name = user.get_full_name()

    if display_name != current_display_name:
        set_display_name(user, display_name)
        changes.append(f'display_name={display_name}')

    # .. while one's own role and status never change through this screen.
    if not is_self:

        is_admin = 'is_admin' in req.POST
        is_active = 'is_active' in req.POST

        if is_admin != user.is_superuser:
            if not check_rule(req, user_rules.ensure_can_set_role, user.username):
                return None
            user.is_staff = is_admin
            user.is_superuser = is_admin
            changes.append(f'is_admin={is_admin}')

        if is_active != user.is_active:
            if not check_rule(req, user_rules.ensure_can_set_active, user.username):
                return None
            user.is_active = is_active
            changes.append(f'is_active={is_active}')

    return changes

# ################################################################################################################################

@admin_required
def user_edit(req:'any_', username:'str') -> 'any_':
    """ Display name, role and status of a user - the actor's own row keeps its role and status.
    """

    # The permission rules decide first, for the form and for the change alike ..
    if not check_rule(req, user_rules.ensure_can_update_profile, username):
        return redirect('users')

    # .. the row may be gone by now ..
    user = find_user(req, username)
    if user is None:
        return redirect('users')

    is_self = username == req.user.username

    if req.method == 'GET':
        context = {
            'subject': user,
            'is_self': is_self,
        }
        out = render(req, 'user_edit.html', context)
        return out

    # .. the form is applied field by field, each change behind its own rule ..
    changes = _collect_edit_changes(req, user, is_self)
    if changes is None:
        return redirect('users')

    # .. the trail records the action even when no field changed ..
    if changes:
        details = ' '.join(changes)
    else:
        details = _no_changes_details

    # .. the change and its event land in one transaction ..
    with atomic():
        user.save()
        _ = add_event(req.user.username, UserAction.Update, username, client_address(req), details)

    # .. and the list shows the outcome.
    messages.success(req, f'User `{username}` updated')

    out = redirect('users')
    return out

# ################################################################################################################################

@signed_in_required
def user_change_password(req:'any_', username:'str') -> 'any_':
    """ A new password for a user - admins for anyone else, everyone for themselves.
    """

    # The permission rules decide first, for the form and for the change alike ..
    if not check_rule(req, user_rules.ensure_can_change_password, username):
        out = HttpResponseRedirect(default_screen(req.user))
        return out

    # .. the row may be gone by now ..
    user = find_user(req, username)
    if user is None:
        out = HttpResponseRedirect(default_screen(req.user))
        return out

    is_self = username == req.user.username

    if req.method == 'GET':
        context = {
            'subject': user,
            'is_self': is_self,
        }
        out = render(req, 'user_change_password.html', context)
        return out

    new_password = req.POST.get('new_password', '')
    confirm_password = req.POST.get('confirm_password', '')

    # .. the new password must be filled in and confirmed ..
    if not new_password:
        messages.error(req, 'Password is required')
        return redirect('user-change-password', username)

    if new_password != confirm_password:
        messages.error(req, 'The passwords do not match')
        return redirect('user-change-password', username)

    # .. the change and its event land in one transaction - the details never carry the password ..
    with atomic():
        user.set_password(new_password)
        user.save()
        _ = add_event(req.user.username, UserAction.Password_Change, username, client_address(req), '')

    # .. one's own session survives the change ..
    if is_self:
        update_session_auth_hash(req, user)

    # .. and the person goes back to where they manage users from.
    messages.success(req, f'Password of user `{username}` changed')

    if is_self:
        out = redirect('profile')
    else:
        out = redirect('users')

    return out

# ################################################################################################################################

@signed_in_required
def profile(req:'any_') -> 'any_':
    """ One's own display name, with the password change one click away.
    """
    is_root = req.user.username == Root_Username

    if req.method == 'GET':
        context = {
            'is_root': is_root,
        }
        out = render(req, 'profile.html', context)
        return out

    # The permission rules decide first ..
    if not check_rule(req, user_rules.ensure_can_update_profile, req.user.username):
        return redirect('profile')

    display_name = req.POST.get('display_name', '').strip()
    current_display_name = req.user.get_full_name()

    # .. the trail records the action even when the name stayed the same ..
    if display_name == current_display_name:
        details = _no_changes_details
    else:
        details = f'display_name={display_name}'

    # .. the change and its event land in one transaction ..
    with atomic():
        set_display_name(req.user, display_name)
        req.user.save()
        _ = add_event(req.user.username, UserAction.Update, req.user.username, client_address(req), details)

    # .. and the profile shows the outcome.
    messages.success(req, 'Display name updated')

    out = redirect('profile')
    return out

# ################################################################################################################################

@admin_required
def user_set_active(req:'any_', username:'str', is_active:'bool') -> 'any_':
    """ Enables or disables a user from the list.
    """
    if req.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # The permission rules decide first ..
    if not check_rule(req, user_rules.ensure_can_set_active, username):
        return redirect('users')

    # .. the row may be gone by now ..
    user = find_user(req, username)
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
    if not check_rule(req, user_rules.ensure_can_delete, username):
        return redirect('users')

    # .. the row may be gone by now ..
    user = find_user(req, username)
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
