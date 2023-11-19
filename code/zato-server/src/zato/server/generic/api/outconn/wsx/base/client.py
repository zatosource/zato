# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent import sleep as _gevent_sleep

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.typing_ import cast_
from zato.server.generic.api.outconn.wsx.client_generic import _NonZatoWSXClient
from zato.server.generic.api.outconn.wsx.client_zato import ZatoWSXClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_, strdict, strnone
    from zato.common.wsx_client import MessageFromServer
    from zato.server.base.parallel import ParallelServer
    from zato.server.generic.api.outconn.wsx.base.wrapper import OutconnWSXWrapper
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_json = DATA_FORMAT.JSON
msg_closing_superfluous = 'Closing superfluous connection (Zato queue)'

# ################################################################################################################################
# ################################################################################################################################

class WSXClient:
    """ A client through which outgoing WebSocket messages can be sent.
    """

    is_zato: 'bool'
    impl: 'ZatoWSXClient | _NonZatoWSXClient'

    send: 'callable_'
    invoke: 'callable_'

    address_masked:'str'

    def __init__(self, server:'ParallelServer', config:'strdict') -> 'None':
        self.server = server
        self.config = config
        self.is_zato = self.config['is_zato']
        self.impl = cast_('any_', None)
        self.address_masked = self.config['address_masked']

    def _init(self) -> 'None':

        # Decide which implementation class to use ..
        if self.is_zato:
            _impl_class = ZatoWSXClient
        else:
            _impl_class = _NonZatoWSXClient

        # .. this will create an instance ..
        self.impl = _impl_class(
            self.server,
            self.config,
            self.on_connected_cb,
            self.on_message_cb,
            self.on_close_cb
        )

        # .. this will initialize it ..
        _ = self.impl.init()

        # .. so now, we can make use of what was possibly initialized in .init above ..
        self.send   = self.impl.send
        self.invoke = self.send

        # .. additional features of the Zato client ..
        if _impl_class is ZatoWSXClient:
            self.invoke_service = self.impl._zato_client.invoke_service # type: ignore

        # .. now, the client can connect ..
        _ = self.impl.connect()

        # .. and run forever.
        _ = self.impl.run_forever()

# ################################################################################################################################

    def init(self) -> 'None':

        # Keep trying until our underlying client is connected ..
        while not self.is_impl_connected():

            # .. stop if the client should not try again, e.g. it has been already deleted ..
            if self.impl and (not self.impl.should_keep_running()):

                # .. log what we are about to do ..
                msg  = f'Returning from WSXClient.init -> {self.address_masked} -> '
                msg += f'self.impl of `{hex(id(self))}` should not keep running'
                logger.info(msg)

                # .. do return to our caller.
                return

            # .. also, delete the connection and stop if we are no longer ..
            # .. in the server-wide list of connection pools that should exist ..
            if not self.server.wsx_connection_pool_wrapper.has_item(self):

                # .. log what we are about to do ..
                msg  = f'Returning from WSXClient.init -> `{self.address_masked}` -> '
                msg += 'pool `{hex(id(self))}` already deleted'
                logger.info(msg)

                # .. delete and close the underlying client ..
                self.delete()

                # .. do return to our caller.
                return

            # .. if we are here, it means that we keep trying ..
            else:

                # .. do try to connect ..
                self._init()

                # .. sleep for a while after the attempt.
                _gevent_sleep(1)

    def on_connected_cb(self, conn:'OutconnWSXWrapper') -> 'None':
        self.config['parent'].on_connected_cb(conn)

# ################################################################################################################################

    def on_message_cb(self, msg:'MessageFromServer') -> 'None':
        self.config['parent'].on_message_cb(msg)

# ################################################################################################################################

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':
        self.config['parent'].on_close_cb(code, reason)

# ################################################################################################################################

    def delete(self, reason:'str'='') -> 'None':
        if self.impl:
            self.impl.delete(reason)

# ################################################################################################################################

    def is_impl_connected(self) -> 'bool':
        return self.impl and self.impl.check_is_connected()

# ################################################################################################################################

    def get_name(self) -> 'str':
        return f'{self.config["name"]} - {self.config["type_"]} - {hex(id(self))}'

# ################################################################################################################################
# ################################################################################################################################
