# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services the queue and DLQ pages of an outgoing connection read from and act through.

# stdlib
from contextlib import closing
from json import dumps, loads

# Zato
from zato.common.odb.model import PubSubTopic
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name, Header_Error, Header_Moved_Time, Header_Reason, Key_DLQ
from zato.common.pubsub.outgoing import find_outgoing_conn, get_dlq_settings, get_outgoing_sub_key, get_outgoing_topic_name, \
    get_page_description, invoker_to_dict, Key_Attempts, Key_CID, Key_Data, Key_DLQ_Rounds, Key_Msg_ID, Key_Pub_Time, \
    Key_Request
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, anytuple, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

_default_page_size = 50
_default_page = 1

_pending = 'pending'

# How many messages one read of a queue brings back
_read_page_size = 500

Kind_Queue = 'queue'
Kind_DLQ   = 'dlq'

Action_Retry   = 'retry'
Action_Forward = 'forward'
Action_Discard = 'discard'

# The DLQ services one action on the DLQ tab runs, by action
_dlq_action_services = {
    Action_Retry:   'zato.pubsub.dlq.retry-message',
    Action_Forward: 'zato.pubsub.dlq.forward-message',
    Action_Discard: 'zato.pubsub.dlq.discard-message',
}

# ################################################################################################################################
# ################################################################################################################################

def _matches(document:'stranydict', query:'str') -> 'bool':
    """ Whether a message has the query anywhere in it.
    """
    text = dumps(document)
    text = text.lower()

    out = query in text
    return out

# ################################################################################################################################

def _to_row(document:'stranydict', destination:'str') -> 'stranydict':
    """ What the listing shows of one message.
    """
    out = {
        'msg_id': document[Key_Msg_ID],
        'cid': document[Key_CID],
        'pub_time_iso': document[Key_Pub_Time],
        'attempts': document[Key_Attempts],
        'rounds': document[Key_DLQ_Rounds],
        'destination': destination,
    }

    if dlq_header := document.get(Key_DLQ):
        out['moved_time_iso'] = dlq_header[Header_Moved_Time]
        out['error'] = dlq_header[Header_Error]
        out['reason'] = dlq_header[Header_Reason]
    else:
        out['moved_time_iso'] = ''
        out['error'] = ''
        out['reason'] = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class _BrowseService(AdminService):
    """ What the browsing services share.
    """

    def _get_conn(self, conn_type:'str', conn_id:'int') -> 'anytuple':
        """ The connection by its id, as its name and its wrapper.
        """
        found = find_outgoing_conn(self.server, conn_type, conn_id)

        if not found:
            raise Exception(f'No such outgoing connection `{conn_type}` `{conn_id}`')

        out = found
        return out

# ################################################################################################################################

    def _get_names(self, kind:'str', conn_type:'str', conn_id:'int', conn_name:'str') -> 'anytuple':
        """ The topic and the sub key of a connection's queue or of its DLQ.
        """
        if kind == Kind_DLQ:
            topic_name = get_dlq_topic_name(conn_type, conn_name)
            sub_key = get_dlq_sub_key(conn_type, conn_id)
        else:
            topic_name = get_outgoing_topic_name(conn_type, conn_name)
            sub_key = get_outgoing_sub_key(conn_type, conn_id)

        out = (topic_name, sub_key)
        return out

# ################################################################################################################################

    def _get_documents(self, kind:'str', conn_type:'str', conn_id:'int', conn_name:'str') -> 'anylist':
        """ Every message the queue or the DLQ holds, oldest first.
        """
        topic_name, sub_key = self._get_names(kind, conn_type, conn_id, conn_name)
        backend = self.server.pubsub_backend

        out:'anylist' = []
        cursor = '-'

        # The messages come in pages until there is no next one
        while True:
            messages, cursor = backend.browse_messages(topic_name, sub_key, _pending, cursor, _read_page_size, needs_data=True)

            for message in messages:
                out.append(loads(message['data']))

            if not cursor:
                break

        return out

# ################################################################################################################################

    def _load_document(self, kind:'str', conn_type:'str', conn_id:'int', conn_name:'str', msg_id:'str') -> 'stranydict':
        """ One message the queue or the DLQ holds.
        """
        topic_name, _ = self._get_names(kind, conn_type, conn_id, conn_name)
        details = self.server.pubsub_backend.get_message_details(topic_name, msg_id)

        if not details:
            raise Exception(f'No such message `{msg_id}` in `{topic_name}`')

        out = loads(details['data'])
        return out

