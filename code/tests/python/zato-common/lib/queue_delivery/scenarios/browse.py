# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services behind the delivery page - the listing of a queue and of a DLQ, the search, the pages, one message in
# full, the refresh, the actions on selected messages and the edit of a message, on every pub/sub backend.

# stdlib
from json import dumps

# pytest
import pytest

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.pubsub.dlq import Header_Moved_Time, Key_DLQ
from zato.common.pubsub.outgoing import Attempts_Direct, Key_Data, Key_Request

# Test support
from queue_delivery.client import get_client, get_queue, is_broker_backend, msg_ids_of, send, wait_for_queue_depth, \
    wait_for_queue_empty
from queue_delivery.dlq import get_dlq, invoke, send_to_dlq, wait_for_dlq_count
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_DLQ_Keep, Conn_Orders

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, anylist
    from queue_delivery.receiver import RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

Get_Message_List = 'zato.pubsub.outgoing.get-message-list'
Get_Message = 'zato.pubsub.outgoing.get-message'
Get_Message_Time_List = 'zato.pubsub.outgoing.get-message-time-list'
Message_Action = 'zato.pubsub.outgoing.message-action'
Update_Message = 'zato.pubsub.outgoing.update-message'

Kind_Queue = 'queue'
Kind_DLQ = 'dlq'

Action_Retry = 'retry'
Action_Discard = 'discard'

# The columns of one row of either tab
Row_Columns = ('msg_id', 'cid', 'pub_time_iso', 'attempts', 'rounds', 'destination', 'moved_time_iso', 'error', 'reason')

_broker_skip_reason = 'The queue of a broker backend cannot be browsed'
_not_a_broker_reason = 'The queue of this backend is in the pub/sub database'

# ################################################################################################################################
# ################################################################################################################################

def fill_dlq_with(client:'AdminClient', conn_name:'str', receiver:'RecordingReceiver', data_list:'anylist') -> 'anylist':
    """ Puts these documents into a connection's DLQ, one after another, and returns the DLQ messages they became.
    """
    receiver.refuse_all()

    for data in data_list:
        result = send(client, conn_name, data)
        assert result['is_in_queue'] is True

    dlq = wait_for_dlq_count(client, conn_name, len(data_list))
    assert len(dlq['messages']) == len(data_list), dlq

    receiver.accept_all()

    out = dlq['messages']
    return out

# ################################################################################################################################
# ################################################################################################################################

class BrowseScenarios(ScenarioBase):

    def _list(self, client:'AdminClient', conn_key:'str', kind:'str', **extra:'anydict') -> 'anydict':
        """ One page of a connection's queue or DLQ.
        """
        request = {
            'conn_type': self.t.conn_type,
            'conn_id': self._conn_id(client, conn_key),
            'kind': kind,
        }
        request.update(extra)

        out = invoke(client, Get_Message_List, request)
        return out

# ################################################################################################################################

    def _conn_id(self, client:'AdminClient', conn_key:'str') -> 'int':
        """ The id of a connection.
        """
        out = get_queue(client, self.conn(conn_key))['conn_id']
        return out

