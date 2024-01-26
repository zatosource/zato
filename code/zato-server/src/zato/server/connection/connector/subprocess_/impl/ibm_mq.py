# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
from logging import DEBUG
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_ACCEPTABLE, OK, responses, SERVICE_UNAVAILABLE
from time import sleep
from traceback import format_exc

# Python 2/3 compatibility
from zato.common.py23_ import start_new_thread

# Zato
from zato.common.json_internal import dumps
from zato.server.connection.jms_wmq.jms import WebSphereMQException, NoMessageAvailableException
from zato.server.connection.jms_wmq.jms.connection import WebSphereMQConnection
from zato.server.connection.jms_wmq.jms.core import TextMessage
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response

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

_cc_failed = 2  # pymqi.CMQC.MQCC_FAILED
_rc_conn_broken = 2009  # pymqi.CMQC.MQRC_CONNECTION_BROKEN
_rc_not_authorized = 2035  # pymqi.CMQC.MQRC_NOT_AUTHORIZED
_rc_q_mgr_quiescing = 2161  # pymqi.CMQC.MQRC_Q_MGR_QUIESCING
_rc_host_not_available = 2538  # pymqi.CMQC.MQRC_HOST_NOT_AVAILABLE

# A list of reason codes upon which we will try to reconnect
_rc_reconnect_list = [_rc_conn_broken, _rc_q_mgr_quiescing, _rc_host_not_available]

# ################################################################################################################################

class _MessageCtx:
    __slots__ = ('mq_msg', 'channel_id', 'queue_name', 'service_name', 'data_format')

    def __init__(self, mq_msg, channel_id, queue_name, service_name, data_format):
        self.mq_msg = mq_msg
        self.channel_id = channel_id
        self.queue_name = queue_name
        self.service_name = service_name
        self.data_format = data_format

# ################################################################################################################################

class IBMMQChannel:
    """ A process to listen for messages from IBM MQ queue managers.
    """
    def __init__(self, conn, is_active, channel_id, queue_name, service_name, data_format, on_message_callback, logger):
        self.conn = conn
        self.is_active = is_active
        self.id = channel_id
        self.queue_name = queue_name
        self.service_name = service_name
        self.data_format = data_format
        self.on_message_callback = on_message_callback
        self.keep_running = True if is_active else False
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
        def _invoke_callback(msg_ctx):
            try:
                self.on_message_callback(msg_ctx)
            except Exception:
                self.logger.warning('Could not invoke message callback %s', format_exc())

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

                except NoMessageAvailableException:
                    if self.has_debug:
                        self.logger.debug('Consumer for queue `%s` did not receive a message. `%s`' % (
                            self.queue_name, self._get_destination_info(self.queue_name)))

                except self.pymqi.MQMIError as e:
                    if e.reason == self.pymqi.CMQC.MQRC_UNKNOWN_OBJECT_NAME:
                        self.logger.warning('No such queue `%s` found for %s', self.queue_name, self.conn.get_connection_info())
                    else:
                        self.logger.warning('%s in run, reason_code:`%s`, comp_code:`%s`' % (
                            e.__class__.__name__, e.reason, e.comp))

                    # In case of any low-level PyMQI error, sleep for some time
                    # because there is nothing we can do at this time about it.
                    self.logger.info('Sleeping for %ss', sleep_on_error)
                    sleep(sleep_on_error)

                except WebSphereMQException as e:

                    sleep(sleep_on_error)
                    conn_info = self.conn.get_connection_info()

                    # Try to reconnect if the reason code points to one that is of a transient nature
                    while self.keep_running and e.completion_code == _cc_failed and e.reason_code in _rc_reconnect_list:
                        try:
                            self.logger.warning('Reconnecting channel `%s` due to MQRC `%s` and MQCC `%s`',
                                conn_info, e.reason_code, e.completion_code)
                            self.conn.reconnect()
                            self.conn.ping()
                            break
                        except WebSphereMQException as exc:
                            e = exc
                            sleep(sleep_on_error)
                        except Exception:
                            self.logger.error('Stopping channel `%s` due to `%s`', conn_info, format_exc())
                            raise
                    else:
                        self.logger.error(
                            'Stopped channel `%s` due to MQRC `%s` and MQCC `%s`',
                            conn_info, e.reason_code, e.completion_code)
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

