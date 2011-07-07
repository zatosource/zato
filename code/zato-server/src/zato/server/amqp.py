# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

'''
from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
import logging
from uuid import uuid4
from threading import RLock, Thread

# Pika
import pika

# Circuits
from circuits.core.workers import Process

class Client(Process):
    def __init__(self, conn_params=None, server_type=None):
        self.logger = logging.getLogger("%s.%s:%s" % (__name__, self.__class__.__name__, hex(id(self))))
        self.server_type = server_type

        self.conn = pika.BlockingConnection(conn_params)
        self.ch = self.conn.channel()
        self.stats = {}
        self._stats_lock = RLock()
        self._looping = False # We're not consuming any AMQP messages on startup.

        super(Client, self).__init__()

    def run(self):
        self.ipc_queue = multiprocessing.Queue()
        notifier = _IPCNotifier(self.ipc_queue, self.on_ipc_message)
        notifier.setDaemon(True)
        notifier.start()

        self.logger.debug("AMQP client starting [%s] [%s]" % (self.server_type, self.ipc_queue))

        self.ipc_queue.put("q1")
        #self.ipc_queue.put("q2")

        #self.listen("q1")
        #self.listen("q2")
        pass

    def on_ipc_message(self, msg):
        """ Handler for IPC messages read from self.ipc_queue (defined in self.loop).
        """
        self.logger.log(TRACE1, "on_ipc_message [%s] [%s]" % (msg, self.server_type))

        self.listen(msg)

    def _on_config_message(self, msg):
        """ Handler for AMQP configuration messages.
        """
        self.logger.log(TRACE1, "_on_config_message [%s] [%s]" % (msg, self.server_type))

    def on_message(self, channel, method, header, body):
        """ Handler for AMQP messages.
        """
        self.logger.log(TRACE1, "on_message [%s] [%s] [%s] [%s] [%s]" % (channel,
                    method, header, body, self.server_type))
        self.ch.basic_ack(delivery_tag=method.delivery_tag)

    def listen(self, queue_name, durable=False, exclusive=False, auto_delete=False):

        consumer_tag = "zato." + uuid4().hex
        self.logger.log(TRACE1, "listen [%s] [%s] [%s] [%s] [%s]" % (queue_name,
                    durable, exclusive, auto_delete, consumer_tag))

        self.ch.queue_declare(queue=queue_name, durable=durable, exclusive=exclusive, auto_delete=auto_delete)
        self.ch.basic_consume(self.on_message, queue=queue_name, consumer_tag=consumer_tag)

        #if not self._looping:
        self.conn.mainloop()
        #    self._looping = True
'''

