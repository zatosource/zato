# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from threading import current_thread
from traceback import format_exc

# gevent
from gevent import sleep

# Zato
from zato.common.wsx_client import Client as ZatoWSXClientImpl, Config as _ZatoWSXConfigImpl
from zato.common.util.api import new_cid
from zato.server.generic.api.outconn.wsx.common import _BaseWSXClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, strdict, strlist
    from zato.server.generic.api.outconn.wsx.base import OutconnWSXWrapper
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
    def __init__(
        self,
        server: 'ParallelServer',
        config:'strdict',
        on_connected_cb:'callable_',
        on_message_cb:'callable_',
        on_close_cb:'callable_',
    ) -> 'None':

        # Call our base class first
        super(ZatoWSXClient, self).__init__(
            server,
            config,
            on_connected_cb,
            on_message_cb,
            on_close_cb,
        )

        # Assign for later use
        self.server = server

        # Initialize the underlying client's configuration
        self._zato_client_config = _ZatoWSXConfigImpl()
        self._zato_client_config.client_name = 'WSX outconn - {}:{} - {}'.format(
            self.config['id'],
            current_thread().name,
            self.config['name']
        )

        self._zato_client_config.check_is_active_func = self.check_is_active
        self._zato_client_config.on_outconn_stopped_running_func = self.on_outconn_stopped_running
        self._zato_client_config.on_outconn_connected_func = self.on_outconn_connected
        self._zato_client_config.client_id = 'wsx.out.{}'.format(new_cid(8))
        self._zato_client_config.address = self.config['address']
        self._zato_client_config.on_request_callback = self.on_message_cb
        self._zato_client_config.on_closed_callback = self.on_close_cb
        self._zato_client_config.max_connect_attempts = self.config.get('max_connect_attempts', 1234567890)

        if self.config.get('username'):
            self._zato_client_config.username = self.config['username']
            self._zato_client_config.secret = self.config['secret']

        self._zato_client = _ZatoWSXClientImpl(self.opened, self.server, self._zato_client_config)
        self.invoke = self._zato_client.invoke
        self.send = self.invoke

# ################################################################################################################################

    def init(self) -> 'None':
        pass

# ################################################################################################################################

    def connect(self) -> 'None':
        # Not needed but added for API completeness.
        # The reason it is not needed is that self._zato_client's run_forever will connect itself.
        pass

# ################################################################################################################################

    def delete(self, reason:'str'='') -> 'None':
        self.close()

# ################################################################################################################################

    def close(self, reason:'str'='') -> 'None':
        self._zato_client.stop(reason)

# ################################################################################################################################

    def should_keep_running(self):
        return self._zato_client.keep_running

# ################################################################################################################################

    def check_is_connected(self):
        return self._zato_client.is_connected

# ################################################################################################################################

    def check_is_active(self):
        parent:'OutconnWSXWrapper' = self.config['parent']
        is_active = parent.check_is_active()
        return is_active

# ################################################################################################################################

    def on_outconn_stopped_running(self):
        parent:'OutconnWSXWrapper' = self.config['parent']
        parent.on_outconn_stopped_running()

# ################################################################################################################################

    def on_outconn_connected(self):
        parent:'OutconnWSXWrapper' = self.config['parent']
        parent.on_outconn_connected()

# ################################################################################################################################

    def get_subscription_list(self) -> 'strlist':

        # This is an initial, static list of topics to subscribe to ..
        subscription_list = (self.config['subscription_list'] or '').splitlines()

        # .. while the rest can be dynamically populated by services.
        on_subscribe_service_name = self.config.get('on_subscribe_service_name')

        if on_subscribe_service_name:
            topic_list = self.config['parent'].on_subscribe_cb(on_subscribe_service_name)

            if topic_list:
                _ = subscription_list.extend(topic_list)

        return subscription_list

# ################################################################################################################################

    def subscribe_to_topics(self) -> 'None':

        subscription_list = self.get_subscription_list()

        if subscription_list:
            logger.info('Subscribing WSX outconn `%s` to `%s`', self.config['name'], subscription_list)

            for topic_name in subscription_list:
                try:
                    self._zato_client.subscribe(topic_name)
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
