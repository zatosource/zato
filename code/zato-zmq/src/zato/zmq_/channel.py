# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent import spawn

# Zato
from zato.common import CHANNEL
from zato.common.util import new_cid
from zato.zmq_ import Base

# ################################################################################################################################

class Simple(Base):
    """ A ZeroMQ channel other than Majordomo.
    """
    start_in_greenlet = True

    def _start(self):
        super(Simple, self)._start()

        # Open a ZMQ socket and set its options, if required
        self.impl = self.ctx.socket(getattr(zmq, self.config.socket_type))

        if self.config.socket_type == ZMQ.SUB and self.config.sub_key:
            self.impl.setsockopt(zmq.SUBSCRIBE, self.config.sub_key)

        # Whether to bind or connect?
        socket_method = getattr(self.impl, self.config.socket_method)
        socket_method(self.config.address)

        # Micro-optimizations to make things faster
        _spawn = spawn
        _callback = self.callback
        _new_cid = new_cid
        _service = self.service
        _impl_recv = self.impl.recv
        _config = self.config
        _channel_zmq = CHANNEL.ZMQ

        # Run the main loop
        while self.keep_running:

            # Spawn a new greenlet for the callback invoking a service with data received from the socket on input
            _spawn(_callback, {
                'cid': _new_cid,
                'service': _service,
                'payload': _impl_recv(), # This line is blocking waiting for requests
                'zato_ctx': {'channel_config': _config}
            }, _channel_zmq, None)

    def _send(self, msg, *args, **kwargs):
        self.impl.send(msg, *args, **kwargs)

# ################################################################################################################################

class MDPv01(Base):
    """ An MDP (Majordomo) v0.1 ZeroMQ channel.
    """

# ################################################################################################################################