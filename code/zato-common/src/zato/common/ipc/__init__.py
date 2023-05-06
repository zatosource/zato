# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from logging import getLogger
from tempfile import gettempdir

# Zato
from zato.common.api import DATA_FORMAT, NO_DEFAULT_VALUE
from zato.common.util.api import make_repr, new_cid, spawn_greenlet

# ################################################################################################################################
# ################################################################################################################################

class Request:
    def __init__(self, publisher_tag, publisher_pid, payload='', request_id=None):
        self.publisher_tag = publisher_tag
        self.publisher_pid = publisher_pid
        self.action = NO_DEFAULT_VALUE
        self.service = ''
        self._payload = payload
        self.payload_type = type(payload).__name__
        self.data_format = DATA_FORMAT.DICT
        self.request_id = request_id or 'ipc.{}'.format(new_cid())
        self.target_pid = None
        self.reply_to_tag = ''
        self.reply_to_fifo = ''
        self.in_reply_to = ''
        self.socket = None
        self.creation_time_utc = datetime.utcnow()

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        self._payload = value
        self.payload_type = type(self._payload)

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################
# ################################################################################################################################

class IPCBase:
    """ Base class for core IPC objects.
    """
    def __init__(self, name:'str', pid:'int') -> 'None':

        # ZeroMQ
        import zmq.green as zmq

        self.name = name
        self.pid = pid
        self.ctx = zmq.Context()
        self.socket = None
        spawn_greenlet(self.set_up_sockets)
        self.keep_running = True
        self.logger = getLogger('zato')
        self.log_connected()

    def __repr__(self):
        return make_repr(self)

    def set_up_sockets(self) -> 'None':
        raise NotImplementedError('Needs to be implemented in subclasses')

    def log_connected(self) -> 'None':
        raise NotImplementedError('Needs to be implemented in subclasses')

    def close(self) -> 'None':
        raise NotImplementedError('Needs to be implemented in subclasses')

# ################################################################################################################################
# ################################################################################################################################

class IPCEndpoint(IPCBase):
    """ A participant in IPC conversations, i.e. either publisher or subscriber.
    """
    socket_method = '<invalid-socket_method>'
    socket_type = '<invalid-socket_type>'

    def __init__(self, name:'str', pid:'int') -> 'None':
        self.address = self.get_address(name)
        super(IPCEndpoint, self).__init__(name, pid)

    def get_address(self, address:'str') -> 'str':
        return 'ipc://{}'.format(os.path.join(gettempdir(), 'zato-ipc-{}'.format(address)))

    def set_up_sockets(self) -> 'None':

        # ZeroMQ
        import zmq.green as zmq

        _socket_type_name = self.socket_type.upper()
        _socket_type = getattr(zmq, _socket_type_name)

        self.socket = self.ctx.socket(_socket_type)
        self.socket.setsockopt(zmq.LINGER, 0)

        _socket_start_func = getattr(self.socket, self.socket_method)
        _socket_start_func(self.address)

    def log_connected(self) -> 'None':
        self.logger.info('Established %s/%s to %s (self.pid: %s)', self.socket_type, self.socket_method, self.address, self.pid)

    def close(self) -> 'None':
        self.keep_running = False
        self.socket.close()
        self.ctx.term()

# ################################################################################################################################
# ################################################################################################################################