# ################################################################################################################################

    def test_the_queue_and_the_dlq_list_their_messages_with_the_columns_of_a_row(self) -> 'None':
        """ Two messages in the DLQ and one waiting in the queue.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        in_dlq = fill_dlq_with(client, conn_name, receiver, [{'seq': 1}, {'seq': 2}])

        receiver.refuse_all()

        waiting = send(client, conn_name, {'seq': 3})
        assert waiting['is_in_queue'] is True

        try:
            queue_page = self._list(client, Conn_DLQ_Keep, Kind_Queue)

            assert queue_page['conn_name'] == conn_name
            assert queue_page['queue_depth'] == 1
            assert queue_page['dlq_depth'] == 2
            assert queue_page['dlq_settings'][_dlq.Field_Use_DLQ] is True
            assert queue_page['dlq_settings'][_dlq.Field_Action] == _dlq.Action.Keep
            assert queue_page['cur_page'] == 1
            assert queue_page['num_pages'] == 1

            if is_broker_backend():
                assert queue_page['is_queue_browsable'] is False
                assert queue_page['items'] == []
                assert queue_page['total'] == 0
            else:
                assert queue_page['is_queue_browsable'] is True
                assert queue_page['total'] == 1

                row = queue_page['items'][0]
                assert sorted(row) == sorted(Row_Columns)

                assert row['msg_id'] == waiting['msg_id']
                assert row['cid'] == waiting['cid']
                assert row['pub_time_iso']
                assert row['attempts'] == Attempts_Direct
                assert row['rounds'] == 0
                assert row['moved_time_iso'] == ''
                assert row['error'] == ''
                assert row['reason'] == ''

                self.t.check_destination(Conn_DLQ_Keep, row['destination'])

            dlq_page = self._list(client, Conn_DLQ_Keep, Kind_DLQ)

            assert dlq_page['total'] == 2
            assert msg_ids_of(dlq_page['items']) == msg_ids_of(in_dlq)

            for row in dlq_page['items']:
                assert sorted(row) == sorted(Row_Columns)
                assert row['moved_time_iso']
                assert row['error'].startswith(self.t.refused_error_prefix), row['error']
                assert row['reason'] == PubSub.Outgoing.DLQ_Reason_Retries_Exhausted

                self.t.check_destination(Conn_DLQ_Keep, row['destination'])

        finally:
            receiver.accept_all()

        _ = receiver.wait_for_accepted(1)
        _ = wait_for_queue_empty(client, conn_name)

# ################################################################################################################################

    def test_a_search_matches_a_body_and_matches_nothing(self) -> 'None':
        """ The query is looked for anywhere in a message.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        in_dlq = fill_dlq_with(client, conn_name, receiver, [
            {'seq': 1, 'tag': 'needle-alpha'},
            {'seq': 2, 'tag': 'needle-beta'},
            {'seq': 3, 'tag': 'needle-gamma'},
        ])

        page = self._list(client, Conn_DLQ_Keep, Kind_DLQ, query='NEEDLE-BETA')

        assert page['total'] == 1
        assert msg_ids_of(page['items']) == [in_dlq[1]['msg_id']]

        page = self._list(client, Conn_DLQ_Keep, Kind_DLQ, query='no-such-thing')

        assert page['total'] == 0
        assert page['items'] == []
        assert page['num_pages'] == 0

# ################################################################################################################################

    def test_the_second_page_of_a_list_longer_than_the_page_size(self) -> 'None':
        """ Three messages, two per page.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        in_dlq = fill_dlq_with(client, conn_name, receiver, [{'seq': 1}, {'seq': 2}, {'seq': 3}])

        first = self._list(client, Conn_DLQ_Keep, Kind_DLQ, page_size=2, cur_page=1)

        assert first['total'] == 3
        assert first['num_pages'] == 2
        assert first['page_size'] == 2
        assert first['cur_page'] == 1
        assert msg_ids_of(first['items']) == msg_ids_of(in_dlq[:2])

        second = self._list(client, Conn_DLQ_Keep, Kind_DLQ, page_size=2, cur_page=2)

        assert second['cur_page'] == 2
        assert msg_ids_of(second['items']) == msg_ids_of(in_dlq[2:])

# ################################################################################################################################

    def test_get_message_returns_the_whole_document_with_the_dlq_settings(self) -> 'None':
        """ One DLQ message in full, with what the details window shows of it.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})

        response = invoke(client, Get_Message, {
            'conn_type': self.t.conn_type,
            'conn_id': self._conn_id(client, Conn_DLQ_Keep),
            'kind': Kind_DLQ,
            'msg_id': message['msg_id'],
        })

        assert response['document'] == message['document']
        assert response['dlq_settings'][_dlq.Field_Use_DLQ] is True
        assert response['dlq_settings'][_dlq.Field_Action] == _dlq.Action.Keep
        assert response['body_mode']
        assert isinstance(response['facts'], list)

        self.t.check_destination(Conn_DLQ_Keep, response['destination'])

