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
from zato.common.pubsub.delivery import DeliveryExhausted
from zato.common.pubsub.dlq import get_dlq_topic_name, Header_Moved_Time, Header_Rounds, Header_Rule_Rounds, Header_Source, \
    Header_Source_Topic, Key_DLQ, move_to_dlq, parse_dlq_sub_key, strip_dlq_header
from zato.common.pubsub.outgoing import Attempts_None, deliver_envelope, find_outgoing_conn, get_dlq_settings, has_queue, \
    Key_Attempts, Key_CID, Key_DLQ_Rounds, Key_DLQ_Rule_Rounds, Key_Request, locate_outgoing_conn, OutgoingPublisher
from zato.common.util.time_ import utcnow
from zato.server.service import Bool
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, stranydict, strnone

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

    def _claim(self, sub_key:'str', msg_id:'str') -> 'bool':
        """ Takes one message out of the DLQ, telling whether it was still there to be taken out.
        """
        out = self.server.pubsub_backend.claim_message(sub_key, msg_id)
        return out

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

    def _retry(self, sub_key:'str', msg_id:'str', document:'stranydict', *, is_rule_retry:'bool'=False) -> 'strnone':
        """ Tries one DLQ message again, returning its new id in the queue or the DLQ, an empty string if it was delivered,
        or None if another retry had already taken it out of the DLQ.
        """
        conn_type, conn_id, _ = self._get_dlq_names(sub_key)

        header = document[Key_DLQ]
        rounds = header[Header_Rounds] + 1
        rule_rounds = header[Header_Rule_Rounds]
        envelope = strip_dlq_header(document)

        # The DLQ rule's limit counts the retries of the rule only, not those of an operator.
        if is_rule_retry:
            rule_rounds += 1

        # A connection type without a queue has its service invoked right here.
        if not has_queue(conn_type):
            out = self._retry_inbound(sub_key, msg_id, envelope, header, rounds, rule_rounds)
            return out

        # The message leaves the DLQ before it is put back into the queue, and one that is no longer there was retried already.
        if not self._claim(sub_key, msg_id):
            logger.info('DLQ message `%s` of `%s` not retried, it was already taken out of the DLQ', msg_id, sub_key)
            return None

        publisher = OutgoingPublisher(self.server, conn_type, conn_id)
        result = publisher.publish_request(envelope[Key_CID], Attempts_None, envelope[Key_Request],
            dlq_rounds=rounds, dlq_rule_rounds=rule_rounds)

        logger.info('Retried DLQ message `%s` of `%s` as `%s`, round %d', msg_id, sub_key, result.msg_id, rounds)

        out = result.msg_id
        return out

# ################################################################################################################################

    def _retry_inbound(
        self,
        sub_key:'str',
        msg_id:'str',
        envelope:'stranydict',
        header:'stranydict',
        rounds:'int',
        rule_rounds:'int',
        ) -> 'str':
        """ Invokes a channel's service again under the channel's retry policy.
        """
        envelope[Key_Attempts] = Attempts_None
        envelope[Key_DLQ_Rounds] = rounds
        envelope[Key_DLQ_Rule_Rounds] = rule_rounds

        cid = envelope[Key_CID]

        try:
            deliver_envelope(self.server, cid, envelope)
        except DeliveryExhausted as e:

            # The message goes back to its DLQ as a new message.
            new_msg_id = move_to_dlq(self.server, cid, envelope, e,
                source_topic=header[Header_Source_Topic], source=header[Header_Source])

            if not new_msg_id:
                raise

            self._ack(sub_key, msg_id)

            logger.info('Retried DLQ message `%s` of `%s`, round %d, exhausted again, now `%s`, e:`%s`',
                msg_id, sub_key, rounds, new_msg_id, e.error)

            out = new_msg_id
            return out

        self._ack(sub_key, msg_id)

        logger.info('Retried DLQ message `%s` of `%s`, round %d, delivered', msg_id, sub_key, rounds)

        return ''

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

        if new_msg_id is None:
            raise Exception(f'DLQ message `{msg_id}` of `{sub_key}` was already taken out of the DLQ')

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

    def _forward(self, sub_key:'str', msg_id:'str', document:'stranydict', topic_name:'str', keep_header:'bool') -> 'bool':
        """ Takes one DLQ message out of the DLQ and publishes it to a topic, returning False if another forward
        had already taken it out.
        """
        if keep_header:
            to_publish = document
        else:
            to_publish = strip_dlq_header(document)

        # The message leaves the DLQ before it is published, so that one which is no longer there is published once only.
        if not self._claim(sub_key, msg_id):
            logger.info('DLQ message `%s` of `%s` not forwarded, it was already taken out of the DLQ', msg_id, sub_key)
            return False

        pubsub = PubSubFacade(self.server, PubSub.Outgoing.Delivery_Service)
        _ = pubsub.publish(topic_name, dumps(to_publish), cid=document[Key_CID])

        logger.info('Forwarded DLQ message `%s` of `%s` to `%s`, header kept:%s', msg_id, sub_key, topic_name, keep_header)

        return True

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

        is_forwarded = self._forward(sub_key, msg_id, document, topic_name, keep_header)

        if not is_forwarded:
            raise Exception(f'DLQ message `{msg_id}` of `{sub_key}` was already taken out of the DLQ')

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

                if header[Header_Rule_Rounds] >= max_rounds:
                    continue

                new_msg_id = self._retry(sub_key, msg_id, document, is_rule_retry=True)

                # A message that an operator retried after this run read the DLQ is left to that retry.
                if new_msg_id is None:
                    continue

            elif action == _dlq.Action.Forward:
                is_forwarded = self._forward(sub_key, msg_id, document, forward_to, keep_header)

                # A message that an operator forwarded after this run read the DLQ was published by that forward.
                if not is_forwarded:
                    continue

            else:
                self._discard(sub_key, msg_id, document)

            count += 1

        return count

# ################################################################################################################################
# ################################################################################################################################
