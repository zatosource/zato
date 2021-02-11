
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
import sys

# Zato
from zato.common.const import SECRETS

# ################################################################################################################################
# ################################################################################################################################

def resolve_secret_key(secret_key, _url_prefix=SECRETS.URL_PREFIX):
    """ Finds a secret key among command line options or via environment variables.
    """
    # We always require a string
    secret_key = secret_key or ''

    if secret_key and (not isinstance(_url_prefix, bytes)):
        _url_prefix = _url_prefix.encode('utf8')

    # This is a direct value, to be used as-is
    if not secret_key.startswith(_url_prefix):
        return secret_key
    else:
        # We need to look it up somewhere
        secret_key = secret_key.replace(_url_prefix, '', 1)

        # Command line options
        if secret_key.startswith('cli'):

            # This will be used by check-config
            for idx, elem in enumerate(sys.argv):
                if elem == '--secret-key':
                    secret_key = sys.argv[idx+1]
                    break

            # This will be used when components are invoked as subprocesses
            else:
                # To prevent circular imports
                from zato.common.util.api import parse_cmd_line_options

                cli_options = parse_cmd_line_options(sys.argv[1])
                secret_key = cli_options['secret_key']

        # Environment variables
        elif secret_key.startswith('env'):
            env_key = secret_key.replace('env.', '', 1)
            secret_key = os.environ[env_key]

        # Unknown scheme, we need to give up
        else:
            raise ValueError('Unknown secret key type `{}`'.format(secret_key))

    # At this point, we have a secret key extracted in one way or another
    return secret_key if isinstance(secret_key, bytes) else secret_key.encode('utf8')

# ################################################################################################################################
# ################################################################################################################################
