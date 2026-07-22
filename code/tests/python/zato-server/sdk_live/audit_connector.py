# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import threading
import time

# Zato
from zato.common.sdk import Connector, Field

# ################################################################################################################################
# ################################################################################################################################

class AuditClient:
    """ A fire-and-forget sender for an audit collector - events are buffered client-side
    and flushed in batches, each batch over its own short-lived connection, so nothing is lost
    when the collector is briefly down.
    """
    def __init__(self, host:'str', port:'int', flush_interval:'int') -> 'None':
        self.host = host
        self.port = port
        self.flush_interval = flush_interval

        # Guards the buffer.
        self.lock = threading.Lock()

        # Events waiting for the next flush.
        self.buffer = []

        # Set by close, which stops the flusher loop.
        self.is_stopped = False

        # Flush periodically in the background.
        flusher_thread = threading.Thread(target=self._flush_loop, daemon=True)
        flusher_thread.start()

# ################################################################################################################################

    def _flush_loop(self) -> 'None':

        while not self.is_stopped:

            # Waiting in small slices makes close take effect quickly even with long intervals.
            waited = 0.0
            while waited < self.flush_interval and not self.is_stopped:
                time.sleep(0.1)
                waited += 0.1

            if self.is_stopped:
                return

            try:
                self.flush()
            except OSError:
                # The collector is down - the events stay in the buffer for the next flush.
                pass

# ################################################################################################################################

    def add(self, event:'str') -> 'None':
        with self.lock:
            self.buffer.append(event)

# ################################################################################################################################

    def flush(self) -> 'None':

        # Take the whole buffer under the lock ..
        with self.lock:
            batch = self.buffer[:]
            self.buffer.clear()

        # .. an empty batch means there is nothing to send.
        if not batch:
            return

        # .. and send it over one short-lived connection.
        payload = ''.join(f'{event}\n' for event in batch)

        try:
            with socket.create_connection((self.host, self.port)) as conn:
                conn.sendall(payload.encode('utf8'))
        except OSError:
            # The collector is down - put the batch back so nothing is lost.
            with self.lock:
                self.buffer[0:0] = batch
            raise

# ################################################################################################################################

    def close(self) -> 'None':
        """ Stops the flusher and sends whatever remains in the buffer - flush-on-stop.
        """
        self.is_stopped = True
        self.flush()

# ################################################################################################################################
# ################################################################################################################################

class AuditConnector(Connector):
    """ Wraps the audit collector as a connection type that services access through self.out.audit.
    """
    type = 'audit'

    # Configuration schema
    host = Field.Text()
    port = Field.Int(default=9990)
    flush_interval = Field.Int(default=2)

# ################################################################################################################################

    def create_client(self) -> 'AuditClient':
        out = AuditClient(self.config.host, self.config.port, self.config.flush_interval)
        return out

# ################################################################################################################################

    def ping(self, client:'AuditClient') -> 'None':

        # The collector never replies, so reaching it is the whole check.
        conn = socket.create_connection((client.host, client.port))
        conn.close()

# ################################################################################################################################

    def on_stop(self, client:'AuditClient') -> 'None':
        client.close()
        self.logger.info('Audit client flushed and closed for `%s`', self.name)

# ################################################################################################################################

    def send_event(self, event:'str') -> 'None':
        self.client.add(event)

# ################################################################################################################################
# ################################################################################################################################
