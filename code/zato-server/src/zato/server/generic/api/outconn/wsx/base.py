# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep as _gevent_sleep

# Zato
from zato.common.api import DATA_FORMAT, GENERIC as COMMON_GENERIC, WEB_SOCKET, ZATO_NONE
from zato.common.typing_ import cast_
from zato.common.util.config import resolve_name
from zato.server.connection.queue import Wrapper
from zato.server.generic.api.outconn.wsx.client_generic import _NonZatoWSXClient
from zato.server.generic.api.outconn.wsx.client_zato import ZatoWSXClient
from zato.server.generic.api.outconn.wsx.common import OnClosed, OnConnected, OnMessageReceived

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_, strdict, strlist, strnone
    from zato.common.wsx_client import MessageFromServer
    from zato.server.base.parallel import ParallelServer
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
        self.config['name'] = resolve_name(self.config['name'])
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

        # Local variables
        config_id = self.config['id']
        is_zato = self.config['is_zato']

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
            if not self.server.wsx_connection_pool_wrapper.has_item(is_zato=is_zato, config_id=config_id, item=self):

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

    def on_message_cb(self, msg:'MessageFromServer') -> 'any_':
        return self.config['parent'].on_message_cb(msg)

# ################################################################################################################################

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':
        self.config['parent'].on_close_cb(code, reason)

# ################################################################################################################################

    def delete(self, reason:'str'='') -> 'None':

        if self.impl:

            # In the Zato client, the .delete method calls its own .close,
            # so we do not need to call it. But in the non-Zato client,
            # .delete and .close are distinct and both need to be called.
            if isinstance(self.impl, _NonZatoWSXClient):
                self.impl.delete()

            # This is common to both implementations.
            self.impl.close(reason=reason) # type: ignore

# ################################################################################################################################

    def is_impl_connected(self) -> 'bool':
        return self.impl and self.impl.check_is_connected()

# ################################################################################################################################

    def get_name(self) -> 'str':
        return f'{self.config["name"]} - {self.config["type_"]} - {hex(id(self))}'

# ################################################################################################################################
# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    has_delete_reasons = True
    supports_reconnections = True

    on_connect_service_name:'str' = ''
    on_message_service_name:'str' = ''
    on_close_service_name:'str'   = ''
    on_subscribe_service_name:'str' = ''

    is_on_connect_service_wsx_adapter:'bool'   = False
    is_on_message_service_wsx_adapter:'bool'   = False
    is_on_close_service_wsx_adapter:'bool'     = False
    is_on_subscribe_service_wsx_adapter:'bool' = False

    def __init__(self, config:'strdict', server:'ParallelServer') -> 'None':

        # .. these used to be optional which is why we need ..
        # .. to ensure that we have this information here ..

        if not config.get('ping_interval'):
            config['ping_interval'] = WEB_SOCKET.DEFAULT.PING_INTERVAL

        if not config.get('pings_missed_threshold'):
            config['pings_missed_threshold'] = WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD_OUTGOING

        if not config.get('socket_read_timeout'):
            config['socket_read_timeout'] = WEB_SOCKET.DEFAULT.Socket_Read_Timeout

        # .. note that it is the same value as with the read timeout ..
        # .. because the underlying TCP sockets may be shared by multiple threads ..
        if not config.get('socket_write_timeout'):
            config['socket_write_timeout'] = config['socket_read_timeout']

        config['parent'] = self
        self._has_json = config.get('data_format') == _json
        self._resolve_config_ids(config, server)
        super(OutconnWSXWrapper, self).__init__(cast_('Bunch', config), COMMON_GENERIC.ConnName.OutconnWSX, server)

# ################################################################################################################################

    def check_is_active(self) -> 'bool':
        is_active = self.server.is_active_outconn_wsx(self.config['id'])
        return is_active

# ################################################################################################################################

    def on_outconn_stopped_running(self) -> 'None':
        self.server.on_wsx_outconn_stopped_running(self.config['id'])

# ################################################################################################################################

    def on_outconn_connected(self) -> 'None':
        self.server.on_wsx_outconn_connected(self.config['id'])

