# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import sleep

# Zato
from zato.common.api import ZATO_NONE
from zato.common.typing_ import cast_
from zato.common.util.api import spawn_greenlet
from zato.server.generic.api.outconn.wsx.common import _BaseWSXClient

# Zato - Ext - ws4py
from zato.server.ext.ws4py.client.threadedclient import WebSocketClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class _NonZatoWSXClientImpl(WebSocketClient, _BaseWSXClient):

    def __init__(
        self,
        config:'stranydict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':

        _BaseWSXClient.__init__(self, config, on_connected_cb, on_message_cb, on_close_cb)
        WebSocketClient.__init__(self, *args, **kwargs)

# ################################################################################################################################

    def close(self, code:'int'=1000, reason:'str'=ZATO_NONE) -> 'None':
        # It is needed to set this custom reason code because when it is us who closes the connection the 'closed' event
        # (i.e. on_close_cb) gets invoked and we need to know not to reconnect automatically in such a case.
        super(_NonZatoWSXClientImpl, self).close(code, reason)

# ################################################################################################################################
# ################################################################################################################################

class _NonZatoWSXClient:

    send:'callable_' # type: ignore
    invoke:'callable_'

    _non_zato_client:'_NonZatoWSXClientImpl'

    def __init__(
        self,
        config:'stranydict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'None':

        self.config = config
        self.on_connected_cb = on_connected_cb
        self.on_message_cb = on_message_cb
        self.on_close_cb = on_close_cb
        self.init_args = args
        self.init_kwargs = kwargs

        # This will be overwritten in self._init in a new thread
        # but we need it set to None so that self.init can check
        # if the client object has been already created.
        self._non_zato_client = cast_('_NonZatoWSXClientImpl', None)

# ################################################################################################################################

    def _init(self) -> 'any_':

        # This is the actual client, starting in a new thread ..
        self._non_zato_client = _NonZatoWSXClientImpl(
            self.config,
            self.on_connected_cb,
            self.on_message_cb,
            self.on_close_cb,
            *self.init_args,
            **self.init_kwargs,
        )

        # .. map implementation methods to our own.
        self.invoke = self._non_zato_client.send
        self.send = self.invoke # type: ignore

# ################################################################################################################################

    def init(self) -> 'any_':

        # This will start a WSX connection in a new thread ..
        _ = spawn_greenlet(self._init)

        # .. which is why we wait here until the object has been created.
        while not self._non_zato_client:
            sleep(0.1)

# ################################################################################################################################

    def send(self, *args:'any_', **kwargs:'any_') -> 'any_':
        """ This method is going to be overwritten in self._init but we need it here because our caller expects it sooner.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def connect(self) -> 'any_':
        self._non_zato_client.connect()

# ################################################################################################################################

    def is_connected(self) -> 'bool':
        return not self._non_zato_client.terminated

# ################################################################################################################################

    def run_forever(self) -> 'any_':
        pass

# ################################################################################################################################

    def close(self, reason:'str') -> 'any_':
        self._non_zato_client.close(reason=reason)

# ################################################################################################################################
# ################################################################################################################################

# For Flake8
_ = _NonZatoWSXClient

# ################################################################################################################################
# ################################################################################################################################
