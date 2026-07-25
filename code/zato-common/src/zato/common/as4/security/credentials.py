# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The wsse:UsernameToken half of AS4 message security - the credentials a network asks for next to the
signature, which is how pull requests are authorized on the networks that work that way.

The token itself is built and checked by the shared WS-Security implementation, the same one SOAP
channels use, because a UsernameToken in an AS4 envelope is the same token in the same header as one
anywhere else. What this module adds is where it goes in an AS4 exchange and what its outcome means
in ebMS terms, which is the EBMS:0101 FailedAuthentication error.
"""

# Zato
from zato.common.as4.common import AS4SecurityException, EbMSError, NS
from zato.common.soap.common import SOAPSecurityException
from zato.common.soap.security.usernametoken import add_username_token, verify_username_token
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.pmode import SecurityConfig
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def add_credentials(envelope:'any_', config:'SecurityConfig') -> 'None':
    """ Adds the wsse:UsernameToken to an outgoing envelope, for an exchange whose P-Mode names
    a username. An exchange that names none carries no token.
    """
    username = config.username_token_username

    if not username:
        return

    _ = add_username_token(envelope, username, config.username_token_password)

# ################################################################################################################################

def _find_security_header(envelope:'any_') -> 'any_':
    """ Returns the wsse:Security header of an incoming envelope, or None for one that carries none.
    """
    header = envelope.find(qname(NS.SOAP, 'Header'))

    if header is None:
        out = None
    else:
        out = header.find(qname(NS.WSSE, 'Security'))

    return out

# ################################################################################################################################

def require_credentials(envelope:'any_', config:'SecurityConfig') -> 'None':
    """ Requires an incoming envelope to carry the wsse:UsernameToken its P-Mode names, with the
    credentials that P-Mode configures. An exchange whose P-Mode names no username is not asked
    for a token and is not refused for arriving without one.
    """
    username = config.username_token_username

    if not username:
        return

    # The token is looked for in a header the message already has - a message with no security header
    # at all is refused here rather than having one created for it just to find it empty.
    if _find_security_header(envelope) is None:
        raise AS4SecurityException(EbMSError.Failed_Authentication, 'Message carries no security header')

    # Whatever the token turns out to be wrong about, an ebMS peer is owed the one error code the
    # specification has for it, so the WS-Security failure is translated rather than propagated.
    try:
        verify_username_token(envelope, username, config.username_token_password)
    except SOAPSecurityException as e:
        raise AS4SecurityException(EbMSError.Failed_Authentication, e.args[0]) from e

# ################################################################################################################################
# ################################################################################################################################
