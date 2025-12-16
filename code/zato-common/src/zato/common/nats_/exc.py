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
    pass

class NATSConnectionError(NATSError):
    """ Connection error.
    """
    pass

class NATSTimeoutError(NATSError):
    """ Timeout error.
    """
    pass

class NATSProtocolError(NATSError):
    """ Protocol error.
    """
    pass

class NATSNoRespondersError(NATSError):
    """ No responders available for the request.
    """
    pass

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
