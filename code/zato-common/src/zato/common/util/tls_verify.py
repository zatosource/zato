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

# The one environment variable that turns TLS verification off for the whole process. It exists for
# development against endpoints with self-signed certificates - in production it means every
# outgoing connection accepts any certificate, which is why it is announced rather than honoured
# quietly. Two other spellings used to be accepted as well, which meant a deployment could have
# verification off through a variable nobody was looking for.
Skip_Verify_Env_Key = 'Zato_Skip_SSL_Verify'

_skip_verify_warning = 'TLS verification is disabled process-wide by the %s environment variable - ' \
    'every outgoing connection will accept any certificate presented to it'

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

    Every outgoing path resolves it here rather than each reading the pieces itself. The declarative
    SOAP path used to read only validate_tls, which meant an mTLS definition's pinned CA bundle was
    configured, stored, and then never reached the request - the connection verified against the
    system trust store and the pinning silently did nothing.
    """
    if is_verification_skipped():
        return False

    tls_verify = config.get('validate_tls', True)

    if not tls_verify:
        return False

    # An mTLS definition may pin the remote end's CA bundle, and when it does the pinned bundle is
    # what to verify against instead of the system trust store.
    ca_certs_path = config.get('ca_certs_path')

    if ca_certs_path:
        return ca_certs_path

    out = tls_verify
    return out

# ################################################################################################################################
# ################################################################################################################################