# ################################################################################################################################

    def _get_topic_list(self) -> 'strlist':
        """ The name of every topic, sorted.
        """
        out:'strlist' = []

        with closing(self.odb.session()) as session:
            query = session.query(PubSubTopic.name)
            query = query.filter(PubSubTopic.cluster_id == self.server.cluster_id)
            query = query.order_by(PubSubTopic.name)

            for row in query:
                out.append(row.name)

        return out

# ################################################################################################################################
# ################################################################################################################################

class GetMessageList(_BrowseService):
    """ One page of the messages an outgoing connection's queue or DLQ holds.
    """
    name  = 'zato.pubsub.outgoing.get-message-list'
    input = 'conn_type', Int('conn_id'), 'kind', '-query', Int('-cur_page'), Int('-page_size')

    def handle(self) -> 'None':
        input = self.request.input

        conn_type = input.conn_type
        conn_id = input.conn_id
        kind = input.kind

        cur_page = input.cur_page or _default_page
        page_size = input.page_size or _default_page_size

        conn_name, wrapper = self._get_conn(conn_type, conn_id)
        page = get_page_description(conn_type)

        # A queue on a broker cannot be browsed
        topic_name = get_outgoing_topic_name(conn_type, conn_name)
        topic_backend = self.server.config_manager.get_pubsub_topic_backend(topic_name)
        is_queue_browsable = topic_backend is None

        documents = self._get_documents(kind, conn_type, conn_id, conn_name)

        if query := input.query:
            query = query.lower()
            matching:'anylist' = []

            for document in documents:
                if _matches(document, query):
                    matching.append(document)

            documents = matching

        total = len(documents)
        start = (cur_page - 1) * page_size
        end = start + page_size
        page_documents = documents[start:end]

        num_pages, remainder = divmod(total, page_size)
        if remainder:
            num_pages += 1

        items:'anylist' = []

        for document in page_documents:
            destination = page.destination(wrapper, document[Key_Request])
            items.append(_to_row(document, destination))

        # The depths of both tabs go along with either
        queue_sub_key = get_outgoing_sub_key(conn_type, conn_id)
        queue_depth = self.server.config_manager.outgoing_queue_depth.get(queue_sub_key)

        dlq_topic_name, dlq_sub_key = self._get_names(Kind_DLQ, conn_type, conn_id, conn_name)
        dlq_depth = self.server.pubsub_backend.get_total_count(dlq_sub_key, dlq_topic_name, _pending)

        dlq_settings = get_dlq_settings(conn_type, wrapper)
        topic_list = self._get_topic_list()

        self.response.payload = {
            'conn_name': conn_name,
            'is_queue_browsable': is_queue_browsable,
            'queue_depth': queue_depth,
            'dlq_depth': dlq_depth,
            'dlq_settings': dlq_settings,
            'invoker': invoker_to_dict(page.invoker),
            'topic_list': topic_list,
            'items': items,
            'total': total,
            'cur_page': cur_page,
            'num_pages': num_pages,
            'page_size': page_size,
        }

# ################################################################################################################################
# ################################################################################################################################

class GetMessage(_BrowseService):
    """ One message in full, with what the page shows of it.
    """
    name  = 'zato.pubsub.outgoing.get-message'
    input = 'conn_type', Int('conn_id'), 'kind', 'msg_id'

    def handle(self) -> 'None':
        input = self.request.input
        conn_type = input.conn_type

        conn_name, wrapper = self._get_conn(conn_type, input.conn_id)
        page = get_page_description(conn_type)

        document = self._load_document(input.kind, conn_type, input.conn_id, conn_name, input.msg_id)
        request = document[Key_Request]

        # The settings go along with the message because the details window states what the rule will do with it
        dlq_settings = get_dlq_settings(conn_type, wrapper)

        self.response.payload = {
            'document': document,
            'dlq_settings': dlq_settings,
            'destination': page.destination(wrapper, request),
            'facts': page.details_facts(request),
            'body_mode': page.body_mode(request),
            'invoker': invoker_to_dict(page.invoker, request),
        }

# ################################################################################################################################
# ################################################################################################################################

