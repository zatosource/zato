# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# ws4py
from ws4py.client.threadedclient import WebSocketClient

# Zato
from zato.common.api import WEB_SOCKET, ZATO_NONE
from zato.common.wsx_client import Client as ZatoWSXClientImpl, Config as _ZatoWSXConfigImpl
from zato.common.util.api import new_cid
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict, strlist, strnone
    from zato.common.wsx_client import MessageFromServer
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

msg_closing_superfluous = 'Closing superfluous connection (Zato queue)'

# ################################################################################################################################
# ################################################################################################################################

class WSXCtx:
    """ Details of a message received from a WebSocket outgoing connection.
    """
    type = None

    def __init__(self, config:'stranydict', conn:'OutconnWSXWrapper') -> 'None':
        self.config = config
        self.conn = conn

# ################################################################################################################################
# ################################################################################################################################

class Connected(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.CONNECT

# ################################################################################################################################
# ################################################################################################################################

class OnMessage(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.MESSAGE

    def __init__(self, data:'MessageFromServer', *args:'any_', **kwargs:'any_') -> 'None':
        self.data = data
        super(OnMessage, self).__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class Close(WSXCtx):
    type = WEB_SOCKET.OUT_MSG_TYPE.CLOSE

    def __init__(self, code:'int', reason:'strnone'=None, *args:'any_', **kwargs:'any_') -> 'None':
        self.code = code
        self.reason = reason
        super(Close, self).__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class _BaseWSXClient:
    def __init__(
        self,
        config:'stranydict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_',
        *ignored_args:'any_',
        **ignored_kwargs:'any_'
    ) -> 'None':
        self.config = config
        self.on_connected_cb = on_connected_cb
        self.on_message_cb = on_message_cb
        self.on_close_cb = on_close_cb

# ################################################################################################################################

    def opened(self) -> 'None':
        self.on_connected_cb(self)

# ################################################################################################################################

    def received_message(self, msg:'MessageFromServer') -> 'None':
        self.on_message_cb(msg.data)

# ################################################################################################################################

    def closed(self, code:'int', reason:'strnone'=None) -> 'None':
        self.on_close_cb(code, reason)

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

    def close(self, code:'int'=1000, reason:'str'=ZATO_NONE) -> 'None':
        # It is needed to set this custom reason code because when it is us who closes the connection the 'closed' event
        # (i.e. on_close_cb) gets invoked and we need to know not to reconnect automatically in such a case.
        super(_NonZatoWSXClient, self).close(code, reason)

# ################################################################################################################################
# ################################################################################################################################

class _ZatoWSXClientImpl(ZatoWSXClientImpl):
    def __init__(
        self,
        _outcon_wsx_on_connect_cb:'callable_',
        *args: 'any_',
        **kwargs: 'any_'
    ) -> 'None':
        self._outcon_wsx_on_connect_cb = _outcon_wsx_on_connect_cb
        super(_ZatoWSXClientImpl, self).__init__(*args, **kwargs)

    def on_connected(self) -> 'None':
        super(_ZatoWSXClientImpl, self).on_connected()
        self._outcon_wsx_on_connect_cb()

# ################################################################################################################################
# ################################################################################################################################

class ZatoWSXClient(_BaseWSXClient):
    """ A client through which Zato services can be invoked over outgoing WebSocket connections.
    """
    def __init__(self, *args: 'any_', **kwargs: 'any_') -> 'None':
        super(ZatoWSXClient, self).__init__(*args, **kwargs)

        self._zato_client_config = _ZatoWSXConfigImpl()
        self._zato_client_config.client_name = 'WSX outconn - {}'.format(self.config['name'])
        self._zato_client_config.client_id = 'wsx.out.{}'.format(new_cid(8))
        self._zato_client_config.address = self.config['address']
        self._zato_client_config.on_request_callback = self.on_message_cb
        self._zato_client_config.on_closed_callback = self.on_close_cb
        self._zato_client_config.max_connect_attempts = self.config.get('max_connect_attempts', 1234567890)

        if self.config.get('username'):
            self._zato_client_config.username = self.config['username']
            self._zato_client_config.secret = self.config['secret']

        self._zato_client = _ZatoWSXClientImpl(self.opened, self._zato_client_config)
        self.invoke = self.send = self._zato_client.invoke

# ################################################################################################################################

    def connect(self) -> 'None':
        # Not needed but added for API completeness.
        # The reason it is not needed is that self._zato_client's run_forever will connect itself.
        pass

# ################################################################################################################################

    def close(self, reason:'str'='') -> 'None':
        self._zato_client.stop(reason)

# ################################################################################################################################

    def should_keep_running(self):
        return self._zato_client.keep_running

# ################################################################################################################################

    def get_subscription_list(self) -> 'strlist':

        # This is an initial, static list of topics to subscribe to ..
        subscription_list = (self.config['subscription_list'] or '').splitlines()

        # .. while the rest can be dynamically populated by services.
        on_subscribe_service_name = self.config.get('on_subscribe_service_name')

        if on_subscribe_service_name:
            topic_list = self.config['parent'].on_subscribe_cb(on_subscribe_service_name)

            if topic_list:
                subscription_list.extend(topic_list)

        return subscription_list

# ################################################################################################################################

    def subscribe_to_topics(self) -> 'None':

        subscription_list = self.get_subscription_list()

        if subscription_list:
            logger.info('Subscribing WSX outconn `%s` to `%s`', self.config['name'], subscription_list)

            for topic_name in subscription_list:
                try:
                    self.invoke_subscribe_service(topic_name)
                except Exception:
                    logger.warning('Could not subscribe WSX outconn to `%s`, e:`%s`', self.config['name'], format_exc())

# ################################################################################################################################

    def run_forever(self) -> 'None':

        try:
            # This will establish an outgoing connection to the remote WSX server.
            # However, this will be still a connection on the level of TCP / WSX,
            # which means that we still need to wait before we can invoke
            # the server with our list of subscriptions below.
            self._zato_client.run()

            # Wait until the client is fully ready
            while not self._zato_client.is_authenticated:

                # Sleep for a moment ..
                sleep(0.1)

                # .. and do not loop anymore if we are not to keep running.
                if not self.should_keep_running():
                    return

            # If we are here, it means that we are both connected and authenticated,
            # so  we know that we can try to subscribe to pub/sub topics
            # and we will not be rejected based on the fact that we are not logged in.
            self.subscribe_to_topics()

        except Exception:
            logger.warn('Exception in run_forever -> %s', format_exc())

# ################################################################################################################################
# ################################################################################################################################

class WSXClient:
    """ A client through which outgoing WebSocket messages can be sent.
    """
    is_zato:'bool'

    def __init__(self, config:'stranydict') -> 'None':
        self.config = config
        self.is_zato = self.config['is_zato']
        self._init()

    def _init(self) -> 'None':

        if self.is_zato:
            _impl_class = ZatoWSXClient
        else:
            _impl_class = _NonZatoWSXClient

        self.impl = _impl_class(self.config, self.on_connected_cb, self.on_message_cb, self.on_close_cb, self.config['address'])

        self.send = self.impl.send
        if _impl_class is ZatoWSXClient:
            self.invoke = self.send

        self.impl.connect()
        self.impl.run_forever()

    def on_connected_cb(self, conn:'OutconnWSXWrapper') -> 'None':
        self.config['parent'].on_connected_cb(conn)

    def on_message_cb(self, msg:'MessageFromServer') -> 'None':
        self.config['parent'].on_message_cb(msg)

    def on_close_cb(self, code:'int', reason:'strnone'=None) -> 'None':
        self.config['parent'].on_close_cb(code, reason)

    def delete(self, reason:'str'='') -> 'None':
        self.impl.close(reason=reason)

    def is_impl_connected(self) -> 'bool':
        if isinstance(self.impl, ZatoWSXClient):
            return self.impl._zato_client.is_connected
        else:
            return not self.impl.terminated

# ################################################################################################################################
# ################################################################################################################################

class OutconnWSXWrapper(Wrapper):
    """ Wraps a queue of connections to WebSockets.
    """
    def __init__(self, config:'stranydict', server:'ParallelServer') -> 'None':
        config['parent'] = self
        self._resolve_config_ids(config, server)
        super(OutconnWSXWrapper, self).__init__(config, 'outgoing WebSocket', server)

# ################################################################################################################################

    def _resolve_config_ids(self, config:'stranydict', server:'ParallelServer') -> 'None':

        on_connect_service_id   = config.get('on_connect_service_id')   # type: int
        on_message_service_id   = config.get('on_message_service_id')   # type: int
        on_close_service_id     = config.get('on_close_service_id')     # type: int
        on_subscribe_service_id = config.get('on_subscribe_service_id') # type: int

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

                config['username'] = sec_def_config['username']
                config['secret'] = sec_def_config['password']

# ################################################################################################################################

    def on_subscribe_cb(self, service_name:'str') -> 'strlist':

        # Our response to produce
        out = []

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

            if self.config['has_auto_reconnect']:
                logger.info('WebSocket `%s` will reconnect to `%s` (hac:%d)',
                    self.config['name'], self.config['address'], self.config['has_auto_reconnect'])
                try:
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

            if not conn.is_impl_connected():
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
