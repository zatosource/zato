# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import threading

# Zato
from zato.common.sdk import ConnectionLost, Field, SubscribingConnector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the feed to confirm a subscription or answer a ping, in seconds.
_reply_timeout = 5

# ################################################################################################################################
# ################################################################################################################################

class FeedClient:
    """ A client for a data feed that pushes messages on its own - after subscribing, the feed
    sends messages whenever it wants and a reader loop hands each one to the on_message callback.
    """
    def __init__(self, host:'str', port:'int', on_message:'any_') -> 'None':

        # Where pushed messages go.
        self.on_message = on_message

        # The one persistent socket the feed pushes into.
        self.socket = socket.create_connection((host, port))
        self.reader_file = self.socket.makefile('r', encoding='utf8')

        # Set when the feed confirms the subscription and answers a ping, respectively.
        self.subscribed_event = threading.Event()
        self.pong_event = threading.Event()

        # Set to False by the reader loop once the socket is gone.
        self.is_connected = True

        reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        reader_thread.start()

# ################################################################################################################################

    def _read_loop(self) -> 'None':

        for line in self.reader_file:
            text = line.strip()

            # A message the feed pushed on its own.
            if text.startswith('push '):
                self.on_message(text[len('push '):])

            # The feed confirmed our subscription.
            elif text == 'subscribed':
                self.subscribed_event.set()

            # The feed answered a ping.
            elif text == 'pong':
                self.pong_event.set()

        # The loop ended, which means the socket is gone.
        self.is_connected = False

# ################################################################################################################################

    def _send_line(self, data:'str') -> 'None':
        self.socket.sendall(f'{data}\n'.encode('utf8'))

# ################################################################################################################################

    def subscribe(self, topic:'str') -> 'None':
        self.subscribed_event.clear()
        self._send_line(f'subscribe {topic}')

        if not self.subscribed_event.wait(_reply_timeout):
            raise ConnectionLost('The feed did not confirm the subscription')

# ################################################################################################################################

    def ping(self) -> 'None':

        # A dead socket cannot answer - the framework will reconnect.
        if not self.is_connected:
            raise ConnectionLost('The feed connection is down')

        self.pong_event.clear()
        self._send_line('ping')

        if not self.pong_event.wait(_reply_timeout):
            raise ConnectionLost('The feed did not answer a ping')

# ################################################################################################################################

    def close(self) -> 'None':
        self.reader_file.close()
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

class FeedConnector(SubscribingConnector):
    """ Wraps the data feed as a connection type - received messages are handed over to a service
    with self.invoke and published to a topic with self.publish, and after every reconnect
    the framework calls on_started again, which resubscribes.
    """
    type = 'feed'

    # Configuration schema
    host = Field.Text()
    port = Field.Int(default=9980)
    topic = Field.Text()

    # The service that receives each pushed message and the pub/sub topic each one is published to.
    service = Field.Text()
    topic_name = Field.Text()

# ################################################################################################################################

    def create_client(self) -> 'FeedClient':
        out = FeedClient(self.config.host, self.config.port, self._handle_message)
        return out

# ################################################################################################################################

    def _handle_message(self, message:'str') -> 'None':

        # Hand the message over to a service (6.8) ..
        _ = self.invoke(self.config.service, {'message': message})

        # .. and publish it to a topic too.
        _ = self.publish(self.config.topic_name, message)

# ################################################################################################################################

    def ping(self, client:'FeedClient') -> 'None':
        client.ping()

# ################################################################################################################################

    def on_started(self, client:'FeedClient') -> 'None':
        client.subscribe(self.config.topic)
        self.logger.info('Feed `%s` subscribed to `%s`', self.name, self.config.topic)

# ################################################################################################################################

    def on_stop(self, client:'FeedClient') -> 'None':
        client.close()
        self.logger.info('Feed client closed for `%s`', self.name)

# ################################################################################################################################
# ################################################################################################################################