'''
def _get_key_value_config(arguments):
    out = {}
    for line in arguments:
        k, v = line.strip().split("=")
        out[k.strip()] = v.strip()

    return out

def key_value_config(f):
    def wrapper(self, arguments):
        arguments = _get_key_value_config(arguments)
        return f(self, arguments)

    return wrapper


class ThreadedClient(Thread):
    def __init__(self, conn_params=None, loop_on_start=False):
        super(ThreadedClient, self).__init__()
        self.conn_params = conn_params
        self.loop_on_start = loop_on_start
        self.keep_running = True
        self.daemon = True

        self.logger = logging.getLogger("%s.%s:%s" % (__name__, self.__class__.__name__, hex(id(self))))

    def on_started(self):
        """ May be overridden by subclasses, will get called right before
        entering the mainloop.
        """

    def on_message(self, channel, method, header, body):
        """ A handler for incoming AMQP messages. Must be overridden by subclasses.
        """
        raise NotImplementedError("Must be overridden by subclasses.")

    def listen(self, queue_name, callback=None, durable=False, exclusive=False, auto_delete=True):
        self.channel.queue_declare(queue=queue_name, durable=durable,
                                   exclusive=exclusive, auto_delete=auto_delete)
        self.channel.basic_consume(callback, queue=queue_name, consumer_tag=uuid4().hex)

        msg = ("Will now listen on queue=[%s], durable=[%s], "
               "exclusive=[%s], auto_delete=[%s].") % (queue_name, durable, exclusive, auto_delete)
        self.logger.debug(msg)

    def publish(self, exchange, routing_key, body, declare=False, declare_args=[False, False, True]):
        if declare:
            durable, exclusive, auto_delete = declare_args
            self.channel.queue_declare(queue=routing_key, durable=durable,
                                       exclusive=exclusive, auto_delete=auto_delete)
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)

    def run(self):

        # Delay connecting after the thread have been started.
        self.conn = pika.AsyncoreConnection(self.conn_params)
        self.channel = self.conn.channel()

        self.on_started()

        if self.loop_on_start:
            self.loop()

    def loop(self):
        """ Runs the main Pika event loop.
        """
        self.logger.debug("Starting the AMQP listener loop.")
        #self.conn.drain_events()
        asyncore.loop()

class CircuitsProxy(Component):
    """ A circuits component which delegates all the AMQP work to a separate
    thread.
    """
    def __init__(self, **kwargs):
        self._init_kwargs = kwargs
        super(CircuitsProxy, self).__init__()

    def started(self, component, mode):
        self.client = _ParallelServerConfigClient(**self._init_kwargs)
        self.client.start()

class ThreadedConfigClient(ThreadedClient):
    def __init__(self, server_type=None, conn_params=None, loop_on_start=False):
        self.server_type = server_type
        super(ThreadedConfigClient, self).__init__(conn_params, loop_on_start)

    def on_message(self, channel, method, header, body):
        self.logger.debug("Message received [%s] [%s] [%s] [%s] [%s]" % (os.getpid(), channel, method, header, body))
        self.channel.basic_ack(delivery_tag = method.delivery_tag)

        body = body.splitlines()
        command, arguments = body[0], body[1:]

        try:
            handler = getattr(self, "on_" + command)
        except AttributeError, e:
            self.logger.error("Unrecognized command=[%s], arguments=[%s], "
                              "body=[%s]" % (command, arguments, body))
        else:
            handler(arguments)


    def get_client_queue_name(self):
        """ Returns the name of a queue this particular client will be listening on,
        must be overridden by subclasses.
        """
        raise NotImplementedError("Must be overridden by subclasses.")

    def on_started(self):
        self.listen(self.get_client_queue_name(), self.on_message, exclusive=True)

################################################################################

class _ParallelServer(object):
    """ Parallel server as seen from the SingletonServerConfigClient perspective.
    """
    def __init__(self, queue_name=None):
        self.queue_name = queue_name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<%s at %s, queue_name=[%s]>" % (self.__class__.__name__, hex(id(self)), self.queue_name)

class ParallelServerConfigClient(CircuitsProxy):
    """ Proxies everything to the super-class or to the actual config client.
    """
    def __getattr__(self, attr):
        return getattr(self.client, attr)

class _ParallelServerConfigClient(ThreadedConfigClient):
    """ The actual configuration client working on behalf of a parallel server.
    """
    def __init__(self, **kwargs):
        server_type = kwargs["server_type"]
        conn_params = kwargs["conn_params"]
        loop_on_start = kwargs["loop_on_start"]
        super(_ParallelServerConfigClient, self).__init__(server_type, conn_params, loop_on_start)

    def get_client_queue_name(self):
        return "zato.config.%s.1.%s.%s" % (self.server_type, os.getpid(), uuid4().hex)

    def on_started(self):
        # Call the super-class first.
        super(_ParallelServerConfigClient, self).on_started()

        # Let's introduce ourselves to the singleton server.
        body = "REGISTER_PARALLEL_SERVER\nqueue_name=" + self.get_client_queue_name()
        self.publish("", "zato.config.single.1", body, declare=True)

    def request_reply(self, body, timeout):
        response = None
        def _on_message(channel, method, header, body):
            raise AttributeError()

        queue_name = "zato.%s" % uuid4().hex
        self.listen(queue_name, _on_message)
        #self.publish("", "zato.config.single.1", "ABC", declare=True)


class SingletonServerConfigClient(ThreadedConfigClient):
    """ A singleton server's configuration client.
    """
    def __init__(self, *args, **kwargs):
        self.parallel_servers = []
        super(SingletonServerConfigClient, self).__init__(*args, **kwargs)

    def get_client_queue_name(self):
        return "zato.config.single.1"

    @key_value_config
    def on_REGISTER_PARALLEL_SERVER(self, arguments):
        self.logger.debug("arguments=[%s]" % arguments)

        queue_name = arguments["queue_name"]
        ps = _ParallelServer(queue_name)
        self.parallel_servers.append(ps)
'''
