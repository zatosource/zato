# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
   Copyright 2006-2008 SpringSource (http://springsource.com), All Rights Reserved

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# stdlib
import logging
import os
import signal
import sys
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_ACCEPTABLE, OK, responses, SERVICE_UNAVAILABLE
from json import loads
from logging import DEBUG, Formatter, getLogger, StreamHandler
from logging.handlers import RotatingFileHandler
from os import getppid, path
from threading import RLock
from time import sleep
from traceback import format_exc
from wsgiref.simple_server import make_server

# Bunch
from bunch import bunchify

# Requests
from requests import post as requests_post

# YAML
import yaml

# Python 2/3 compatibility
from builtins import bytes
from six import PY2
from zato.common.py23_ import start_new_thread

# Zato
from zato.common.broker_message import code_to_name
from zato.common.util import parse_cmd_line_options
from zato.common.util.auth import parse_basic_auth
from zato.common.util.json_ import dumps
from zato.common.util.posix_ipc_ import ConnectorConfigIPC
from zato.server.connection.jms_wmq.jms import WebSphereMQException, NoMessageAvailableException
from zato.server.connection.jms_wmq.jms.connection import WebSphereMQConnection
from zato.server.connection.jms_wmq.jms.core import TextMessage
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, get_logging_config

# ################################################################################################################################

logger_zato = logging.getLogger('zato')

# ################################################################################################################################

_http_200 = '{} {}'.format(OK, responses[OK])
_http_400 = '{} {}'.format(BAD_REQUEST, responses[BAD_REQUEST])
_http_403 = '{} {}'.format(FORBIDDEN, responses[FORBIDDEN])
_http_406 = '{} {}'.format(NOT_ACCEPTABLE, responses[NOT_ACCEPTABLE])
_http_500 = '{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
_http_503 = '{} {}'.format(SERVICE_UNAVAILABLE, responses[SERVICE_UNAVAILABLE])

_path_api = '/api'
_path_ping = '/ping'
_paths = (_path_api, _path_ping)

_cc_failed         = 2    # pymqi.CMQC.MQCC_FAILED
_rc_conn_broken    = 2009 # pymqi.CMQC.MQRC_CONNECTION_BROKEN
_rc_not_authorized = 2035 # pymqi.CMQC.MQRC_NOT_AUTHORIZED

# ################################################################################################################################

class Response(object):
    def __init__(self, status=_http_200, data=b'', content_type='text/json'):
        self.status = status
        self.data = data
        self.content_type = content_type

# ################################################################################################################################

class _MessageCtx(object):
    __slots__ = ('mq_msg', 'channel_id', 'queue_name', 'service_name', 'data_format')

    def __init__(self, mq_msg, channel_id, queue_name, service_name, data_format):
        self.mq_msg = mq_msg
        self.channel_id = channel_id
        self.queue_name = queue_name
        self.service_name = service_name
        self.data_format = data_format

# ################################################################################################################################

class IBMMQChannel(object):
    """ A process to listen for messages from IBM MQ queue managers.
    """
    def __init__(self, conn, channel_id, queue_name, service_name, data_format, on_message_callback, logger):
        self.conn = conn
        self.id = channel_id
        self.queue_name = queue_name
        self.service_name = service_name
        self.data_format = data_format
        self.on_message_callback = on_message_callback
        self.keep_running = False
        self.logger = logger
        self.has_debug = self.logger.isEnabledFor(DEBUG)

        # PyMQI is an optional dependency so let's import it here rather than on module level
        import pymqi
        self.pymqi = pymqi

# ################################################################################################################################

    def _get_destination_info(self):
        return 'destination:`%s`, %s' % (self.queue_name, self.conn.get_connection_info())

# ################################################################################################################################

    def start(self, sleep_on_error=3, _connection_closing='zato.connection.closing'):
        """ Runs a background queue listener in its own  thread.
        """
        self.keep_running = True

        def _invoke_callback(msg_ctx):
            try:
                self.on_message_callback(msg_ctx)
            except Exception:
                self.logger.warn('Could not invoke message callback %s', format_exc())

        def _impl():
            while self.keep_running:
                try:
                    msg = self.conn.receive(self.queue_name, 100)
                    if self.has_debug:
                        self.logger.debug('Message received `%s`' % str(msg).decode('utf-8'))

                    if msg == _connection_closing:
                        self.logger.info('Received request to quit, closing channel for queue `%s` (%s)',
                            self.queue_name, self.conn.get_connection_info())
                        self.keep_running = False
                        return

                    if msg:
                        start_new_thread(_invoke_callback, (
                            _MessageCtx(msg, self.id, self.queue_name, self.service_name, self.data_format),))

                except NoMessageAvailableException as e:
                    if self.has_debug:
                        self.logger.debug('Consumer for queue `%s` did not receive a message. `%s`' % (
                            self.queue_name, self._get_destination_info(self.queue_name)))

                except self.pymqi.MQMIError as e:
                    if e.reason == self.pymqi.CMQC.MQRC_UNKNOWN_OBJECT_NAME:
                        self.logger.warn('No such queue `%s` found for %s', self.queue_name, self.conn.get_connection_info())
                    else:
                        self.logger.warn('%s in run, reason_code:`%s`, comp_code:`%s`' % (
                            e.__class__.__name__, e.reason, e.comp))

                    # In case of any low-level PyMQI error, sleep for some time
                    # because there is nothing we can do at this time about it.
                    self.logger.info('Sleeping for %ss', sleep_on_error)
                    sleep(sleep_on_error)

                except WebSphereMQException as e:
                    # If current connection is broken we may try to re-estalish it.
                    sleep(sleep_on_error)

                    if e.completion_code == _cc_failed and e.reason_code == _rc_conn_broken:
                        self.logger.warn('Caught MQRC_CONNECTION_BROKEN in receive, will try to reconnect connection to %s ',
                            self.conn.get_connection_info())
                        self.conn.reconnect()
                        self.conn.ping()
                    else:
                        raise

                except Exception as e:
                    self.logger.error('Exception in the main loop %r %s %s', e.args, type(e), format_exc())
                    sleep(sleep_on_error)

        # Start listener in a thread
        start_new_thread(_impl, ())

# ################################################################################################################################

    def stop(self):
        self.keep_running = False

# ################################################################################################################################
# ################################################################################################################################

class IBMMQConnectionContainer(object):
    def __init__(self):

        # PyMQI is an optional dependency so let's import it here rather than on module level
        try:
            import pymqi
        except ImportError:
            self.pymqi = None
        else:
            self.pymqi = pymqi

        # Call our parent to initialize everything
        super(IBMMQConnectionContainer, self).__init__()

# ################################################################################################################################

    def on_mq_message_received(self, msg_ctx):
        return self._post({
            'msg': msg_ctx.mq_msg.to_dict(),
            'channel_id': msg_ctx.channel_id,
            'queue_name': msg_ctx.queue_name,
            'service_name': msg_ctx.service_name,
            'data_format': msg_ctx.data_format,
            })

# ################################################################################################################################

    def _on_DEFINITION_WMQ_CREATE(self, msg):
        """ Creates a new connection to IBM MQ.
        """
        if not self.pymqi:
            return Response(_http_503, 'Could not find pymqi module, IBM MQ connections will not start')

        with self.lock:
            try:
                self._create_definition(msg)
            except Exception as e:
                self.logger.warn(format_exc())
                return Response(_http_503, str(e.message))
            else:
                return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_EDIT(self, msg):
        """ Updates an existing definition - close the current one, including channels and outconns,
        and creates a new one in its place.
        """
        with self.lock:
            def_id = msg.id
            old_conn = self.connections[def_id]

            # Edit messages don't carry passwords
            msg.password = old_conn.password

            # It's possible that we are editing a connection that has no connected yet,
            # e.g. if password was invalid, so this needs to be guarded by an if.
            if old_conn.is_connected:
                self.connections[def_id].close()

            # Overwrites the previous connection object
            new_conn = self._create_definition(msg, old_conn.is_connected)

            # Stop and start all channels using this definition.
            for channel_id, _def_id in self.channel_id_to_def_id.items():
                if def_id == _def_id:
                    channel = self.channels[channel_id]
                    channel.stop()
                    channel.conn = new_conn
                    channel.start()

            return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_DELETE(self, msg):
        """ Deletes an IBM MQ MQ definition along with its associated outconns and channels.
        """
        with self.lock:
            def_id = msg.id

            # Stop all connections ..
            try:
                self.connections[def_id].close()
            except Exception:
                self.logger.warn(format_exc())
            finally:
                try:
                    del self.connections[def_id]
                except Exception:
                    self.logger.warn(format_exc())

                # .. continue to delete outconns regardless of errors above ..
                for outconn_id, outconn_def_id in self.outconn_id_to_def_id.items():
                    if outconn_def_id == def_id:
                        del self.outconn_id_to_def_id[outconn_id]
                        del self.outconns[outconn_id]

                # .. delete channels too.
                for channel_id, channel_def_id in self.channel_id_to_def_id.items():
                    if channel_def_id == def_id:
                        del self.channel_id_to_def_id[channel_id]
                        del self.channels[channel_id]

            return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_CHANGE_PASSWORD(self, msg):
        with self.lock:
            try:
                conn = self.connections[msg.id]
                conn.close()
                conn.password = str(msg.password)
                conn.connect()
            except Exception as e:
                self.logger.warn(format_exc())
                return Response(_http_503, str(e.message), 'text/plain')
            else:
                return Response()

# ################################################################################################################################

    def _on_DEFINITION_WMQ_PING(self, msg):
        """ Pings a remote IBM MQ manager.
        """
        try:
            self.connections[msg.id].ping()
        except WebSphereMQException as e:
            return Response(_http_503, str(e.message), 'text/plain')
        else:
            return Response()

# ################################################################################################################################

    def _on_OUTGOING_WMQ_DELETE(self, msg):
        """ Deletes an existing IBM MQ outconn.
        """
        with self.lock:
            self._delete_outconn(msg)
            return Response()

# ################################################################################################################################

    def _on_OUTGOING_WMQ_CREATE(self, msg):
        """ Creates a new IBM MQ outgoin connections using an already existing definition.
        """
        with self.lock:
            return self._create_outconn(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_EDIT(self, msg):
        """ Updates and existing outconn by deleting and creating it again with latest configuration.
        """
        with self.lock:
            self._delete_outconn(msg, msg.old_name)
            return self._create_outconn(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_SEND(self, msg, is_reconnect=False):
        """ Sends a message to a remote IBM MQ queue.
        """
        with self.lock:
            outconn_id = msg.get('id') or self.outconn_name_to_id[msg.outconn_name]
            outconn = self.outconns[outconn_id]

        if not outconn.is_active:
            return Response(_http_406, 'Cannot send messages through an inactive connection', 'text/plain')
        else:
            def_id = self.outconn_id_to_def_id[outconn_id]
            conn = self.connections[def_id]
            conn.ping()

            try:

                delivery_mode = msg.delivery_mode or outconn.delivery_mode
                priority = msg.priority or outconn.priority
                expiration = msg.expiration or outconn.expiration

                text_msg = TextMessage(
                    text = msg.data,
                    jms_delivery_mode = delivery_mode,
                    jms_priority = priority,
                    jms_expiration = expiration,
                    jms_correlation_id = msg.get('correlation_id', '').encode('utf8'),
                    jms_message_id = msg.get('msg_id', '').encode('utf8'),
                    jms_reply_to = msg.get('reply_to', '').encode('utf8'),
                )

                conn.send(text_msg, msg.queue_name.encode('utf8'))
                return Response(data=dumps(text_msg.to_dict(False)))

            except(self.pymqi.MQMIError, WebSphereMQException) as e:

                if isinstance(e, self.pymqi.MQMIError):
                    cc_code = e.comp
                    reason_code = e.reason
                else:
                    cc_code = e.completion_code
                    reason_code = e.reason_code

                # Try to reconnect if the connection is broken but only if we have not tried to already
                if (not is_reconnect) and cc_code == _cc_failed and reason_code == _rc_conn_broken:
                    self.logger.warn('Caught MQRC_CONNECTION_BROKEN in send, will try to reconnect connection to %s ',
                        conn.get_connection_info())

                    # Sleep for a while before reconnecting
                    sleep(1)

                    # Try to reconnect
                    conn.reconnect()

                    # Confirm it by pinging the queue manager
                    conn.ping()

                    # Resubmit the request
                    return self._on_OUTGOING_WMQ_SEND(msg, is_reconnect=True)
                else:
                    return self._on_send_exception()

            except Exception as e:
                return self._on_send_exception()


# ################################################################################################################################

    def _create_channel_impl(self, conn, msg):
        return IBMMQChannel(conn, msg.id, msg.queue.encode('utf8'), msg.service_name, msg.data_format,
            self.on_mq_message_received, self.logger)

# ################################################################################################################################

    def _on_CHANNEL_WMQ_CREATE(self, msg):
        """ Creates a new background channel listening for messages from a given queue.
        """
        with self.lock:
            conn = self.connections[msg.def_id]
            channel = self._create_channel_impl(conn, msg)
            channel.start()
            self.channels[channel.id] = channel
            self.channel_id_to_def_id[channel.id] = msg.def_id
            return Response()

# ################################################################################################################################

    def _on_CHANNEL_WMQ_EDIT(self, msg):
        """ Updates an IBM MQ MQ channel by stopping it and starting again with a new configuration.
        """
        with self.lock:
            channel = self.channels[msg.id]
            channel.stop()
            channel.queue_name = msg.queue.encode('utf8')
            channel.service_name = msg.service_name
            channel.data_format = msg.data_format
            channel.keep_running = True
            channel.start()

            return Response()

# ################################################################################################################################

    def _on_CHANNEL_WMQ_DELETE(self, msg):
        """ Stops and deletes a background channel.
        """
        with self.lock:
            channel = self.channels[msg.id]
            channel.keep_running = False

            del self.channels[channel.id]
            del self.channel_id_to_def_id[channel.id]

# ################################################################################################################################

if __name__ == '__main__':

    container = IBMMQConnectionContainer()
    container.run()

# ################################################################################################################################

