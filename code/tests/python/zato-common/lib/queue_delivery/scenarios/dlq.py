# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A message whose attempts ran out moves to its connection's DLQ, and the DLQ services, on every pub/sub backend.

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.common import AuditEvent
from zato.common.pubsub.dlq import Header_Attempts, Header_Error, Header_Moved_Time, Header_Pub_Time, Header_Reason, \
    Header_Rounds, Header_Source_Msg_ID, Header_Source_Topic, Key_DLQ
from zato.common.pubsub.outgoing import get_outgoing_topic_name, Key_CID, Key_Conn_Name, Key_Data, Key_DLQ_Rounds, \
    Key_Msg_ID, Key_Pub_Time, Key_Request

# Test support
from queue_delivery.client import get_client, get_queue, is_broker_backend, restart_server, send, wait_for_audit_events, \
    wait_for_queue_empty
from queue_delivery.dlq import Discard_All_Messages, Discard_Message, Forward_All_Messages, Forward_Message, get_dlq, \
    get_topic_messages, Get_Queue_List, invoke, Retry_All_Messages, Retry_Message, send_to_dlq, subscribe_topic, \
    wait_for_dlq_count
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Attempts_Per_Round, Conn_DLQ_Keep, Conn_No_DLQ, Forward_Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict
    from queue_delivery.receiver import RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

# Longer than one round of the connection
_stay_seconds = PubSub.Outgoing.Retry_Round_Wait + 4

# ################################################################################################################################
# ################################################################################################################################

def fill_dlq(client:'AdminClient', conn_name:'str', receiver:'RecordingReceiver', count:'int') -> 'anydict':
    """ Puts that many messages into a connection's DLQ, one after another.
    """
    receiver.refuse_all()

    for index in range(count):
        result = send(client, conn_name, {'seq': index + 1})
        assert result['is_in_queue'] is True

    out = wait_for_dlq_count(client, conn_name, count)
    assert len(out['messages']) == count, out

    receiver.accept_all()

    return out

# ################################################################################################################################
# ################################################################################################################################

