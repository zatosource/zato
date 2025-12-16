# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class NATSError(Exception):
    """ Base exception for NATS errors.
    """

class NATSConnectionError(NATSError):
    """ Connection error.
    """

class NATSTimeoutError(NATSError):
    """ Timeout error.
    """

class NATSProtocolError(NATSError):
    """ Protocol error.
    """

class NATSNoRespondersError(NATSError):
    """ No responders available for the request.
    """

class NATSJetStreamError(NATSError):
    """ JetStream API error.
    """
    def __init__(self, code:'int'=0, err_code:'int'=0, description:'str'='') -> None:
        self.code = code
        self.err_code = err_code
        self.description = description
        super().__init__(f'JetStream error: code={code}, err_code={err_code}, description={description}')

# ################################################################################################################################
# ################################################################################################################################
