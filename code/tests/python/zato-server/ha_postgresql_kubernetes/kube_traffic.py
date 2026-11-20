# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The client of a failover. It sends a request to the Service of the pair every 10 ms over one keep-alive connection,
# as a client of a production installation does, and records the time and the outcome of each request. A connection
# is replaced by a new one after every error.

# stdlib
import logging
import socket
import threading
import time
from dataclasses import dataclass
from http.client import HTTPConnection, HTTPException, OK

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.traffic')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often a request is sent, in seconds
    Request_Interval = 0.01

    # How long one request may take before the client abandons its connection, in seconds
    Client_Timeout = 2.0

    # How long the thread of the client may take to end once it is stopped, in seconds
    Stop_Timeout = Client_Timeout * 2

    # The endpoint that the server of the active pod answers through the Service
    Path = '/zato/ping'

    # The outcomes of a request
    Outcome_OK      = 'ok'
    Outcome_Refused = 'refused'
    Outcome_Reset   = 'reset'
    Outcome_Timeout = 'timeout'
    Outcome_Error   = 'error'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RequestRecord:
    """ One request of the client, with the wall-clock times at which it was sent and ended, and the number
    of the connection that it was sent over.
    """
    sent: 'float'
    ended: 'float'
    outcome: 'str'
    connection_number: 'int'
    detail: 'str'

# ################################################################################################################################
# ################################################################################################################################

record_list = list[RequestRecord]

# ################################################################################################################################
# ################################################################################################################################

class FailoverClient:
    """ Sends requests to the Service of the pair over one keep-alive connection until it is stopped.
    """

    def __init__(self, host:'str', port:'int') -> 'None':
        self.host = host
        self.port = port
        self.records:'record_list' = []
        self._lock = threading.Lock()
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._run, name='failover-client', daemon=True)

    def start(self) -> 'None':
        self._thread.start()
        logger.info('Failover client started -> %s:%s', self.host, self.port)

    def stop(self) -> 'None':
        self._stopped.set()
        self._thread.join(ModuleCtx.Stop_Timeout)
        assert not self._thread.is_alive(), 'Failover client did not stop'

    def get_records(self) -> 'record_list':
        with self._lock:
            out = list(self.records)
        return out

# ################################################################################################################################

    def _send(self, connection:'HTTPConnection') -> 'tuple[str, str]':
        """ Sends one request over the connection and returns its outcome with a detail of an error.
        """
        try:
            connection.request('GET', ModuleCtx.Path)
            response = connection.getresponse()
            _ = response.read()

        # A port that no pod listens on behind the Service ..
        except ConnectionRefusedError as error:
            out = (ModuleCtx.Outcome_Refused, repr(error))

        # .. a connection that the other side ended ..
        except (ConnectionResetError, BrokenPipeError) as error:
            out = (ModuleCtx.Outcome_Reset, repr(error))

        # .. a request that no answer arrived for ..
        except (socket.timeout, TimeoutError) as error:
            out = (ModuleCtx.Outcome_Timeout, repr(error))

        # .. and any other failure, which the test reports in full.
        except (HTTPException, OSError) as error:
            out = (ModuleCtx.Outcome_Error, repr(error))

        else:
            if response.status == OK:
                out = (ModuleCtx.Outcome_OK, '')
            else:
                out = (ModuleCtx.Outcome_Error, f'HTTP {response.status}')

        return out

# ################################################################################################################################

    def _run(self) -> 'None':

        connection:'HTTPConnection | None' = None
        connection_number = 0

        while not self._stopped.is_set():

            # A connection is opened before the first request and after each error ..
            if connection is None:
                connection = HTTPConnection(self.host, self.port, timeout=ModuleCtx.Client_Timeout)
                connection_number += 1

            # .. the request is sent and timed ..
            record = RequestRecord()
            record.connection_number = connection_number
            record.sent = time.time()

            record.outcome, record.detail = self._send(connection)
            record.ended = time.time()

            # .. a connection that failed is not reused ..
            if record.outcome != ModuleCtx.Outcome_OK:
                connection.close()
                connection = None

            with self._lock:
                self.records.append(record)

            # .. and the next request follows after the interval.
            _ = self._stopped.wait(ModuleCtx.Request_Interval)

        if connection is not None:
            connection.close()

# ################################################################################################################################
# ################################################################################################################################
