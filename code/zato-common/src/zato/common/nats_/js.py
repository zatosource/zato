# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from typing import TYPE_CHECKING

# Zato
from zato.common.typing_ import anydict, anydictnone, anylist, floatnone, intnone, strnone

# Local
from .const import JS_Ack, JS_API_Consumer_Create, JS_API_Consumer_Create_Durable, JS_API_Consumer_Delete, \
     JS_API_Consumer_Info, JS_API_Consumer_Msg_Next, JS_API_Stream_Create, JS_API_Stream_Delete, \
     JS_API_Stream_Info, JS_API_Stream_Purge, JS_Nak, JS_Progress, JS_Term, Nanoseconds_Per_Second, \
     Status_Conflict, Status_Control, Status_No_Messages, Status_Timeout
from .exc import NATSError, NATSJetStreamError, NATSTimeoutError
from .model import ConsumerConfig, ConsumerInfo, Msg, PubAck, StreamConfig, StreamInfo

if TYPE_CHECKING:
    from .client import NATSClient

# ################################################################################################################################
# ################################################################################################################################

class JetStream:
    """ JetStream context for a NATS client.
    """
    def __init__(self, client:'NATSClient') -> None:
        self._client = client

    # ############################################################################################################################

    def publish(
        self,
        subject:'str',
        payload:'bytes'=b'',
        timeout:'floatnone'=None,
        headers:'anydictnone'=None,
        msg_id:'strnone'=None,
        expected_stream:'strnone'=None,
        expected_last_seq:'intnone'=None,
    ) -> 'PubAck':
        """ Publishes a message to JetStream and waits for an acknowledgment.
        """
        if timeout is None:
            timeout = self._client._timeout

        hdr = headers or {}
        if msg_id:
            hdr['Nats-Msg-Id'] = msg_id
        if expected_stream:
            hdr['Nats-Expected-Stream'] = expected_stream
        if expected_last_seq is not None:
            hdr['Nats-Expected-Last-Sequence'] = str(expected_last_seq)

        msg = self._client.request(subject, payload, timeout=timeout, headers=hdr if hdr else None)

        data = msg.data.decode('utf-8')
        resp = json.loads(data)
        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return PubAck.from_dict(resp)

    # ############################################################################################################################

    def create_stream(self, config:'StreamConfig', timeout:'floatnone'=None) -> 'StreamInfo':
        """ Creates a JetStream stream.
        """
        if not config.name:
            raise NATSError('Stream name is required')

        subject = JS_API_Stream_Create.format(stream=config.name)
        payload = json.dumps(config.to_dict())
        payload = payload.encode('utf-8')

        msg = self._client.request(subject, payload, timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return StreamInfo.from_dict(resp)

    # ############################################################################################################################

    def delete_stream(self, stream:'str', timeout:'floatnone'=None) -> 'bool':
        """ Deletes a JetStream stream.
        """
        subject = JS_API_Stream_Delete.format(stream=stream)
        msg = self._client.request(subject, b'', timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return resp['success']

    # ############################################################################################################################

    def stream_info(self, stream:'str', timeout:'floatnone'=None) -> 'StreamInfo':
        """ Returns information about a JetStream stream.
        """
        subject = JS_API_Stream_Info.format(stream=stream)
        msg = self._client.request(subject, b'', timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return StreamInfo.from_dict(resp)

    # ############################################################################################################################

    def purge_stream(self, stream:'str', timeout:'floatnone'=None) -> 'int':
        """ Purges messages from a JetStream stream. Returns the number of purged messages.
        """
        subject = JS_API_Stream_Purge.format(stream=stream)
        msg = self._client.request(subject, b'', timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return resp['purged']

    # ############################################################################################################################

    def create_consumer(
        self,
        stream:'str',
        config:'ConsumerConfig',
        timeout:'floatnone'=None,
    ) -> 'ConsumerInfo':
        """ Creates a JetStream consumer.
        """
        if config.durable_name:
            subject = JS_API_Consumer_Create_Durable.format(stream=stream, consumer=config.durable_name)
        else:
            subject = JS_API_Consumer_Create.format(stream=stream)

        payload = json.dumps({
            'stream_name': stream,
            'config': config.to_dict(),
        })
        payload = payload.encode('utf-8')

        msg = self._client.request(subject, payload, timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return ConsumerInfo.from_dict(resp)

    # ############################################################################################################################

    def delete_consumer(self, stream:'str', consumer:'str', timeout:'floatnone'=None) -> 'bool':
        """ Deletes a JetStream consumer.
        """
        subject = JS_API_Consumer_Delete.format(stream=stream, consumer=consumer)
        msg = self._client.request(subject, b'', timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return resp['success']

    # ############################################################################################################################

    def consumer_info(self, stream:'str', consumer:'str', timeout:'floatnone'=None) -> 'ConsumerInfo':
        """ Returns information about a JetStream consumer.
        """
        subject = JS_API_Consumer_Info.format(stream=stream, consumer=consumer)
        msg = self._client.request(subject, b'', timeout=timeout)
        data = msg.data.decode('utf-8')
        resp = json.loads(data)

        if err := resp.get('error'):
            raise NATSJetStreamError(
                code=err['code'],
                err_code=err['err_code'],
                description=err['description'],
            )

        return ConsumerInfo.from_dict(resp)

    # ############################################################################################################################

    def fetch(
        self,
        stream:'str',
        consumer:'str',
        batch:'int'=1,
        timeout:'floatnone'=None,
        no_wait:'bool'=False,
    ) -> 'anylist':
        """ Fetches messages from a JetStream consumer.
        """
        if timeout is None:
            timeout = self._client._timeout

        subject = JS_API_Consumer_Msg_Next.format(stream=stream, consumer=consumer)

        inbox = self._client.new_inbox()
        sub = self._client.subscribe(inbox, max_msgs=batch)

        try:
            # Build fetch request
            req = {'batch': batch}
            if timeout:
                req['expires'] = int(timeout * Nanoseconds_Per_Second)
            if no_wait:
                req['no_wait'] = True

            req_data = json.dumps(req)
            req_data = req_data.encode('utf-8')
            self._client.publish(subject, req_data, reply=inbox)

            msgs = []
            while len(msgs) < batch:
                try:
                    msg = sub.next_msg(timeout=timeout)

                    # Check for status message
                    if msg.headers:
                        status = msg.headers.get('Status')
                        if status == Status_No_Messages:
                            break
                        elif status == Status_Timeout:
                            break
                        elif status == Status_Conflict:
                            continue
                        elif status == Status_Control:
                            # Heartbeat
                            continue

                    msgs.append(msg)
                except NATSTimeoutError:
                    break

            return msgs
        finally:
            try:
                sub.unsubscribe()
            except Exception:
                pass

    # ############################################################################################################################

    def ack(self, msg:'Msg') -> None:
        """ Acknowledges a JetStream message.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')
        self._client.publish(msg.reply, JS_Ack)

    # ############################################################################################################################

    def nak(self, msg:'Msg', delay:'floatnone'=None) -> None:
        """ Negatively acknowledges a JetStream message.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')

        if delay:
            delay_data = json.dumps({'delay': int(delay * Nanoseconds_Per_Second)})
            delay_data = delay_data.encode('utf-8')
            self._client.publish(msg.reply, JS_Nak + b' ' + delay_data)
        else:
            self._client.publish(msg.reply, JS_Nak)

    # ############################################################################################################################

    def in_progress(self, msg:'Msg') -> None:
        """ Marks a JetStream message as in progress, extending the ack deadline.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')
        self._client.publish(msg.reply, JS_Progress)

    # ############################################################################################################################

    def term(self, msg:'Msg') -> None:
        """ Terminates a JetStream message - it will not be redelivered.
        """
        if not msg.reply:
            raise NATSError('Message has no reply subject for acknowledgment')
        self._client.publish(msg.reply, JS_Term)

# ################################################################################################################################
# ################################################################################################################################
