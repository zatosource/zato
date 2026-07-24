# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The account created at first start
Root_Username = 'admin'

# ################################################################################################################################
# ################################################################################################################################

class UserManagementError(Exception):
    """ Raised when an actor attempts a user management action the rules do not allow.
    """

# ################################################################################################################################
# ################################################################################################################################

def _ensure_is_admin(actor:'any_') -> 'None':
    """ Only application admins may manage other users.
    """
    if not actor.is_superuser:
        raise UserManagementError(f'User `{actor.username}` is not an admin')

# ################################################################################################################################

def _ensure_not_root(actor:'any_', subject_username:'str', action:'str') -> 'None':
    """ Blocks actions on the root account.
    """
    if subject_username == Root_Username:
        raise UserManagementError(f'User `{actor.username}` cannot {action} the `{Root_Username}` account')

# ################################################################################################################################

def _ensure_not_self(actor:'any_', subject_username:'str', action:'str') -> 'None':
    """ Some actions only ever apply to other accounts, never one's own.
    """
    if subject_username == actor.username:
        raise UserManagementError(f'User `{actor.username}` cannot {action} their own account')

# ################################################################################################################################
# ################################################################################################################################

def ensure_can_create(actor:'any_', username:'str') -> 'None':
    """ Only admins create users and the root username can never be created again.
    """
    _ensure_is_admin(actor)

    if username == Root_Username:
        raise UserManagementError(f'The `{Root_Username}` account cannot be created')

# ################################################################################################################################

def ensure_can_update_profile(actor:'any_', subject_username:'str') -> 'None':
    """ Everyone edits their own display name, admins also edit anyone else's.
    """
    _ensure_not_root(actor, subject_username, 'edit')

    # One's own profile is otherwise always editable ..
    if subject_username == actor.username:
        return

    # .. and anyone else's requires an admin.
    _ensure_is_admin(actor)

# ################################################################################################################################

def ensure_can_set_role(actor:'any_', subject_username:'str') -> 'None':
    """ Admins promote or demote anyone else - never themselves and never the root account.
    """
    _ensure_is_admin(actor)
    _ensure_not_root(actor, subject_username, 'change the role of')
    _ensure_not_self(actor, subject_username, 'change the role of')

# ################################################################################################################################

def ensure_can_set_active(actor:'any_', subject_username:'str') -> 'None':
    """ Admins enable or disable anyone else - never themselves and never the root account.
    """
    _ensure_is_admin(actor)
    _ensure_not_root(actor, subject_username, 'enable or disable')
    _ensure_not_self(actor, subject_username, 'enable or disable')

# ################################################################################################################################

def ensure_can_delete(actor:'any_', subject_username:'str') -> 'None':
    """ Admins delete anyone else - never themselves and never the root account.
    """
    _ensure_is_admin(actor)
    _ensure_not_root(actor, subject_username, 'delete')
    _ensure_not_self(actor, subject_username, 'delete')

# ################################################################################################################################

def ensure_can_change_password(actor:'any_', subject_username:'str') -> 'None':
    """ Everyone changes their own password, admins also change anyone else's.
    """
    _ensure_not_root(actor, subject_username, 'change the password of')

    # One's own password is otherwise always changeable ..
    if subject_username == actor.username:
        return

    # .. and anyone else's requires an admin.
    _ensure_is_admin(actor)

# ################################################################################################################################
# ################################################################################################################################
