# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import loads
from logging import getLogger

# Zato
from zato.common.crypto import CryptoManager

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

def get_user_profile(user, needs_logging=True):
    if needs_logging:
        logger.info('Getting profile for user `%s`', user)

    from zato.admin.web.models import UserProfile

    try:
        user_profile = UserProfile.objects.get(user=user)
        if needs_logging:
            logger.info('Found an existing profile for user `%s`', user)
    except UserProfile.DoesNotExist:

        if needs_logging:
            logger.info('Did not find an existing profile for user `%s`', user)

        user_profile = UserProfile(user=user)
        user_profile.save()

        if needs_logging:
            logger.info('Created a profile for user `%s`', user)

    finally:
        if needs_logging:
            logger.info('Returning a user profile for `%s`', user)
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

    return opaque_attrs


# ################################################################################################################################
