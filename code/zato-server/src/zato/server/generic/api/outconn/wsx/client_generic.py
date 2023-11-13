# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import ZATO_NONE
from zato.server.generic.api.outconn.wsx.common import _BaseWSXClient

# Zato - Ext - ws4py
from zato.server.ext.ws4py.client.threadedclient import WebSocketClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class _NonZatoWSXClient(WebSocketClient, _BaseWSXClient):

    def __init__(
        self,
        config:'stranydict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':

        WebSocketClient.__init__(self, *args, **kwargs)
        _BaseWSXClient.__init__(self, config, on_connected_cb, on_message_cb, on_close_cb)

# ################################################################################################################################

    def close(self, code:'int'=1000, reason:'str'=ZATO_NONE) -> 'None':
        # It is needed to set this custom reason code because when it is us who closes the connection the 'closed' event
        # (i.e. on_close_cb) gets invoked and we need to know not to reconnect automatically in such a case.
        super(_NonZatoWSXClient, self).close(code, reason)

# ################################################################################################################################
# ################################################################################################################################
