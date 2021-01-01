# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.hl7.mllp.client import HL7MLLPClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _HL7MLLPConnection(object):
    def __init__(self, **kwargs):
        '''
        self.impl = HL7MLLPClient(config)
        '''
        pass

# ################################################################################################################################
# ################################################################################################################################

class HL7MLLPWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 MLLP servers.
    """
    def __init__(self, config, server):
        config.auth_url = config.address
        super(HL7MLLPWrapper, self).__init__(config, 'HL7 MLLP', server)

    def add_client(self):
        conn = _HL7MLLPConnection(self.config)
        self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
