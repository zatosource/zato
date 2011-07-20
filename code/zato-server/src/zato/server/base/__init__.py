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

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
import time
import json
import logging
from uuid import uuid4
from Queue import Empty
from threading import Thread
from cStringIO import StringIO
from traceback import format_exc
from multiprocessing import connection, Queue as _Queue

# Zato
from zato.common.util import TRACE1
from zato.common import ZatoException, ZATO_NOT_GIVEN, ZATO_CONFIG_REQUEST, \
     ZATO_CONFIG_RESPONSE, ZATO_ERROR, ZATO_OK

logger = logging.getLogger("zatoserver.server:%s" % os.getpid())

def _get_key_value_config(arguments):
    logger.log(TRACE1, "_get_key_value_config arguments=[%s]" % arguments)
    out = {}
    for line in arguments:
        if line:
            k, v = line.strip().split("=", 1)
            out[k.strip()] = v.strip()
    return out

def Queue(queue_id=None):
    """ Adds a unique identifier to stdlib's multiprocessing.Queue which is used
    in correlating IPC requests & responses.
    """
    q = _Queue()
    q.queue_id = queue_id

    return q

class IPCMessage(object):
    """ Represents string messages sent between server IPC queues.
    """
    def __init__(self, msg_type=None, command=None, msg_id=None,
                 in_reply_to_msg_id=ZATO_NOT_GIVEN, reply_to_queue=ZATO_NOT_GIVEN,
                 result=ZATO_NOT_GIVEN, params=None):
        self.msg_type = msg_type
        self.command = command
        self.msg_id = msg_id
        self.in_reply_to_msg_id = in_reply_to_msg_id
        self.reply_to_queue = reply_to_queue
        self.result = result
        self.params = params

    def __str__(self):
        buff = StringIO()
        buff.write(self.msg_type)
        buff.write("command=%s\n" % self.command)
        buff.write("msg_id=%s\n" % self.msg_id)
        buff.write("in_reply_to_msg_id=%s\n" % self.in_reply_to_msg_id)
        buff.write("result=%s\n" % self.result)
        buff.write("reply_to_queue=%s\n" % self.reply_to_queue)
        if self.params:
            for k, v, in sorted(self.params.items()):
                buff.write("%s=%s\n" % (k, v))

        value = buff.getvalue()
        buff.close()

        return value

def ipc_message_from_string(payload):
    logger.log(TRACE1, "ipc_message_from_string1 payload=[%s]" % payload)

    payload = payload.split("\n")
    msg_type, payload = payload[0], payload[1:]
    args = _get_key_value_config(payload)

    logger.log(TRACE1, "ipc_message_from_string2 args=[%s]" % args)

    msg = IPCMessage()
    msg.msg_type = msg_type + "\n"
    msg.command = args.pop("command")
    msg.msg_id = args.pop("msg_id")
    msg.in_reply_to_msg_id = args.pop("in_reply_to_msg_id", ZATO_NOT_GIVEN)
    msg.reply_to_queue = args.pop("reply_to_queue", ZATO_NOT_GIVEN)
    msg.result = args.pop("result", ZATO_NOT_GIVEN)

    # Anything left are custom parameters.
    logger.log(TRACE1, "ipc_message_from_string3 args=[%s]" % args)
    msg.params = {}
    for k, v in args.items():
        logger.log(TRACE1, "ipc_message_from_string4 k=[%s], v=[%s]" % (k, v))
        msg.params[k] = v

    return msg


class IPCNotifier(Thread):
    """ A thread for each server's configuration queue which notifies the server
    about incoming config messages.
    """
    def __init__(self, queue=None, callback=None):
        self.logger = logging.getLogger("%s.%s:%s" % (__name__, self.__class__.__name__, hex(id(self))))
        self.queue = queue
        self.callback = callback
        self.tick = 0.05 # TODO: Make it a configurable option.

        super(IPCNotifier, self).__init__()

    def run(self):
        self.logger.log(TRACE1, "IPC notifier starting, queue=[%s]." % self.queue)

        # TODO: Use select.select on self.queue._reader here
        # (and don't forget about Windows).

        while True:
            try:
                data = self.queue.get(True, self.tick)
            except Empty, e:
                pass
            else:
                if self.logger.isEnabledFor(TRACE1):
                    self.logger.log(TRACE1, "run, data=[%s], callback=[%s]" % (data, self.callback))
                self.callback(data)

