# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.api import ZATO_NONE
from zato.common.typing_ import cast_
from zato.common.util.api import spawn_greenlet
from zato.common.util.config import replace_query_string_items
from zato.server.generic.api.outconn.wsx.common import _BaseWSXClient

# Zato - Ext - ws4py
from zato.server.ext.ws4py.client.threadedclient import WebSocketClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _NonZatoWSXClientImpl(WebSocketClient, _BaseWSXClient):

    def __init__(
        self,
        server:'ParallelServer',
        config:'stranydict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_'
    ) -> 'None':

        _BaseWSXClient.__init__(self, server, config, on_connected_cb, on_message_cb, on_close_cb)
        WebSocketClient.__init__(
            self,
            server=server,
            url=config['address'],
            heartbeat_freq=config['ping_interval'],
            socket_read_timeout=config['socket_read_timeout'],
            socket_write_timeout=config['socket_write_timeout'],
        )

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
    log_address:'str'
    _non_zato_client:'_NonZatoWSXClientImpl'

    def __init__(
        self,
        server: 'ParallelServer',
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

        self.server = server
        self.keep_running = True
        self.connection_attempts_so_far = 0

        # This is different than that the underlying implementation's .is_connected flag
        # because this here indicates that we completed a handshake and, for instance,
        # the remote end has not returned any 40x response, whereas .is_connected
        # only indicates if a TCP-level connection exists.
        self.has_established_connection = False

        # This will be overwritten in self._init in a new thread
        # but we need it set to None so that self.init can check
        # if the client object has been already created.
        self._non_zato_client = cast_('_NonZatoWSXClientImpl', None)

# ################################################################################################################################

    def _init(self) -> 'any_':

        # This is the actual client, starting in a new thread ..
        self._non_zato_client = _NonZatoWSXClientImpl(
            self.server,
            self.config,
            self.on_connected_cb,
            self.on_message_cb,
            self.on_close_cb,
            *self.init_args,
            **self.init_kwargs,
        )

        # .. build it here as we may want to update it dynamically ..
        self.address_masked = replace_query_string_items(self.server, self.config['address'])

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

        if not self.should_keep_running():
            return

        self.connection_attempts_so_far += 1

        try:
            self._non_zato_client.connect(close_on_handshake_error=False)
        except Exception:
            logger.warn('WSX could not connect to `%s` -> id:%s -> `%s (#%s)',
                self.address_masked,
                hex(id(self._non_zato_client)),
                format_exc(),
                self.connection_attempts_so_far,
            )
        else:
            self.has_established_connection = True

# ################################################################################################################################

    def close(self, reason:'str') -> 'any_':
        if self._non_zato_client:
            self._non_zato_client.close(reason=reason)

# ################################################################################################################################

    def delete(self) -> 'None':
        self.keep_running = False

# ################################################################################################################################

    def should_keep_running(self) -> 'bool':
        return self.keep_running

# ################################################################################################################################

    def check_is_connected(self) -> 'bool':
        if self._non_zato_client:
            is_connected = not self._non_zato_client.terminated
            return is_connected and self.has_established_connection
        else:
            return False

# ################################################################################################################################

    def run_forever(self) -> 'any_':
        # Added for API completeness
        pass

# ################################################################################################################################
# ################################################################################################################################

# For Flake8 - _NonZatoWSXClient
_ = _NonZatoWSXClient

# ################################################################################################################################
# ################################################################################################################################
