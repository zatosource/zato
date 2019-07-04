# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# ws4py
from ws4py.client.threadedclient import WebSocketClient

# Zato
from zato.common import WEB_SOCKET, ZATO_NONE
from zato.common.wsx_client import Client as ZatoWSXClientImpl, Config as _ZatoWSXConfigImpl
from zato.common.util import new_cid
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

msg_closing_superfluous = 'Closing superfluous connection (Zato queue)'

# ################################################################################################################################

class WSXCtx(object):
    """ Details of a message received from a WebSocket outgoing connection.
    """
    type = None

    def __init__(self, config, conn):
        self.config = config
        self.conn = conn

# ################################################################################################################################

class Connected(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.CONNECT

# ################################################################################################################################

class OnMessage(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.MESSAGE

    def __init__(self, data, *args, **kwargs):
        self.data = data
        super(OnMessage, self).__init__(*args, **kwargs)

# ################################################################################################################################

class Close(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.CLOSE

    def __init__(self, code, reason=None, *args, **kwargs):
        self.code = code
        self.reason = reason
        super(Close, self).__init__(*args, **kwargs)

# ################################################################################################################################

class _BaseWSXClient(object):
    def __init__(self, config, on_connected_cb, on_message_cb, on_close_cb, *ignored_args, **ignored_kwargs):
        self.config = config
        self.on_connected_cb = on_connected_cb
        self.on_message_cb = on_message_cb
        self.on_close_cb = on_close_cb

# ################################################################################################################################

    def opened(self):
        self.on_connected_cb(self)

# ################################################################################################################################

    def received_message(self, msg):
        self.on_message_cb(msg.data)

# ################################################################################################################################

    def closed(self, code, reason=None):
        self.on_close_cb(code, reason)

# ################################################################################################################################

class _NonZatoWSXClient(WebSocketClient, _BaseWSXClient):

    def __init__(self, config, on_connected_cb, on_message_cb, on_close_cb, *args, **kwargs):
        WebSocketClient.__init__(self, *args, **kwargs)
        _BaseWSXClient.__init__(self, config, on_connected_cb, on_message_cb, on_close_cb)

    def close(self, code=1000, reason=ZATO_NONE):
        # It is needed to set this custom reason code because when it is us who closes the connection the 'closed' event
        # (i.e. on_close_cb) gets invoked and we need to know not to reconnect automatically in such a case.
        super(_NonZatoWSXClient, self).close(code, reason)

# ################################################################################################################################

class _ZatoWSXClientImpl(ZatoWSXClientImpl):
    def __init__(self, _outcon_wsx_on_connect_cb, *args, **kwargs):
        self._outcon_wsx_on_connect_cb = _outcon_wsx_on_connect_cb
        super(_ZatoWSXClientImpl, self).__init__(*args, **kwargs)

    def on_connected(self):
        super(_ZatoWSXClientImpl, self).on_connected()
        self._outcon_wsx_on_connect_cb()

# ################################################################################################################################

class ZatoWSXClient(_BaseWSXClient):
    """ A client through which Zato services can be invoked over outgoing WebSocket connections.
    """
    def __init__(self, *args, **kwargs):
        super(ZatoWSXClient, self).__init__(*args, **kwargs)

        self._zato_client_config = _ZatoWSXConfigImpl()
        self._zato_client_config.client_name = 'WSX outconn - {}'.format(self.config.name)
        self._zato_client_config.client_id = 'wsx.out.{}'.format(new_cid(8))
        self._zato_client_config.address = self.config.address
        self._zato_client_config.on_request_callback = self.on_message_cb
        self._zato_client_config.on_closed_callback = self.on_close_cb

        if self.config.get('username'):
            self._zato_client_config.username = self.config.username
            self._zato_client_config.secret = self.config.secret

        self._zato_client = _ZatoWSXClientImpl(self.opened, self._zato_client_config)
        self.invoke = self.send = self._zato_client.invoke

# ################################################################################################################################

    def connect(self):
        # Not needed but added for API completeness.
        # The reason it is not needed is that self._zato_client's run_forever will connect itself.
        pass

# ################################################################################################################################

    def close(self, reason=''):
        self._zato_client.stop(reason)

# ################################################################################################################################

    def run_forever(self):
        self._zato_client.run()

        subscription_list = (self.config.subscription_list or '').splitlines()

        if subscription_list:
            logger.info('Subscribing WSX outconn `%s` to `%s`', self.config.name, subscription_list)

            for topic_name in subscription_list:
                try:
                    self.invoke({
                        'service':'zato.pubsub.pubapi.subscribe-wsx',
                        'request': {
                            'topic_name': topic_name
                        }
                    })
                except Exception:
                    logger.warn('Could not subscribe WSX outconn to `%s`, e:`%s`', self.config.name, format_exc())

# ################################################################################################################################

class WSXClient(object):
    """ A client through which outgoing WebSocket messages can be sent.
    """
    def __init__(self, config):
        self.config = config
        self._init()

    def _init(self):
        _impl_class = ZatoWSXClient if self.config.is_zato else _NonZatoWSXClient
        self.impl = _impl_class(self.config, self.on_connected_cb, self.on_message_cb, self.on_close_cb, self.config.address)

        self.send = self.impl.send
        if _impl_class is ZatoWSXClient:
            self.invoke = self.send

        self.impl.connect()
        self.impl.run_forever()

    def on_connected_cb(self, conn):
        self.config.parent.on_connected_cb(conn)

    def on_message_cb(self, msg):
        self.config.parent.on_message_cb(msg)

    def on_close_cb(self, code, reason=None):
        self.config.parent.on_close_cb(code, reason)

    def delete(self, reason=''):
        self.impl.close(reason)

    def is_impl_connected(self):
        return self.impl._zato_client.is_connected

# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    def __init__(self, config, server):
        config.parent = self
        self._resolve_config_ids(config, server)
        super(OutconnWSXWrapper, self).__init__(config, 'outgoing WebSocket', server)

# ################################################################################################################################

    def _resolve_config_ids(self, config, server):

        if config.get('on_connect_service_id'):
            config.on_connect_service_name = server.service_store.get_service_name_by_id(config.on_connect_service_id)

        if config.get('on_message_service_id'):
            config.on_message_service_name = server.service_store.get_service_name_by_id(config.on_message_service_id)

        if config.get('on_close_service_id'):
            config.on_close_service_name = server.service_store.get_service_name_by_id(config.on_close_service_id)

        if config.get('security_def'):
            if config.security_def != ZATO_NONE:
                _ignored_sec_type, sec_def_id = config.security_def.split('/')
                sec_def_id = int(sec_def_id)
                sec_def_config = server.worker_store.basic_auth_get_by_id(sec_def_id)

                config.username = sec_def_config['username']
                config.secret = sec_def_config['password']

# ################################################################################################################################

    def on_connected_cb(self, conn):

        if self.config.get('on_connect_service_name'):
            try:
                self.server.invoke(self.config.on_connect_service_name, {
                    'ctx': Connected(self.config, conn)
                })
            except Exception:
                logger.warn('Could not invoke CONNECT service `%s`, e:`%s`', self.config.on_close_service_name, format_exc())

# ################################################################################################################################

    def on_message_cb(self, msg):
        if self.config.get('on_message_service_name'):
            self.server.invoke(self.config.on_message_service_name, {
                'ctx': OnMessage(msg, self.config, self)
            })

# ################################################################################################################################

    def _should_handle_close_cb(self, code, reason):

        if reason not in (ZATO_NONE, msg_closing_superfluous):
            if not self.delete_requested:
                return True

# ################################################################################################################################

    def on_close_cb(self, code, reason=None):

        # Ignore events we generated ourselves, e.g. when someone edits a connection in web-admin
        # this will result in deleting and rerecreating a connection which implicitly calls this callback.
        if self._should_handle_close_cb(code, reason):

            logger.info('Remote server closed connection to WebSocket `%s`, c:`%s`, r:`%s`', self.config.name, code, reason)

            if self.config.get('on_close_service_name'):

                try:
                    self.server.invoke(self.config.on_close_service_name, {
                        'ctx': Close(code, reason, self.config, self)
                    })
                except Exception:
                    logger.warn('Could not invoke CLOSE service `%s`, e:`%s`', self.config.on_close_service_name, format_exc())

            if self.config.has_auto_reconnect:
                logger.info('WebSocket `%s` will reconnect to `%s` (hac:%d)',
                    self.config.name, self.config.address, self.config.has_auto_reconnect)
                try:
                    self.server.worker_store.reconnect_generic(self.config.id)
                except Exception:
                    logger.warn('Could not reconnect WebSocket `%s` to `%s`, e:`%s`',
                        self.config.name, self.config.address, format_exc())

        else:
            # Do not handle it but log information so as not to overlook the event
            logger.info('WSX `%s` (%s) ignoring close event code:`%s` reason:`%s`',
                self.config.name, self.config.address, code, reason)

# ################################################################################################################################

    def add_client(self):
        try:
            conn = WSXClient(self.config)

            if not conn.is_impl_connected():
                self.client.decr_in_progress_count()
                return

        except Exception:
            logger.warn('WSX client `%s` could not be built `%s`', self.config.name, format_exc())
        else:
            try:
                if not self.client.put_client(conn):
                    self.delete_queue_connections(msg_closing_superfluous)
            except Exception:
                logger.warn('WSX error `%s`', format_exc())
            finally:
                self.client.decr_in_progress_count()

# ################################################################################################################################
