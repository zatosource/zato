# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import SALESFORCE
from zato.common.typing_ import cast_
from zato.server.connection.salesforce import SalesforceClient
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import stranydict, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields that the create path may not have supplied,
# e.g. when a connection is created directly through zato.generic.connection.create.
cloud_salesforce_config_defaults = {
    'api_version': SALESFORCE.Default.API_Version,
}

# ################################################################################################################################
# ################################################################################################################################

class _SalesforceClient:
    def __init__(self, config:'stranydict') -> 'None':

        # The actual connection object
        self.impl = SalesforceClient.from_config(config)

        # Forward invocations to the underlying client
        self.get = self.impl.get
        self.post = self.impl.post
        self.patch = self.impl.patch
        self.delete = self.impl.delete
        self.ping = self.impl.ping

# ################################################################################################################################

    def zato_delete_impl(self, reason:'strnone'=None) -> 'None':
        """ Called by the connection queue when the connection is deleted - there is nothing to release.
        """
        pass

# ################################################################################################################################
# ################################################################################################################################

class CloudSalesforceWrapper(Wrapper):
    """ Wraps a queue of connections to Salesforce.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config['auth_url'] = config['address']
        super(CloudSalesforceWrapper, self).__init__(config, 'Salesforce', server)

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = _SalesforceClient(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding a Salesforce client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            client = cast_('_SalesforceClient', client)
            _ = client.ping()

# ################################################################################################################################
# ################################################################################################################################
