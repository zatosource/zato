# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import itertools
import socket
import threading

# Zato
from zato.common.sdk import Connector, ConnectionLost, Field

# ################################################################################################################################
# ################################################################################################################################

class PaymentsClient:
    """ A client for a payment switch that multiplexes many in-flight requests over one persistent
    socket - each request carries a correlation ID, replies can arrive in any order and a reader
    loop matches them back to the calls that wait for them (ISO 8583, FIX style).
    """
    def __init__(self, host:'str', port:'int') -> 'None':

        # The one socket all the requests share.
        self.socket = socket.create_connection((host, port))
        self.reader_file = self.socket.makefile('r', encoding='utf8')

        # Guards the pending map and writes to the shared socket.
        self.lock = threading.Lock()

        # Calls in flight, keyed by their correlation IDs.
        self.pending = {}

        # Where the correlation IDs come from.
        self.counter = itertools.count(1)

        # Set to False by the reader loop once the socket is gone.
        self.is_connected = True

        # The reader loop matches replies back to waiting calls for as long as the connection lives.
        reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        reader_thread.start()

# ################################################################################################################################

    def _read_loop(self) -> 'None':

        for line in self.reader_file:
            text = line.strip()
            corr_id, _, payload = text.partition(' ')

            # The call this reply belongs to may have given up already, e.g. it timed out.
            with self.lock:
                holder = self.pending.pop(corr_id, None)

            if holder:
                holder['response'] = payload
                holder['event'].set()

        # The loop ended, which means the socket is gone - wake up everyone still waiting.
        self.is_connected = False

        with self.lock:
            for holder in self.pending.values():
                holder['event'].set()
            self.pending.clear()

# ################################################################################################################################

    def request(self, payload:'str') -> 'str':

        # A dead socket cannot carry anything - the framework will reconnect.
        if not self.is_connected:
            raise ConnectionLost('The payment switch connection is down')

        corr_id = str(next(self.counter))
        holder = {'event': threading.Event(), 'response': None}

        # Register the call and send its request under one lock, so the reply cannot
        # arrive before the call is registered.
        with self.lock:
            self.pending[corr_id] = holder
            self.socket.sendall(f'{corr_id} {payload}\n'.encode('utf8'))

        # Wait for the reader loop to match the reply back to this call.
        _ = holder['event'].wait()

        # A wake-up without a response means the connection died while this call was in flight.
        if holder['response'] is None:
            raise ConnectionLost('The payment switch connection went down mid-call')

        return holder['response']

# ################################################################################################################################

    def close(self) -> 'None':
        self.reader_file.close()
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

class PaymentsConnector(Connector):
    """ Wraps the payment switch as a connection type that services access through self.out.payments.
    """
    type = 'payments'

    # Configuration schema
    host = Field.Text()
    port = Field.Int(default=9970)

# ################################################################################################################################

    def create_client(self) -> 'PaymentsClient':
        out = PaymentsClient(self.config.host, self.config.port)
        self.logger.info('Payments client connected for `%s`', self.name)
        return out

# ################################################################################################################################

    def ping(self, client:'PaymentsClient') -> 'None':
        _ = client.request('ping')

# ################################################################################################################################

    def on_stop(self, client:'PaymentsClient') -> 'None':
        client.close()
        self.logger.info('Payments client closed for `%s`', self.name)

# ################################################################################################################################

    def authorize(self, payload:'str') -> 'str':
        out = self.client.request(payload)
        return out

# ################################################################################################################################
# ################################################################################################################################
