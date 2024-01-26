# -*- coding: utf-8 -*-

# flake8: noqa
# pylint: disable=all

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# PyZMQ
import zmq.green as zmq

# Zato
from zato.common.api import ZMQ
from zato.server.connection.connector import Connector

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class Base(Connector):
    """ Base class for ZeroMQ connections, both channels and outgoing ones, other than Majordomo (MDP).
    """
    def init_simple_socket(self):
        """ Initializes a ZeroMQ socket other than Majordomo one.
        """
        try:
            # Open a ZMQ socket and set its options, if required
            self.impl = self.ctx.socket(getattr(zmq, self.config.socket_type))

            if self.config.socket_type == ZMQ.SUB and self.config.sub_key:
                self.impl.setsockopt(zmq.SUBSCRIBE, self.config.sub_key)

            # Whether to bind or connect?
            socket_method = getattr(self.impl, self.config.socket_method)
            socket_method(self.config.address)

            # Notify parent class that we are connected now.
            self.is_connected = True

        except Exception:
            logger.warning('ZeroMQ socket could not be initialized, e:`%s`', format_exc())
            raise

    def _start(self):
        self.conn = self
        self.ctx = zmq.Context()

    def _send(self, msg, *args, **kwargs):
        raise NotImplementedError('Should be defined in subclasses')

    def _stop(self):
        self.impl.close(50) # TODO: Should be configurable

    def _get_log_details(self, address):
        return '{} {}'.format(self.config.socket_type, address)

    def get_prev_log_details(self):
        return self._get_log_details(self.config.prev_address if 'prev_address' in self.config else self.config.address)

    def get_log_details(self):
        return self._get_log_details(self.config.address)

# ################################################################################################################################