class DLQScenarios(ScenarioBase):

    def test_a_message_whose_attempts_ran_out_moves_to_the_dlq_and_the_next_one_gets_its_turn(self) -> 'None':
        """ Two messages, the first turned down for good.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        receiver.refuse_next(Attempts_Per_Round)

        first = send(client, conn_name, {'seq': 1})
        second = send(client, conn_name, {'seq': 2})

        assert first['is_in_queue'] is True
        assert second['is_in_queue'] is True

        dlq = wait_for_dlq_count(client, conn_name, 1)
        assert len(dlq['messages']) == 1, dlq

        document = dlq['messages'][0]['document']
        header = document[Key_DLQ]

        assert header[Header_Reason] == PubSub.Outgoing.DLQ_Reason_Retries_Exhausted
        assert header[Header_Error].startswith(self.t.refused_error_prefix), header[Header_Error]
        assert header[Header_Attempts] == Attempts_Per_Round
        assert header[Header_Rounds] == 0
        assert header[Header_Moved_Time] > header[Header_Pub_Time]

        assert header[Header_Source_Topic] == get_outgoing_topic_name(self.t.conn_type, conn_name)
        assert header[Header_Source_Msg_ID] == first['msg_id']
        assert header[Header_Source_Msg_ID] == document[Key_Msg_ID]
        assert header[Header_Pub_Time] == document[Key_Pub_Time]

        assert document[Key_CID] == first['cid']
        assert document[Key_Conn_Name] == conn_name
        assert document[Key_DLQ_Rounds] == 0
        assert self.t.body_of_envelope_data(document[Key_Request][Key_Data]) == {'seq': 1}

        events = wait_for_audit_events(first['cid'], AuditEvent.DLQ, 1)
        assert len(events) == 1
        assert events[0]['sub_key'] == dlq['sub_key']

        accepted = receiver.wait_for_accepted(1)
        assert self.bodies(accepted) == [{'seq': 2}]

        assert len(receiver.requests) == Attempts_Per_Round + 1

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

        # The DLQ is in the pub/sub database whichever backend the queue has
        if is_broker_backend():
            assert queue['messages'] == []
            assert len(get_dlq(client, conn_name)['messages']) == 1

# ################################################################################################################################

    def test_a_retried_message_goes_to_the_end_of_the_queue_and_counts_its_rounds(self) -> 'None':
        """ Retry puts a DLQ message back into its connection's queue without its header.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        dlq_sub_key = get_dlq(client, conn_name)['sub_key']

        receiver.refuse_next(Attempts_Per_Round)

        response = invoke(client, Retry_Message, {'sub_key': dlq_sub_key, 'msg_id': message['msg_id']})
        assert response['msg_id'] == message['msg_id']
        assert response['new_msg_id'] != message['msg_id']

        dlq = wait_for_dlq_count(client, conn_name, 1)
        retried = dlq['messages'][0]

        assert retried['msg_id'] != message['msg_id']
        assert retried['document'][Key_DLQ][Header_Rounds] == 1
        assert retried['document'][Key_DLQ_Rounds] == 1
        assert retried['document'][Key_DLQ][Header_Source_Msg_ID] == response['new_msg_id']
        assert retried['document'][Key_CID] == message['document'][Key_CID]

        assert len(receiver.requests) == 2 * Attempts_Per_Round

        receiver.accept_all()

        _ = invoke(client, Retry_Message, {'sub_key': dlq_sub_key, 'msg_id': retried['msg_id']})

        accepted = receiver.wait_for_accepted(1)
        assert self.bodies(accepted) == [{'seq': 1}]

        dlq = get_dlq(client, conn_name)
        assert dlq['messages'] == []

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_with_the_dlq_off_the_message_stays_at_the_head_and_nothing_overtakes_it(self) -> 'None':
        """ With the DLQ switch off a message whose attempts ran out stays where it is.
        """
        client = get_client()
        receiver = self.receiver(Conn_No_DLQ)
        conn_name = self.conn(Conn_No_DLQ)

        receiver.refuse_all()

        first = send(client, conn_name, {'seq': 1})
        second = send(client, conn_name, {'seq': 2})

        assert first['is_in_queue'] is True
        assert second['is_in_queue'] is True

        _ = receiver.wait_for_requests(3, timeout=_stay_seconds)

        for body in self.bodies(receiver.requests):
            assert body == {'seq': 1}

        dlq = get_dlq(client, conn_name)
        assert dlq['messages'] == []

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 2

        receiver.accept_all()

        accepted = receiver.wait_for_accepted(2)
        assert self.bodies(accepted) == [{'seq': 1}, {'seq': 2}]

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_forward_publishes_the_document_to_a_topic_with_or_without_its_header(self) -> 'None':
        """ Forward publishes a DLQ message to a topic and takes it out of the DLQ.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        subscribe_topic(client, Forward_Topic)
        _ = get_topic_messages(client, Forward_Topic)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        dlq_sub_key = get_dlq(client, conn_name)['sub_key']

        response = invoke(client, Forward_Message, {
            'sub_key': dlq_sub_key,
            'msg_id': message['msg_id'],
            'topic_name': Forward_Topic,
            'keep_header': True,
        })
        assert response['topic_name'] == Forward_Topic

        forwarded = get_topic_messages(client, Forward_Topic)
        assert len(forwarded) == 1

        assert forwarded[0]['document'] == message['document']
        assert Key_DLQ in forwarded[0]['document']

        assert get_dlq(client, conn_name)['messages'] == []

        message = send_to_dlq(client, conn_name, receiver, {'seq': 2})

        _ = invoke(client, Forward_Message, {
            'sub_key': dlq_sub_key,
            'msg_id': message['msg_id'],
            'topic_name': Forward_Topic,
            'keep_header': False,
        })

        forwarded = get_topic_messages(client, Forward_Topic)
        assert len(forwarded) == 1

        document = forwarded[0]['document']
        assert Key_DLQ not in document
        assert document[Key_Msg_ID] == message['document'][Key_Msg_ID]
        assert self.t.body_of_envelope_data(document[Key_Request][Key_Data]) == {'seq': 2}

        assert get_dlq(client, conn_name)['messages'] == []

# ################################################################################################################################

    def test_discard_takes_the_message_out_of_the_dlq_for_good(self) -> 'None':
        """ Discard removes a DLQ message and nothing arrives anywhere.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        dlq_sub_key = get_dlq(client, conn_name)['sub_key']

        response = invoke(client, Discard_Message, {'sub_key': dlq_sub_key, 'msg_id': message['msg_id']})
        assert response['msg_id'] == message['msg_id']

        assert get_dlq(client, conn_name)['messages'] == []

        assert len(receiver.requests) == Attempts_Per_Round
        assert receiver.accepted() == []

