# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Bunch
from bunch import Bunch

# Python 2/3 compatibility
from builtins import bytes
from past.builtins import basestring

# Zato
from zato.common.const import SECRETS

# ################################################################################################################################

def resolve_value(key, value, decrypt_func=None, _default=object(), _secrets=SECRETS):
    """ Resolves final value of a given variable by looking it up in environment if applicable.
    """
    # Skip non-resolvable items
    if not isinstance(value, basestring):
        return value

    if not value:
        return value

    value = value.decode('utf8') if isinstance(value, bytes) else value

    # It may be an environment variable ..
    if value.startswith('$'):

        # .. but not if it's $$ which is a signal to skip this value ..
        if value.startswith('$$'):
            return value

        # .. a genuine pointer to an environment variable.
        else:
            env_key = value[1:].strip().upper()
            value = os.environ.get(env_key, _default)

            # Use a placeholder if the actual environment key is missing
            if value is _default:
                value = 'ENV_KEY_MISSING_{}'.format(env_key)

    # It may be an encrypted value
    elif key in _secrets.PARAMS and value.startswith(_secrets.PREFIX):
        value = decrypt_func(value)

    # Pre-processed, we can assign this pair to output
    return value

# ################################################################################################################################

def resolve_env_variables(data):
    """ Given a Bunch instance on input, iterates over all items and resolves all keys/values to ones extracted
    from environment variables.
    """
    out = Bunch()
    for key, value in data.items():
        out[key] = resolve_value(None, value)

    return out