# ################################################################################################################################

    def _resolve_config_ids(self, config:'strdict', server:'ParallelServer') -> 'None':

        on_connect_service_id   = config.get('on_connect_service_id',   0) # type: int
        on_message_service_id   = config.get('on_message_service_id',   0) # type: int
        on_close_service_id     = config.get('on_close_service_id',     0) # type: int
        on_subscribe_service_id = config.get('on_subscribe_service_id', 0) # type: int

        on_connect_service_name   = config.get('on_connect_service_name',   '') # type: str
        on_message_service_name   = config.get('on_message_service_name',   '') # type: str
        on_close_service_name     = config.get('on_close_service_name',     '') # type: str
        on_subscribe_service_name = config.get('on_subscribe_service_name', '') # type: str

        #
        # Connect service
        #
        if not on_connect_service_name:
            if on_connect_service_id:
                on_connect_service_name = server.api_service_store_get_service_name_by_id(on_connect_service_id)

        if on_connect_service_name:
            self.on_connect_service_name = on_connect_service_name
            self.is_on_connect_service_wsx_adapter = server.is_service_wsx_adapter(self.on_connect_service_name)
            config['on_connect_service_name'] = self.on_connect_service_name

        #
        # On message service
        #
        if not on_message_service_name:
            if on_message_service_id:
                on_message_service_name = server.api_service_store_get_service_name_by_id(on_message_service_id)

        if on_message_service_name:
            self.on_message_service_name = on_message_service_name
            self.is_on_message_service_wsx_adapter = server.is_service_wsx_adapter(self.on_message_service_name)
            config['on_message_service_name'] = self.on_message_service_name

        #
        # OnClosed service
        #
        if not on_close_service_name:
            if on_close_service_id:
                on_close_service_name = server.api_service_store_get_service_name_by_id(on_close_service_id)

        if on_close_service_name:
            self.on_close_service_name = on_close_service_name
            self.is_on_close_service_wsx_adapter = server.is_service_wsx_adapter(self.on_close_service_name)
            config['on_close_service_name'] = self.on_close_service_name

        #
        # Subscribe service
        #
        if not on_subscribe_service_name:
            if on_subscribe_service_id:
                on_subscribe_service_name = server.api_service_store_get_service_name_by_id(on_subscribe_service_id)

        if on_subscribe_service_name:
            self.on_subscribe_service_name = on_subscribe_service_name
            self.is_on_subscribe_service_wsx_adapter = server.is_service_wsx_adapter(self.on_subscribe_service_name)
            config['on_subscribe_service_name'] = self.on_subscribe_service_name

        if config.get('security_def'):
            if config['security_def'] != ZATO_NONE:
                _ignored_sec_type, sec_def_id = config['security_def'].split('/')
                sec_def_id = int(sec_def_id)
                sec_def_config = server.api_worker_store_basic_auth_get_by_id(sec_def_id)

                if sec_def_config:
                    config['username'] = sec_def_config['username']
                    config['secret'] = sec_def_config['password']

# ################################################################################################################################

    def on_subscribe_cb(self, service_name:'str') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        # Invoke the service that will produce a list of topics to subscribe to
        response = self.server.invoke(service_name)

        # If there was any response, make sure our caller receives it
        if response:
            out.extend(response)

        # Finally, return the result to the caller
        return out

# ################################################################################################################################

    def on_connected_cb(self, conn:'OutconnWSXWrapper') -> 'None':

        if self.on_connect_service_name:
            try:
                ctx = OnConnected(self.config, conn)
                if self.is_on_connect_service_wsx_adapter:
                    self.server.invoke_wsx_adapter(self.on_connect_service_name, ctx)
                else:
                    self.server.invoke(self.on_connect_service_name, ctx)
            except Exception:
                logger.warning('Could not invoke CONNECT service `%s`, e:`%s`', self.on_connect_service_name, format_exc())

# ################################################################################################################################

    def on_message_cb(self, msg:'bytes | MessageFromServer') -> 'None':

        if self.on_message_service_name:
            try:
                if self._has_json and isinstance(msg, bytes):
                    msg = msg.decode('utf8') # type: ignore
                    msg = loads(msg) # type: ignore
                ctx = OnMessageReceived(cast_('strdict | MessageFromServer', msg), self.config, self)
                if self.is_on_message_service_wsx_adapter:
                    response = self.server.invoke_wsx_adapter(self.on_message_service_name, ctx)
                    return response
                else:
                    response = self.server.invoke(self.on_message_service_name, ctx)
                    return response
            except Exception:
                logger.warning('Could not invoke MESSAGE service `%s`, e:`%s`', self.on_message_service_name, format_exc())