class GetMessageTimeList(_BrowseService):
    """ When each of the messages named entered the queue or the DLQ - what the pages' refreshes read.
    """
    name  = 'zato.pubsub.outgoing.get-message-time-list'
    input = 'conn_type', Int('conn_id'), 'kind', AsIs('msg_id_list')

    def handle(self) -> 'None':
        input = self.request.input
        kind = input.kind

        conn_name, _ = self._get_conn(input.conn_type, input.conn_id)
        documents = self._get_documents(kind, input.conn_type, input.conn_id, conn_name)

        wanted = set(loads(input.msg_id_list))
        items:'stranydict' = {}

        for document in documents:
            msg_id = document[Key_Msg_ID]

            if msg_id not in wanted:
                continue

            if kind == Kind_DLQ:
                items[msg_id] = document[Key_DLQ][Header_Moved_Time]
            else:
                items[msg_id] = document[Key_Pub_Time]

        self.response.payload = {'items': items}

# ################################################################################################################################
# ################################################################################################################################

class MessageAction(_BrowseService):
    """ Runs one action on the messages named by their ids - on the DLQ tab through the DLQ services, on the queue tab
    a discard takes each message out of the queue.
    """
    name  = 'zato.pubsub.outgoing.message-action'
    input = 'conn_type', Int('conn_id'), 'kind', 'action', AsIs('msg_id_list'), '-forward_to', Bool('-keep_header')

    def handle(self) -> 'None':
        input = self.request.input

        conn_type = input.conn_type
        conn_id = input.conn_id
        kind = input.kind
        action = input.action

        conn_name, _ = self._get_conn(conn_type, conn_id)
        msg_id_list = loads(input.msg_id_list)

        _, sub_key = self._get_names(kind, conn_type, conn_id, conn_name)

        if kind == Kind_DLQ:
            self._act_on_dlq(sub_key, action, msg_id_list, input.forward_to, input.keep_header)
        else:
            self._discard_from_queue(sub_key, msg_id_list)

        self.response.payload = {
            'action': action,
            'count': len(msg_id_list),
            'forward_to': input.forward_to,
            'keep_header': input.keep_header,
        }

# ################################################################################################################################

    def _act_on_dlq(self, sub_key:'str', action:'str', msg_id_list:'strlist', forward_to:'str', keep_header:'bool') -> 'None':
        """ Runs one DLQ service on each message named.
        """
        service_name = _dlq_action_services[action]

        for msg_id in msg_id_list:
            request:'anydict' = {'sub_key': sub_key, 'msg_id': msg_id}

            if action == Action_Forward:
                request['topic_name'] = forward_to
                request['keep_header'] = keep_header

            _ = self.invoke(service_name, request)

# ################################################################################################################################

    def _discard_from_queue(self, sub_key:'str', msg_id_list:'strlist') -> 'None':
        """ Takes each message named out of the queue - a discarded message must not hold the queue up.
        """
        depth = self.server.config_manager.outgoing_queue_depth

        for msg_id in msg_id_list:
            was_acked = self.server.pubsub_backend.ack_message(sub_key, msg_id)

            if was_acked:
                depth.lower(sub_key, 1)

# ################################################################################################################################
# ################################################################################################################################

class UpdateMessage(_BrowseService):
    """ Replaces the body of one message, which is what its next attempt sends.
    """
    name  = 'zato.pubsub.outgoing.update-message'
    input = 'conn_type', Int('conn_id'), 'kind', 'msg_id', 'data'

    def handle(self) -> 'None':
        input = self.request.input

        conn_type = input.conn_type
        conn_id = input.conn_id
        kind = input.kind
        msg_id = input.msg_id

        conn_name, _ = self._get_conn(conn_type, conn_id)
        topic_name, _ = self._get_names(kind, conn_type, conn_id, conn_name)

        # The stored message is the whole envelope, so the body is replaced inside it ..
        document = self._load_document(kind, conn_type, conn_id, conn_name, msg_id)
        document[Key_Request][Key_Data] = input.data

        # .. and the envelope is written back.
        was_updated = self.server.pubsub_backend.update_message(topic_name, msg_id, dumps(document))

        if not was_updated:
            raise Exception(f'No such message `{msg_id}` in `{topic_name}`')

        data_bytes = input.data.encode('utf8')

        self.response.payload = {
            'msg_id': msg_id,
            'size': len(data_bytes),
        }

# ################################################################################################################################
# ################################################################################################################################