class IBMMQConnectionContainer(BaseConnectionContainer):

    has_prereqs = True
    connection_class = WebSphereMQConnection
    ipc_name = 'ibm-mq'
    conn_type = 'ibm_mq'
    logging_file_name = 'ibm-mq'

    def __init__(self):

        # PyMQI is an optional dependency so let's import it here rather than on module level
        try:
            import pymqi
        except ImportError:
            self.pymqi = None
        else:
            self.pymqi = pymqi

        # Call our parent to initialize everything
        super().__init__()

# ################################################################################################################################

    def check_prereqs_ready(self):
        return bool(self.pymqi)

# ################################################################################################################################

    def get_prereqs_not_ready_message(self):
        return 'PyMQI library could not be imported. Is PyMQI installed? Is ibm_mq set to True in server.conf?'

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
        # Require that PyMQI be available
        if not self.pymqi:
            return Response(_http_503, 'Could not find pymqi module, IBM MQ connections will not start')

        # Call our parent which will actually create the definition
        return super().on_definition_create(msg)

# ################################################################################################################################

    def _on_DEFINITION_WMQ_EDIT(self, msg):
        return super().on_definition_edit(msg)

# ################################################################################################################################

    def _on_DEFINITION_WMQ_DELETE(self, msg):
        return super().on_definition_delete(msg)

# ################################################################################################################################

    def _on_DEFINITION_WMQ_CHANGE_PASSWORD(self, msg):
        return super().on_definition_change_password(msg)

# ################################################################################################################################

    def _on_DEFINITION_WMQ_PING(self, msg):
        return super().on_definition_ping(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_DELETE(self, msg):
        return super().on_outgoing_delete(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_CREATE(self, msg):
        return super().on_outgoing_create(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_EDIT(self, msg):
        return super().on_outgoing_edit(msg)

# ################################################################################################################################

    def _on_CHANNEL_WMQ_CREATE(self, msg):
        return super().on_channel_create(msg)

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
            channel.keep_running = True if msg.is_active else False
            channel.start()

            return Response()

# ################################################################################################################################

    def _on_CHANNEL_WMQ_DELETE(self, msg):
        return super().on_channel_delete(msg)

# ################################################################################################################################

    def _on_OUTGOING_WMQ_SEND(self, msg, is_reconnect=False):
        """ Sends a message to a remote IBM MQ queue - note that the functionality is specific to IBM MQ
        and, consequently, it does not make use of any method in the parent class unlike, e.g. _on_CHANNEL_WMQ_DELETE.
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

                jms_correlation_id = msg.get('correlation_id', '')
                jms_message_id = msg.get('msg_id', '')
                jms_reply_to = msg.get('reply_to', '')

                if isinstance(jms_correlation_id, str):
                    jms_correlation_id = jms_correlation_id.encode('utf8')

                if isinstance(jms_message_id, str):
                    jms_message_id = jms_message_id.encode('utf8')

                if isinstance(jms_reply_to, str):
                    jms_reply_to = jms_reply_to.encode('utf8')

                text_msg = TextMessage(
                    text = msg.data,
                    jms_delivery_mode = delivery_mode,
                    jms_priority = priority,
                    jms_expiration = expiration,
                    jms_correlation_id = jms_correlation_id,
                    jms_message_id = jms_message_id,
                    jms_reply_to = jms_reply_to,
                )

                conn.send(text_msg, msg.queue_name)

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
                    self.logger.warning('Caught MQRC_CONNECTION_BROKEN in send, will try to reconnect connection to %s ',
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

            except Exception:
                return self._on_send_exception()

# ################################################################################################################################

    def _create_channel_impl(self, conn, msg):
        return IBMMQChannel(conn, msg.is_active, msg.id, msg.queue.encode('utf8'), msg.service_name, msg.data_format,
            self.on_mq_message_received, self.logger)

# ################################################################################################################################

if __name__ == '__main__':

    container = IBMMQConnectionContainer()
    container.run()

# ################################################################################################################################