# ################################################################################################################################

    def test_the_all_services_act_on_every_message_oldest_first(self) -> 'None':
        """ Retry-all, forward-all and discard-all act on every DLQ message, in order.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        subscribe_topic(client, Forward_Topic)
        _ = get_topic_messages(client, Forward_Topic)

        dlq = fill_dlq(client, conn_name, receiver, 3)
        dlq_sub_key = dlq['sub_key']

        response = invoke(client, Retry_All_Messages, {'sub_key': dlq_sub_key})
        assert response['count'] == 3

        accepted = receiver.wait_for_accepted(3)
        assert self.bodies(accepted) == [{'seq': 1}, {'seq': 2}, {'seq': 3}]
        assert get_dlq(client, conn_name)['messages'] == []

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

        receiver.clear()
        _ = fill_dlq(client, conn_name, receiver, 3)

        response = invoke(client, Forward_All_Messages, {
            'sub_key': dlq_sub_key,
            'topic_name': Forward_Topic,
            'keep_header': True,
        })
        assert response['count'] == 3

        forwarded = get_topic_messages(client, Forward_Topic)
        assert len(forwarded) == 3

        for index, item in enumerate(forwarded):
            assert self.t.body_of_envelope_data(item['document'][Key_Request][Key_Data]) == {'seq': index + 1}
            assert item['document'][Key_DLQ][Header_Rounds] == 0

        assert get_dlq(client, conn_name)['messages'] == []

        receiver.clear()
        _ = fill_dlq(client, conn_name, receiver, 3)

        response = invoke(client, Discard_All_Messages, {'sub_key': dlq_sub_key})
        assert response['count'] == 3

        assert get_dlq(client, conn_name)['messages'] == []
        assert receiver.accepted() == []

# ################################################################################################################################

    def test_the_queue_list_shows_the_depths(self) -> 'None':
        """ The queue list has one row per connection with a queue or a DLQ, with how many messages wait in each.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        no_dlq_receiver = self.receiver(Conn_No_DLQ)

        dlq_conn = self.conn(Conn_DLQ_Keep)
        no_dlq_conn = self.conn(Conn_No_DLQ)

        _ = fill_dlq(client, dlq_conn, receiver, 2)

        no_dlq_receiver.refuse_all()
        result = send(client, no_dlq_conn, {'seq': 1})
        assert result['is_in_queue'] is True

        response = invoke(client, Get_Queue_List, {})
        rows = {row['name']: row for row in response['items']}

        row = rows[dlq_conn]
        assert row['conn_type'] == self.t.conn_type
        assert row['queue_depth'] == 0
        assert row['dlq_depth'] == 2

        row = rows[no_dlq_conn]
        assert row['conn_type'] == self.t.conn_type
        assert row['queue_depth'] == 1
        assert row['dlq_depth'] == 0

        no_dlq_receiver.accept_all()

# ################################################################################################################################

    def test_a_restart_leaves_the_dlq_where_it_was(self) -> 'None':
        """ A message in the DLQ is still there after the server restarts.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})

        restart_server()

        dlq = get_dlq(client, conn_name)
        assert len(dlq['messages']) == 1
        assert dlq['messages'][0]['msg_id'] == message['msg_id']

        response = invoke(client, Retry_Message, {'sub_key': dlq['sub_key'], 'msg_id': message['msg_id']})
        assert response['msg_id'] == message['msg_id']

        accepted = receiver.wait_for_accepted(1)
        assert self.bodies(accepted) == [{'seq': 1}]

        assert get_dlq(client, conn_name)['messages'] == []

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################
# ################################################################################################################################
