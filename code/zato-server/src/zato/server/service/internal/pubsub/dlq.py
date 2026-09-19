# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQ actions of outgoing connections and the DLQ rule.

# stdlib
from datetime import datetime, timedelta
from functools import partial
from json import dumps, loads
from logging import getLogger

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.facade import PubSubFacade
from zato.common.pubsub.dlq import get_dlq_topic_name, Header_Moved_Time, Header_Rounds, Key_DLQ, parse_dlq_sub_key, \
    strip_dlq_header
from zato.common.pubsub.outgoing import Attempts_None, find_outgoing_conn, get_dlq_settings, Key_CID, Key_Request, \
    locate_outgoing_conn, OutgoingPublisher
from zato.common.util.time_ import utcnow
from zato.server.service import Bool
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_dlq = HTTP_SOAP.DLQ

_pending = 'pending'

# ################################################################################################################################
# ################################################################################################################################

class _DLQService(AdminService):
    """ What every DLQ action has in common.
    """

    def _get_dlq_names(self, sub_key:'str') -> 'tuple[str, int, str]':
        """ The connection type and id a DLQ belongs to and the name of the DLQ's topic.
        """
        conn_type, conn_id = parse_dlq_sub_key(sub_key)
        conn_name, _ = locate_outgoing_conn(self.server, conn_type, conn_id)

        topic_name = get_dlq_topic_name(conn_type, conn_name)

        out = (conn_type, conn_id, topic_name)
        return out

# ################################################################################################################################

    def _load_message(self, topic_name:'str', msg_id:'str') -> 'stranydict':
        """ One DLQ message's document.
        """
        details = self.server.pubsub_backend.get_message_details(topic_name, msg_id)

        if not details:
            raise Exception(f'No such DLQ message `{msg_id}` in `{topic_name}`')

        out = loads(details['data'])
        return out

# ################################################################################################################################

    def _get_all_documents(self, topic_name:'str', sub_key:'str') -> 'anylist':
        """ Every message a DLQ holds, oldest first, each as its id and its document.
        """
        messages, _ = self.server.pubsub_backend.browse_messages(topic_name, sub_key, _pending, needs_data=True)

        out:'anylist' = []

        for message in messages:
            out.append((message['msg_id'], loads(message['data'])))

        return out

# ################################################################################################################################

    def _ack(self, sub_key:'str', msg_id:'str') -> 'None':
        """ Takes one message out of the DLQ.
        """
        _ = self.server.pubsub_backend.ack_message(sub_key, msg_id)

# ################################################################################################################################

    def _act_on_all(self, sub_key:'str', act:'callable_') -> 'anydict':
        """ Runs one action on every message a DLQ holds, returning how many.
        """
        _, _, topic_name = self._get_dlq_names(sub_key)
        count = 0

        while True:
            documents = self._get_all_documents(topic_name, sub_key)

            if not documents:
                break

            for msg_id, document in documents:
                act(sub_key, msg_id, document)
                count += 1

        out = {'sub_key': sub_key, 'count': count}
        return out

# ################################################################################################################################
# ################################################################################################################################

class _RetryMixin(_DLQService):

    def _retry(self, sub_key:'str', msg_id:'str', document:'stranydict') -> 'str':
        """ Puts one DLQ message back at the end of its connection's queue, returning its new id.
        """
        conn_type, conn_id, _ = self._get_dlq_names(sub_key)

        rounds = document[Key_DLQ][Header_Rounds] + 1
        envelope = strip_dlq_header(document)

        publisher = OutgoingPublisher(self.server, conn_type, conn_id)
        result = publisher.publish_request(envelope[Key_CID], Attempts_None, envelope[Key_Request], dlq_rounds=rounds)

        self._ack(sub_key, msg_id)

        logger.info('Retried DLQ message `%s` of `%s` as `%s`, round %d', msg_id, sub_key, result.msg_id, rounds)

        out = result.msg_id
        return out

# ################################################################################################################################

class RetryMessage(_RetryMixin):
    """ Puts one message from the DLQ of an outgoing connection back at the end of the connection's queue.
    """
    name  = 'zato.pubsub.dlq.retry-message'
    input = 'sub_key', 'msg_id'

    def handle(self) -> 'None':
        sub_key = self.request.input.sub_key
        msg_id = self.request.input.msg_id

        _, _, topic_name = self._get_dlq_names(sub_key)
        document = self._load_message(topic_name, msg_id)

        new_msg_id = self._retry(sub_key, msg_id, document)

        self.response.payload = {'msg_id': msg_id, 'new_msg_id': new_msg_id}

# ################################################################################################################################

class RetryAllMessages(_RetryMixin):
    """ Puts every message from the DLQ of an outgoing connection back at the end of the connection's queue, oldest first.
    """
    name  = 'zato.pubsub.dlq.retry-all-messages'
    input = 'sub_key'

    def handle(self) -> 'None':
        self.response.payload = self._act_on_all(self.request.input.sub_key, self._retry)

# ################################################################################################################################
# ################################################################################################################################

class _ForwardMixin(_DLQService):

    def _forward(self, sub_key:'str', msg_id:'str', document:'stranydict', topic_name:'str', keep_header:'bool') -> 'None':
        """ Publishes one DLQ message to a topic and takes it out of the DLQ.
        """
        if keep_header:
            to_publish = document
        else:
            to_publish = strip_dlq_header(document)

        pubsub = PubSubFacade(self.server, PubSub.Outgoing.Delivery_Service)
        _ = pubsub.publish(topic_name, dumps(to_publish), cid=document[Key_CID])

        self._ack(sub_key, msg_id)

        logger.info('Forwarded DLQ message `%s` of `%s` to `%s`, header kept:%s', msg_id, sub_key, topic_name, keep_header)

