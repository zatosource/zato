# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common import AUTH_RESULT

def parse_basic_auth(auth, prefix='Basic '):
    """ Parses username/password out of incoming HTTP Basic Auth data.
    """
    if not auth:
        raise ValueError('No auth received in `{}` ({})'.format(auth, AUTH_RESULT.BASIC_AUTH.NO_AUTH))

    if not auth.startswith(prefix):
        raise ValueError('Invalid prefix in `{}` ({})'.format(auth, AUTH_RESULT.BASIC_AUTH.NO_AUTH))

    _, auth = auth.split(prefix)
    auth = auth.strip().decode('base64')

    return auth.split(':', 1)
