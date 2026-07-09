# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import ODATA
from zato.common.odata.client import ODataClient
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_odata_config_defaults:'dict[str, object]' = {
    'odata_version': ODATA.DEFAULT.ODATA_VERSION,
    'auth_type': ODATA.AUTH_TYPE.BASIC.id,
    'username': '',
    'secret': '',
    'token_url': '',
    'tenant_id': '',
    'client_id': '',
    'client_secret': '',
    'scopes': '',
    'needs_csrf_token': False,
    'page_size': ODATA.DEFAULT.PAGE_SIZE,
    'timeout': ODATA.DEFAULT.TIMEOUT,
    'pool_size': ODATA.DEFAULT.POOL_SIZE,
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_odata_int_config_keys = ('page_size', 'timeout', 'pool_size')

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_odata_bool_config_keys = ('needs_csrf_token',)

# ################################################################################################################################
# ################################################################################################################################

class OutconnODataWrapper(Wrapper):
    """ Wraps a queue of OData clients - each client owns its HTTP session along with
    the OAuth2 and CSRF tokens it caches.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.auth_url = config.address
        super(OutconnODataWrapper, self).__init__(config, 'OData', server)

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = ODataClient(self.config)
            _ = self.client.put_client(conn)
        except Exception:
            logger.warning('Caught an exception while adding an OData client (%s); e:`%s`',
                self.config['name'], format_exc())

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            client = cast_('ODataClient', client)
            status_code = client.ping()

            # The service root replied but with an error status - surface it as a failed ping.
            if status_code >= BAD_REQUEST:
                raise Exception(f'OData ping to `{self.config["address"]}` failed -> {status_code}')

# ################################################################################################################################
# ################################################################################################################################