# ################################################################################################################################

class ForwardMessage(_ForwardMixin):
    """ Publishes one message from the DLQ of an outgoing connection to a topic.
    """
    name  = 'zato.pubsub.dlq.forward-message'
    input = 'sub_key', 'msg_id', 'topic_name', Bool('keep_header')

    def handle(self) -> 'None':
        sub_key = self.request.input.sub_key
        msg_id = self.request.input.msg_id

        topic_name = self.request.input.topic_name
        keep_header = self.request.input.keep_header

        _, _, dlq_topic_name = self._get_dlq_names(sub_key)
        document = self._load_message(dlq_topic_name, msg_id)

        self._forward(sub_key, msg_id, document, topic_name, keep_header)

        self.response.payload = {'msg_id': msg_id, 'topic_name': topic_name}

# ################################################################################################################################

class ForwardAllMessages(_ForwardMixin):
    """ Publishes every message from the DLQ of an outgoing connection to a topic, oldest first.
    """
    name  = 'zato.pubsub.dlq.forward-all-messages'
    input = 'sub_key', 'topic_name', Bool('keep_header')

    def handle(self) -> 'None':
        topic_name = self.request.input.topic_name
        keep_header = self.request.input.keep_header

        act = partial(self._forward, topic_name=topic_name, keep_header=keep_header)

        self.response.payload = self._act_on_all(self.request.input.sub_key, act)

# ################################################################################################################################
# ################################################################################################################################

class _DiscardMixin(_DLQService):

    def _discard(self, sub_key:'str', msg_id:'str', document:'stranydict') -> 'None':
        """ Takes one message out of the DLQ.
        """
        self._ack(sub_key, msg_id)

        logger.info('Discarded DLQ message `%s` of `%s`', msg_id, sub_key)

# ################################################################################################################################

class DiscardMessage(_DiscardMixin):
    """ Discards one message from the DLQ of an outgoing connection.
    """
    name  = 'zato.pubsub.dlq.discard-message'
    input = 'sub_key', 'msg_id'

    def handle(self) -> 'None':
        sub_key = self.request.input.sub_key
        msg_id = self.request.input.msg_id

        _, _, topic_name = self._get_dlq_names(sub_key)
        document = self._load_message(topic_name, msg_id)

        self._discard(sub_key, msg_id, document)

        self.response.payload = {'msg_id': msg_id}

# ################################################################################################################################

class DiscardAllMessages(_DiscardMixin):
    """ Discards every message from the DLQ of an outgoing connection.
    """
    name  = 'zato.pubsub.dlq.discard-all-messages'
    input = 'sub_key'

    def handle(self) -> 'None':
        self.response.payload = self._act_on_all(self.request.input.sub_key, self._discard)

# ################################################################################################################################
# ################################################################################################################################

class GetQueueList(AdminService):
    """ One row per outgoing connection that has a queue or a DLQ.
    """
    name = 'zato.pubsub.outgoing.get-queue-list'

    def handle(self) -> 'None':
        self.response.payload = {'items': self.server.config_manager.get_outgoing_queue_list()}

# ################################################################################################################################
# ################################################################################################################################

class DLQRun(_RetryMixin, _ForwardMixin, _DiscardMixin):
    """ The DLQ rule - carries out each outgoing connection's DLQ action on the messages in its DLQ.
    """
    name = PubSub.Outgoing.DLQ_Rule_Service

    def handle(self) -> 'None':
        now = utcnow()
        counts:'anydict' = {}

        for sub_key in self.server.config_manager.get_outgoing_dlq_sub_keys():

            conn_type, conn_id = parse_dlq_sub_key(sub_key)
            found = find_outgoing_conn(self.server, conn_type, conn_id)

            if not found:
                continue

            conn_name, wrapper = found
            settings = get_dlq_settings(conn_type, wrapper)

            if not settings:
                continue

            action = settings[_dlq.Field_Action]

            if action == _dlq.Action.Keep:
                continue

            count = self._run_for_connection(sub_key, conn_type, conn_name, settings, now)

            if count:
                counts[conn_name] = count

        if counts:
            logger.info('DLQ rule acted on %s', counts)

        self.response.payload = {'counts': counts}

# ################################################################################################################################

    def _run_for_connection(self, sub_key:'str', conn_type:'str', conn_name:'str', settings:'stranydict', now:'datetime') -> 'int':
        """ Carries out one connection's DLQ action on every due message of its DLQ, returning how many.
        """
        action = settings[_dlq.Field_Action]
        interval = timedelta(seconds=settings[_dlq.Field_Retry_Interval])
        max_rounds = settings[_dlq.Field_Retries]
        forward_to = settings[_dlq.Field_Forward_To]
        keep_header = settings[_dlq.Field_Keep_Header]

        if action == _dlq.Action.Forward and not forward_to:
            logger.warning('DLQ rule cannot forward from `%s` - the connection `%s` has no topic to forward to', sub_key, conn_name)
            return 0

        topic_name = get_dlq_topic_name(conn_type, conn_name)
        count = 0

        for msg_id, document in self._get_all_documents(topic_name, sub_key):
            header = document[Key_DLQ]

            moved_time = datetime.fromisoformat(header[Header_Moved_Time])

            if now - moved_time < interval:
                continue

            if action == _dlq.Action.Retry:

                if header[Header_Rounds] >= max_rounds:
                    continue

                _ = self._retry(sub_key, msg_id, document)

            elif action == _dlq.Action.Forward:
                self._forward(sub_key, msg_id, document, forward_to, keep_header)

            else:
                self._discard(sub_key, msg_id, document)

            count += 1

        return count

# ################################################################################################################################
# ################################################################################################################################
