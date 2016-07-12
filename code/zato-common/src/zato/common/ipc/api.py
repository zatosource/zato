# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import errno
import logging
import os
import stat
import tempfile
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent import sleep

# pyrapidjson
from rapidjson import loads

# Zato
from zato.common.ipc.forwarder import Forwarder
from zato.common.ipc.publisher import Publisher
from zato.common.ipc.subscriber import Subscriber
from zato.common.util import spawn_greenlet

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

fifo_create_mode = stat.S_IRUSR | stat.S_IWUSR
fifo_ignore_err = errno.EAGAIN, errno.EWOULDBLOCK

# ################################################################################################################################

class IPCAPI(object):
    """ API through which IPC is performed.
    """
    def __init__(self, is_forwarder, name=None, on_message_callback=None, pid=None):
        self.is_forwarder = is_forwarder
        self.name = name
        self.on_message_callback = on_message_callback
        self.pid = pid

    def run(self):

        if self.is_forwarder:
            spawn_greenlet(Forwarder, self.name, self.pid)
        else:
            self.publisher = Publisher(self.name, self.pid)
            self.subscriber = Subscriber(self.on_message_callback, self.name, self.pid)
            spawn_greenlet(self.subscriber.serve_forever)

    def publish(self, payload):
        self.publisher.publish(payload)

    def invoke_by_pid(self, service, payload, target_pid, fifo_response_buffer_size, timeout=5, fifo_ignore_err=fifo_ignore_err):
        """ Synchronously invokes a service through IPC. If target_pid is an exact PID then this one worker process
        will be invoked if it exists at all.
        """
        target_pid = self.pid

        # Create a FIFO pipe to receive replies to come through
        fifo_path = os.path.join(tempfile.tempdir, 'zato-ipc-fifo-{}'.format(uuid4().hex))
        os.mkfifo(fifo_path, fifo_create_mode)

        logger.warn('4433 %s', fifo_path)

        try:
            response = None
            self.publisher.publish(payload, service, target_pid, reply_to_fifo=fifo_path)

            try:
                # Open the pipe for reading ..
                fifo = os.open(fifo_path, os.O_RDONLY|os.O_NONBLOCK)

                # .. wait for response ..
                sleep(0.2)

                # .. and obtain it.
                response = os.read(fifo, fifo_response_buffer_size)

                if response is not None:
                    response = loads(response)

            except OSError, e:
                if e.errno not in fifo_ignore_err:
                    logger.warn('zzz %s', e)
                    raise
            finally:
                os.close(fifo)

            logger.warn('aaaa `%s`', response)

            return response

        except Exception, e:
            logger.warn(format_exc(e))
        finally:
            os.remove(fifo_path)

# ################################################################################################################################
