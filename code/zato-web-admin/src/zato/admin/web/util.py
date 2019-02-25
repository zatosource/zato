# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps, loads

# Zato
from zato.admin.web.models import UserProfile
from zato.common.crypto import CryptoManager

# ################################################################################################################################

def get_user_profile(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=user)
        user_profile.save()
    finally:
        return user_profile

# ################################################################################################################################

def set_user_profile_totp_key(user_profile, zato_secret_key, totp_key, totp_key_label=None, opaque_attrs=None):

    if not opaque_attrs:
        opaque_attrs = user_profile.opaque1
        opaque_attrs = loads(opaque_attrs) if opaque_attrs else {}

    cm = CryptoManager(secret_key=zato_secret_key)

    # TOTP key is always encrypted
    totp_key = cm.encrypt(totp_key.encode('utf8'))
    opaque_attrs['totp_key'] = totp_key

    # .. and so is its label
    if totp_key_label:
        totp_key_label = cm.encrypt(totp_key_label.encode('utf8'))
        opaque_attrs['totp_key_label'] = totp_key_label

    '''
    cm = CryptoManager(secret_key=zato_settings.zato_secret_key)

    # TOTP key is always encrypted
    totp_key = cm.encrypt(totp_key.encode('utf8'))
    opaque_attrs['totp_key'] = totp_key

    # .. and so is its label
    totp_key_label = opaque_attrs.get('totp_key_label')
    if totp_key_label:
        totp_key_label = cm.encrypt(totp_key_label.encode('utf8'))
        opaque_attrs['totp_key_label'] = totp_key_label
    '''


# ################################################################################################################################