# ################################################################################################################################

    def test_get_message_time_list_for_a_subset_of_ids(self) -> 'None':
        """ The refresh asks for some of the messages on the page and gets the time of each.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        in_dlq = fill_dlq_with(client, conn_name, receiver, [{'seq': 1}, {'seq': 2}, {'seq': 3}])
        wanted = [in_dlq[0], in_dlq[2]]

        response = invoke(client, Get_Message_Time_List, {
            'conn_type': self.t.conn_type,
            'conn_id': self._conn_id(client, Conn_DLQ_Keep),
            'kind': Kind_DLQ,
            'msg_id_list': dumps(msg_ids_of(wanted)),
        })

        items = response['items']

        assert sorted(items) == sorted(msg_ids_of(wanted))

        for message in wanted:
            assert items[message['msg_id']] == message['document'][Key_DLQ][Header_Moved_Time]

# ################################################################################################################################

    def test_message_action_retries_and_discards_selected_dlq_messages(self) -> 'None':
        """ Two messages in the DLQ, one action each.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        in_dlq = fill_dlq_with(client, conn_name, receiver, [{'seq': 1}, {'seq': 2}])
        conn_id = self._conn_id(client, Conn_DLQ_Keep)

        receiver.clear()

        response = invoke(client, Message_Action, {
            'conn_type': self.t.conn_type,
            'conn_id': conn_id,
            'kind': Kind_DLQ,
            'action': Action_Retry,
            'msg_id_list': dumps([in_dlq[0]['msg_id']]),
        })
        assert response['count'] == 1

        accepted = receiver.wait_for_accepted(1)
        assert self.bodies(accepted) == [{'seq': 1}]

        response = invoke(client, Message_Action, {
            'conn_type': self.t.conn_type,
            'conn_id': conn_id,
            'kind': Kind_DLQ,
            'action': Action_Discard,
            'msg_id_list': dumps([in_dlq[1]['msg_id']]),
        })
        assert response['count'] == 1

        assert get_dlq(client, conn_name)['messages'] == []

        _ = wait_for_queue_empty(client, conn_name)

# ################################################################################################################################

    def test_discarding_a_queue_message_lowers_the_depth_and_the_one_behind_goes_out(self) -> 'None':
        """ Two messages wait, the first is discarded from the queue tab.
        """
        if is_broker_backend():
            pytest.skip(_broker_skip_reason)

        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        first = send(client, conn_name, {'seq': 1})
        second = send(client, conn_name, {'seq': 2})

        assert first['is_in_queue'] is True
        assert second['is_in_queue'] is True

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 2

        response = invoke(client, Message_Action, {
            'conn_type': self.t.conn_type,
            'conn_id': queue['conn_id'],
            'kind': Kind_Queue,
            'action': Action_Discard,
            'msg_id_list': dumps([first['msg_id']]),
        })
        assert response['count'] == 1

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 1
        assert msg_ids_of(queue['messages']) == [second['msg_id']]

        receiver.accept_all()

        accepted = receiver.wait_for_accepted(1)
        assert self.bodies(accepted) == [{'seq': 2}]

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

        assert self.bodies(receiver.accepted()) == [{'seq': 2}]

# ################################################################################################################################

    def test_update_message_changes_what_the_next_attempt_sends(self) -> 'None':
        """ A waiting message is edited and the edited body is what arrives.
        """
        if is_broker_backend():
            pytest.skip(_broker_skip_reason)

        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        waiting = send(client, conn_name, {'seq': 1})
        assert waiting['is_in_queue'] is True

        edited = {'seq': 1, 'edited': True}
        data = self.t.envelope_data_of(edited)

        queue = get_queue(client, conn_name)

        response = invoke(client, Update_Message, {
            'conn_type': self.t.conn_type,
            'conn_id': queue['conn_id'],
            'kind': Kind_Queue,
            'msg_id': waiting['msg_id'],
            'data': data,
        })

        assert response['msg_id'] == waiting['msg_id']
        assert response['size'] == len(data.encode('utf8'))

        queue = get_queue(client, conn_name)
        envelope = queue['messages'][0]['envelope']
        assert self.t.body_of_envelope_data(envelope[Key_Request][Key_Data]) == edited

        receiver.accept_all()

        accepted = receiver.wait_for_accepted(1)
        assert self.bodies(accepted) == [edited]

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_on_a_broker_the_queue_is_not_browsable_while_the_dlq_still_lists(self) -> 'None':
        """ The queue tab of a broker-backed connection has no rows, its DLQ tab has.
        """
        if not is_broker_backend():
            pytest.skip(_not_a_broker_reason)

        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        in_dlq = fill_dlq_with(client, conn_name, receiver, [{'seq': 1}])

        receiver.refuse_all()

        waiting = send(client, conn_name, {'seq': 2})
        assert waiting['is_in_queue'] is True

        try:
            queue_page = self._list(client, Conn_DLQ_Keep, Kind_Queue)

            assert queue_page['is_queue_browsable'] is False
            assert queue_page['items'] == []
            assert queue_page['queue_depth'] == 1
            assert queue_page['dlq_depth'] == 1

            dlq_page = self._list(client, Conn_DLQ_Keep, Kind_DLQ)

            assert dlq_page['is_queue_browsable'] is False
            assert msg_ids_of(dlq_page['items']) == msg_ids_of(in_dlq)

        finally:
            receiver.accept_all()

        _ = receiver.wait_for_accepted(1)
        _ = wait_for_queue_empty(client, conn_name)

# ################################################################################################################################
# ################################################################################################################################