# ################################################################################################################################

    def _should_handle_close_cb(self, _ignored_code:'int', reason:'strnone') -> 'bool':

        if reason not in (ZATO_NONE, msg_closing_superfluous):
            if not self.delete_requested:
                return True

        # Return False by default
        return False

# ################################################################################################################################

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':

        # We need to special-case the situation when it is us who deleted the outgoing connection.
        reason_is_not_delete = not reason in {COMMON_GENERIC.DeleteReasonBytes, COMMON_GENERIC.InitialReason}

        # Ignore events we generated ourselves, e.g. when someone edits a connection in web-admin
        # this will result in deleting and rerecreating a connection which implicitly calls this callback.
        if self._should_handle_close_cb(code, reason):

            # If reason is something else than our deleting the connection, we can log this message
            # to indicate that it must have been the remote server that did it.
            if reason_is_not_delete:
                logger.info('Remote server closed connection to WebSocket `%s`, c:`%s`, r:`%s`',
                    self.config['name'], code, reason)

            if self.on_close_service_name:
                try:
                    ctx = OnClosed(code, reason, self.config, self)
                    if self.is_on_close_service_wsx_adapter:
                        self.server.invoke_wsx_adapter(self.on_close_service_name, ctx)
                    else:
                        self.server.invoke(self.on_close_service_name, ctx)
                except Exception:
                    logger.warning('Could not invoke CLOSE service `%s`, e:`%s`', self.on_close_service_name, format_exc())

            has_auto_reconnect = self.config.get('has_auto_reconnect', True)

            if has_auto_reconnect:
                try:

                    # Reconnect only if it was not us who deleted the connection ..
                    if reason_is_not_delete:

                        # .. log what we are about to do ..
                        logger.info('WebSocket `%s` will reconnect to `%s` (hac:%d)',
                            self.config['name'], self.config['address'], has_auto_reconnect)

                        # .. and do reconnect now.
                        self.server.api_worker_store_reconnect_generic(self.config['id'])

                except Exception:
                    logger.warning('Could not reconnect WebSocket `%s` to `%s`, e:`%s`',
                        self.config['name'], self.config['address'], format_exc())

        else:
            # Do not handle it but log information so as not to overlook the event
            logger.info('WSX `%s` (%s) ignoring close event code:`%s` reason:`%s`',
                self.config['name'], self.config['address'], code, reason)

# ################################################################################################################################

    def send(self, data:'any_') -> 'None':

        # If we are being invoked while the queue is still building, we need to wait until it becomes available ..
        while self.client.is_building_conn_queue:
            _gevent_sleep(1)

        # .. now, we can invoke the remote web socket.
        with self.client() as client:
            client.send(data) # type: ignore

    invoke = send

# ################################################################################################################################

    def add_client(self) -> 'None':

        # Local variables
        config_id = self.config['id']
        is_zato = self.config['is_zato']

        # Obtain a lock whose type will differ depending on whether it is a connection to Zato or not ..
        _lock = self.server.wsx_connection_pool_wrapper.get_update_lock(is_zato=is_zato)

        # .. do make use of the lock ..
        with _lock(config_id):

            try:

                # First, make sure there are no previous connection pools for this ID ..
                self.server.wsx_connection_pool_wrapper.delete_all(config_id=config_id, is_zato=is_zato)

                # .. now, initialize the client ..
                conn = WSXClient(self.server, self.config)

                # .. append it for potential later use ..
                self.conn_in_progress_list.append(conn)

                # .. add it to the wrapper for potential later use ..
                self.server.wsx_connection_pool_wrapper.add_item(config_id=config_id, is_zato=is_zato, item=conn)

                # .. try to initialize the connection ..
                conn.init()

                # .. if we are not connected at this point, we need to delete all the reference to the pool ..
                if not conn.is_impl_connected():
                    self.delete()
                    self.client.decr_in_progress_count()
                    return

            except Exception:
                logger.warning('WSX client `%s` could not be built `%s`', self.config['name'], format_exc())
            else:
                try:
                    if not self.client.put_client(conn):
                        self.delete_queue_connections(msg_closing_superfluous)
                except Exception:
                    logger.warning('WSX error `%s`', format_exc())
                finally:
                    self.client.decr_in_progress_count()

# ################################################################################################################################
# ################################################################################################################################
