# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class B2BException(Exception):
    """ Base class for all exceptions raised by the B2B protocol layers.
    """

# ################################################################################################################################
# ################################################################################################################################

class B2BProtocolException(B2BException):
    """ Raised when a message or an agreement violates the rules of its protocol. Has the protocol's
    own error code, so that the error signal sent back names it, and the location of the offending
    element when the protocol reports one.
    """
    def __init__(self, error_code:'str', detail:'str', location:'str'='') -> 'None':
        super().__init__(f'{error_code} -> {detail}')
        self.error_code = error_code
        self.detail = detail
        self.location = location

# ################################################################################################################################
# ################################################################################################################################

class B2BSecurityException(B2BProtocolException):
    """ Raised when signature verification or certificate validation fails.
    """

# ################################################################################################################################
# ################################################################################################################################
