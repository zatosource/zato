# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A replication barrier that answers each request the way the active-standby node does once the standby stored
# every commit, and records each request, for the tests of the connections of a replicated Zato database.

# stdlib
import os
import socket
from contextlib import contextmanager
from threading import Event, Lock, Thread

# Zato
from zato.common.ha.common import ModuleCtx as HACtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Iterator

    Iterator = Iterator

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The name of the socket in the directory of a test
    Socket_Name = 'barrier.sock'

    # The answer of the node once the standby stored every commit
    Answer_OK = b'ok\n'

    # How many connections may wait to be accepted
    Backlog = 16

    # How long accepting a connection waits before the server checks whether to stop, in seconds
    Accept_Timeout = 0.2

# ################################################################################################################################
# ################################################################################################################################

class RecordingBarrier:
    """ Answers each barrier request with `ok` and counts the requests.
    """

    def __init__(self, socket_path:'str') -> 'None':
        self.socket_path = socket_path
        self._lock = Lock()
        self._request_count = 0
        self._stop_event = Event()

        self._server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server.bind(socket_path)
        self._server.listen(ModuleCtx.Backlog)
        self._server.settimeout(ModuleCtx.Accept_Timeout)

        self._thread = Thread(target=self._serve, daemon=True)

# ################################################################################################################################

    @property
    def request_count(self) -> 'int':
        with self._lock:
            out = self._request_count
        return out

# ################################################################################################################################

    def _answer(self, connection:'socket.socket') -> 'None':
        with connection:
            request = connection.recv(1)
            if request:
                with self._lock:
                    self._request_count += 1
                connection.sendall(ModuleCtx.Answer_OK)

# ################################################################################################################################

    def _serve(self) -> 'None':
        while not self._stop_event.is_set():
            try:
                connection, _ = self._server.accept()
            except TimeoutError:
                continue

            self._answer(connection)

# ################################################################################################################################

    def start(self) -> 'None':
        self._thread.start()

    def stop(self) -> 'None':
        self._stop_event.set()
        self._thread.join()
        self._server.close()
        os.remove(self.socket_path)

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def replicated_environment(directory:'str') -> 'Iterator[RecordingBarrier]':
    """ Makes this process an active-standby environment that replicates its SQLite Zato database, with the barrier
    of the node answered by a recording barrier, and restores the environment afterwards.
    """
    socket_path = os.path.join(directory, ModuleCtx.Socket_Name)

    names = (HACtx.Env_Mode, HACtx.Env_Barrier_Socket)
    previous = {name: os.environ.get(name) for name in names}

    os.environ[HACtx.Env_Mode] = HACtx.Mode_Active_Standby
    os.environ[HACtx.Env_Barrier_Socket] = socket_path

    barrier = RecordingBarrier(socket_path)
    barrier.start()

    try:
        yield barrier
    finally:
        barrier.stop()

        for name, value in previous.items():
            if value is None:
                _ = os.environ.pop(name, None)
            else:
                os.environ[name] = value

# ################################################################################################################################
# ################################################################################################################################
