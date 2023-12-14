# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.typing_ import cast_
from zato.server.connection.salesforce import SalesforceClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _SalesforceClient:
    def __init__(self, config:'stranydict') -> 'None':

        # The actual connection object
        self.impl = SalesforceClient.from_config(config)

        # Forward invocations to the underlying client
        self.get = self.impl.get
        self.post = self.impl.post
        self.ping = self.impl.ping

# ################################################################################################################################
# ################################################################################################################################

class CloudSalesforceWrapper(Wrapper):
    """ Wraps a queue of connections to Salesforce.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config['auth_url'] = config['address']
        super(CloudSalesforceWrapper, self).__init__(config, 'Salesforce', server)

# ################################################################################################################################

    def add_client(self):

        try:
            conn = _SalesforceClient(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Salesforce client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self):
        with self.client() as client:
            client = cast_('_SalesforceClient', client)
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
