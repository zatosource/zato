# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class NATSError(Exception):
    pass

class NATSConnectionError(NATSError):
    pass

class NATSTimeoutError(NATSError):
    pass

class NATSProtocolError(NATSError):
    pass

class NATSNoRespondersError(NATSError):
    pass

class NATSJetStreamError(NATSError):
    def __init__(self, code:'int'=0, err_code:'int'=0, description:'str'='') -> None:
        self.code = code
        self.err_code = err_code
        self.description = description
        super().__init__(f'JetStream error: code={code}, err_code={err_code}, description={description}')

# ################################################################################################################################
# ################################################################################################################################
