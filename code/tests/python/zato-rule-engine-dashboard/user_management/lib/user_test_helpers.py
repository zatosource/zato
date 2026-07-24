# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.contrib.auth.models import User
from django.test import Client

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The display name new accounts start with
_default_display_name = 'Test User'

# ################################################################################################################################
# ################################################################################################################################

def new_account(
    *,
    is_admin:'bool'=False,
    is_active:'bool'=True,
    display_name:'str'=_default_display_name,
    ) -> 'anytuple':
    """ Creates a user of a unique name, returning it along with its plaintext password.
    """
    username = 'test.user.' + CryptoManager.generate_hex_string()
    password = 'password.' + CryptoManager.generate_hex_string()

    user:'any_' = User(username=username)

    first_name, _, last_name = display_name.partition(' ')
    user.first_name = first_name
    user.last_name = last_name

    user.set_password(password)
    user.is_staff = is_admin
    user.is_superuser = is_admin
    user.is_active = is_active
    user.save()

    out = user, password
    return out

# ################################################################################################################################

def signed_in_client(user:'any_') -> 'Client':
    """ Returns a test client with that user already signed in.
    """
    out = Client()
    out.force_login(user)

    return out

# ################################################################################################################################

def is_signed_in(client:'Client') -> 'bool':
    """ Whether the client's session belongs to an authenticated user.
    """
    out = '_auth_user_id' in client.session
    return out

# ################################################################################################################################
# ################################################################################################################################
