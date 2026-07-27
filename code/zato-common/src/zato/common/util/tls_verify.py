# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# The one environment variable that turns TLS verification off for the whole process. It is meant
# for development against endpoints with self-signed certificates and it is spelled this way and
# no other way.
Skip_Verify_Env_Key = 'Zato_Skip_SSL_Verify'

_skip_verify_warning = 'TLS verification is disabled process-wide by the %s environment variable'

# What a configuration that does not spell TLS verification out at all gets. Only a connection
# stored in the ODB carries the setting, so a client built by hand outside one has to start
# somewhere, and the only safe place to start is verifying.
Default_Validate_TLS = True

# Whether the warning above has already been emitted. It is a process-wide setting, so saying so
# once at the first outgoing request is the point - repeating it per request would bury it.
_warning_emitted = False

# ################################################################################################################################
# ################################################################################################################################

def is_verification_skipped() -> 'bool':
    """ Says whether TLS verification is disabled process-wide, announcing it the first time.
    """
    global _warning_emitted

    if Skip_Verify_Env_Key not in os.environ:
        return False

    if not _warning_emitted:
        logger.warning(_skip_verify_warning, Skip_Verify_Env_Key)
        _warning_emitted = True

    return True

# ################################################################################################################################

def resolve_tls_verify(config:'stranydict') -> 'any_':
    """ Returns what to hand requests as its verify argument for a connection - False to skip
    verification, a path to a CA bundle to verify against, or True for the system trust store.

    Every outgoing path resolves it here rather than each reading the pieces itself.
    """
    if is_verification_skipped():
        return False

    tls_verify = config['validate_tls']

    if not tls_verify:
        return False

    # An mTLS definition may pin the remote end's CA bundle, and when it does the pinned bundle is
    # what to verify against instead of the system trust store. It is carried by the definition,
    # not by the connection, so it is only there when such a definition is attached.
    ca_certs_path = config.get('ca_certs_path')

    if ca_certs_path:
        return ca_certs_path

    out = tls_verify
    return out

# ################################################################################################################################
# ################################################################################################################################
