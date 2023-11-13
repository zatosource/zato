# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC, ZATO_NONE
from zato.common.typing_ import cast_
from zato.server.connection.queue import Wrapper
from zato.server.generic.api.outconn.wsx.client_generic import _NonZatoWSXClient
from zato.server.generic.api.outconn.wsx.client_zato import ZatoWSXClient
from zato.server.generic.api.outconn.wsx.common import Close, Connected, OnMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import strdict, strlist, strnone
    from zato.common.wsx_client import MessageFromServer
    from zato.server.base.parallel import ParallelServer
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

msg_closing_superfluous = 'Closing superfluous connection (Zato queue)'

# ################################################################################################################################
# ################################################################################################################################

class WSXClient:
    """ A client through which outgoing WebSocket messages can be sent.
    """
    is_zato:'bool'

    def __init__(self, config:'strdict') -> 'None':
        self.config = config
        self.is_zato = self.config['is_zato']
        self.impl = None

    def init(self) -> 'None':

        if self.is_zato:
            _impl_class = ZatoWSXClient
        else:
            _impl_class = _NonZatoWSXClient

        self.impl = _impl_class(self.config, self.on_connected_cb, self.on_message_cb, self.on_close_cb, self.config['address'])
        self.send = self.impl.send

        if _impl_class is ZatoWSXClient:
            self.invoke = self.send
            self.invoke_service = self.impl._zato_client.invoke_service # type: ignore

        self.impl.connect()
        self.impl.run_forever()

    def on_connected_cb(self, conn:'OutconnWSXWrapper') -> 'None':
        self.config['parent'].on_connected_cb(conn)

    def on_message_cb(self, msg:'MessageFromServer') -> 'None':
        self.config['parent'].on_message_cb(msg)

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':
        self.config['parent'].on_close_cb(code, reason)

    def delete(self, reason:'str'='') -> 'None':
        self.impl.close(reason=reason) # type: ignore

    def is_impl_connected(self) -> 'bool':

        if isinstance(self.impl, ZatoWSXClient):
            is_connected = self.impl._zato_client.is_connected
        else:
            is_connected = not self.impl.terminated # type: ignore

        return is_connected

# ################################################################################################################################
# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    has_delete_reasons = True
    supports_reconnections = True

    def __init__(self, config:'strdict', server:'ParallelServer') -> 'None':
        config['parent'] = self
        self._resolve_config_ids(config, server)
        super(OutconnWSXWrapper, self).__init__(cast_('Bunch', config), COMMON_GENERIC.ConnName.OutconnWSX, server)

# ################################################################################################################################

    def check_is_active(self) -> 'bool':
        is_active = self.server.is_active_outconn_wsx(self.config['id'])
        return is_active

# ################################################################################################################################

    def _resolve_config_ids(self, config:'strdict', server:'ParallelServer') -> 'None':

        on_connect_service_id   = config.get('on_connect_service_id', 0)   # type: int
        on_message_service_id   = config.get('on_message_service_id', 0)   # type: int
        on_close_service_id     = config.get('on_close_service_id', 0)     # type: int
        on_subscribe_service_id = config.get('on_subscribe_service_id', 0) # type: int

        if on_connect_service_id:
            config['on_connect_service_name'] = server.api_service_store_get_service_name_by_id(on_connect_service_id)

        if on_message_service_id:
            config['on_message_service_name'] = server.api_service_store_get_service_name_by_id(on_message_service_id)

        if on_close_service_id:
            config['on_close_service_name'] = server.api_service_store_get_service_name_by_id(on_close_service_id)

        if on_subscribe_service_id:
            config['on_subscribe_service_name'] = server.api_service_store_get_service_name_by_id(on_subscribe_service_id)

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

    def on_connected_cb(self, conn:'OutconnWSXWrapper'):

        if self.config.get('on_connect_service_name'):
            try:
                self.server.invoke(self.config['on_connect_service_name'], {
                    'ctx': Connected(self.config, conn)
                })
            except Exception:
                logger.warning('Could not invoke CONNECT service `%s`, e:`%s`',
                    self.config['on_close_service_name'], format_exc())

# ################################################################################################################################

    def on_message_cb(self, msg:'MessageFromServer'):

        if self.config.get('on_message_service_name'):
            self.server.invoke(self.config['on_message_service_name'], {
                'ctx': OnMessage(msg, self.config, self)
            })

# ################################################################################################################################

    def _should_handle_close_cb(self, _ignored_code:'int', reason:'strnone') -> 'bool':

        if reason not in (ZATO_NONE, msg_closing_superfluous):
            if not self.delete_requested:
                return True

        # Return False by default
        return False

# ################################################################################################################################

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':

        # Ignore events we generated ourselves, e.g. when someone edits a connection in web-admin
        # this will result in deleting and rerecreating a connection which implicitly calls this callback.
        if self._should_handle_close_cb(code, reason):

            logger.info('Remote server closed connection to WebSocket `%s`, c:`%s`, r:`%s`', self.config['name'], code, reason)

            if self.config.get('on_close_service_name'):

                try:
                    self.server.invoke(self.config['on_close_service_name'], {
                        'ctx': Close(code, reason, self.config, self)
                    })
                except Exception:
                    logger.warning('Could not invoke CLOSE service `%s`, e:`%s`', self.config['on_close_service_name'], format_exc())

            has_auto_reconnect:'bool' = self.config.get('has_auto_reconnect', True)

            if has_auto_reconnect:
                logger.info('WebSocket `%s` will reconnect to `%s` (hac:%d)',
                    self.config['name'], self.config['address'], has_auto_reconnect)
                try:
                    if reason != COMMON_GENERIC.DeleteReasonBytes:
                        self.server.api_worker_store_reconnect_generic(self.config['id'])
                except Exception:
                    logger.warning('Could not reconnect WebSocket `%s` to `%s`, e:`%s`',
                        self.config['name'], self.config['address'], format_exc())

        else:
            # Do not handle it but log information so as not to overlook the event
            logger.info('WSX `%s` (%s) ignoring close event code:`%s` reason:`%s`',
                self.config['name'], self.config['address'], code, reason)

# ################################################################################################################################

    def add_client(self) -> 'None':

        try:
            conn = WSXClient(self.config)
            self.conn_in_progress_list.append(conn)
            conn.init()

            sleep(5)

            if not conn.is_impl_connected():
                self.client.decr_in_progress_count()
                # return

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
