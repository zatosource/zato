# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.hl7.mllp.client import HL7MLLPClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _HL7MLLPConnection:
    def __init__(self, config):
        self.impl = HL7MLLPClient(config)

    def invoke(self, data):
        # type: (str) -> str
        return self.impl.send(data)

# ################################################################################################################################
# ################################################################################################################################

class OutconnHL7MLLPWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 MLLP servers.
    """
    def __init__(self, config, server):
        config.auth_url = config.address
        super(OutconnHL7MLLPWrapper, self).__init__(config, 'HL7 MLLP', server)

    def add_client(self):

        try:
            conn = _HL7MLLPConnection(self.config)
            self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding an HL7 MLLP client (%s); e:`%s`',
                self.config.name, format_exc())

    def delete(self, ignored_reason=None):
        pass

# ################################################################################################################################
# ################################################################################################################################