class BaseServer(object):
    """ A base class upon which singleton and parallel servers are created.
    """
    
    def __init__(self, parallel_server=None):
        self.parallel_server = parallel_server

    def _create_ipc_notifiers(self):
        # Will pick up messages from server's IPC queues.

        self.ipc_request_notifier = IPCNotifier(self.request_queue, self.on_ipc_request)
        self.ipc_request_notifier.daemon = True
        self.ipc_request_notifier.start()

        self.ipc_response_notifier = IPCNotifier(self.response_queue, self.on_ipc_response)
        self.ipc_response_notifier.daemon = True
        self.ipc_response_notifier.start()

    def on_ipc_request(self, msg):

        def _create_ipc_response_message(request_msg, result, response):
            if request_msg.reply_to_queue != ZATO_NOT_GIVEN:
                self.logger.log(TRACE1, "on_ipc_message2 [%s] [%s]." % (
                    request_msg.reply_to_queue, bool(request_msg.reply_to_queue)))

                response_msg = IPCMessage(ZATO_CONFIG_RESPONSE, request_msg.command)
                response_msg.msg_id = uuid4().hex
                response_msg.in_reply_to_msg_id = request_msg.msg_id
                response_msg.params = {}
                response_msg.result = result
                response_msg.params["response"] = response

                response = str(response_msg)

                if self.logger.isEnabledFor(TRACE1):
                    self.logger.log(TRACE1, "on_ipc_message3 response=[%s]" % (response))

                return response

        try:
            self.logger.log(TRACE1, "on_ipc_message1 [%s]." % msg)
            if msg.startswith(ZATO_CONFIG_REQUEST):
                msg = ipc_message_from_string(msg)
                result, response = self._on_config_message(msg)
                response = _create_ipc_response_message(msg, result, response)
            else:
                err_msg = "Unrecognized IPC message [%r]." % msg
                self.logger.error(err_msg)
                raise ZatoException(err_msg)
        except Exception, e:
            err_msg = "Caught an exception [%s]." % format_exc()
            self.logger.error(err_msg)
            response = None
            try:
                # Could be that call to 'ipc_message_from_string' failed
                # and 'msg' is still a string.
                if isinstance(msg, IPCMessage):
                    response = _create_ipc_response_message(msg, ZATO_ERROR, json.dumps(err_msg))
            except Exception, e:
                err_msg = "Could not create a response message [%s]." % format_exc()
                self.logger.error(err_msg)
        finally:
            if response:
                # There has been a response returned which implies one has
                # been requested, so we were sure passed a reply to queue name.
                response_queue = self.partner_response_queues[msg.reply_to_queue]

                self.logger.log(TRACE1, "Found a partner response queue=[%s]" % response_queue.queue_id)

                response_queue.put(response)

    def on_ipc_response(self, msg):
        """ Invoked by the IPCNotifier when a response from the SingletonServer
        is available. Inserts the response into a dictionary of responses from
        which it is read by the requesting function/method.
        """
        if self.logger.isEnabledFor(TRACE1):
            self.logger.log(TRACE1, "on_ipc_message1 [%s]" % msg)

        if msg.startswith(ZATO_CONFIG_RESPONSE):
            msg = ipc_message_from_string(msg)
            if msg.in_reply_to_msg_id:
                self._config_responses[msg.in_reply_to_msg_id] = str(msg)
                if self.logger.isEnabledFor(TRACE1):
                    self.logger.log(TRACE1, "on_ipc_message2 self._config_responses=[%s]" % self._config_responses)
        else:
            self.logger.error("Unrecognized IPC message [%r]." % msg)

    def _create_ipc_config_request(self, command, data=None):
        request = IPCMessage(ZATO_CONFIG_REQUEST, command)
        if data:
            request.params = {}
            request.params["data"] = json.dumps(data)

        return request

    def _send_config_request(self, msg, queue, timeout=None):
        return self._send_config_message(msg, queue, timeout)

    def _send_config_message(self, msg, queue, timeout=None):
        """ A blocking call to the other server's config queue, either time outs
        or gets a response for the config request from  self._config_responses.
        """
        # Append additional attributes and send the request away..
        msg.msg_id = uuid4().hex

        # .. timeout means we are interested in a response.
        if timeout:
            self.logger.log(TRACE1, "Assigning the reply_to_queue=[%s]" % self.response_queue.queue_id)
            msg.reply_to_queue = self.response_queue.queue_id

        queue.put(str(msg))

        if timeout:
            end_time = time.time() + timeout
            it = self._spin(end_time, msg.msg_id)
            while True:
                try:
                    it.next()
                except StopIteration, e:
                    response = self._config_responses.get(msg.msg_id)
                    if not response:
                        err_msg = "No response to the config message, " \
                              "timeout=[%s]s, msg=[%s]" % (timeout, msg)
                        self.logger.error(err_msg)
                        return ZATO_ERROR, json.dumps(err_msg)
                    else:
                        if self.logger.isEnabledFor(TRACE1):
                            self.logger.log(TRACE1, "_send_config_message response=[%s]" % response)
                        response = ipc_message_from_string(response)

                        # TODO: How about making it thread-safe? Is it needed?
                        del self._config_responses[msg.msg_id]

                        params_response = response.params["response"]
                        if params_response:
                            params_response = json.loads(params_response)
                        return response.result, params_response

    def _spin(self, end_time, msg_id):
        while time.time() <= end_time:
            if self._config_responses.get(msg_id):
                raise StopIteration()
            else:
                time.sleep(0.01)
                yield True

    def _on_config_message(self, msg):
        """ Invokes an appropriate handler of one of the base classes.
        """
        if self.logger.isEnabledFor(TRACE1):
            self.logger.log(TRACE1, "_on_config_message1 [%s]" % msg)

        handler = getattr(self, "_on_config_" + msg.command, None)
        if not handler:
            err_msg = "No handler for command [%s], msg=[%s]" % (msg.command, msg)
            self.logger.error(err_msg)
            raise ZatoException(err_msg)

        # Call the appropriate handler.
        result, response = handler(msg)

        if self.logger.isEnabledFor(TRACE1):
            self.logger.log(TRACE1, "_on_config_message2 result=[%s], response=[%s]" % (result, response))
        return result, response