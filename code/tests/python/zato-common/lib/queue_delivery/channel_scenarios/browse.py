# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the delivery page of a channel shows - both tabs, the queued request with its destination and the DLQ message
# with the error the target refused it with.

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.pubsub.outgoing import Attempts_None

# Test support
from queue_delivery.channel.client import accept_all, Refuse_Everything, set_behaviour
from queue_delivery.channel.type_under_test import Attempts_Per_Round, Channel_DLQ_Keep, Refused_Error_Text
from queue_delivery.channel_scenarios.base import ChannelScenarioBase, order
from queue_delivery.client import get_client, is_broker_backend, msg_ids_of, wait_for_queue_empty
from queue_delivery.dlq import wait_for_dlq_count
from queue_delivery.scenarios.browse import Kind_DLQ, Kind_Queue, Row_Columns

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

# A message that waits for its next round arrives within this long
_round_timeout = PubSub.Delivery.Retry_Round_Wait + 10.0

# ################################################################################################################################
# ################################################################################################################################

class BrowseScenarios(ChannelScenarioBase):

    def test_the_delivery_page_lists_the_queue_and_the_dlq_of_a_channel(self) -> 'None':
        """ One message in the DLQ and one waiting in the queue, each with the destination of a queued request.
        """
        client = get_client()
        conn_name = self.conn(Channel_DLQ_Keep)

        set_behaviour(client, Attempts_Per_Round)

        _ = self.ack_of(self.call(Channel_DLQ_Keep, order(1)))

        dlq = wait_for_dlq_count(client, conn_name, 1)
        assert len(dlq['messages']) == 1, dlq

        _ = wait_for_queue_empty(client, conn_name)

        set_behaviour(client, Refuse_Everything)

        try:
            waiting = self.ack_of(self.call(Channel_DLQ_Keep, order(2)))

            # The second request's message is in the queue for as long as the target refuses its round
            queue_page = self.browse(client, Channel_DLQ_Keep, Kind_Queue)

            assert queue_page['conn_name'] == conn_name
            assert queue_page['has_queue'] is True
            assert queue_page['queue_depth'] == 1
            assert queue_page['dlq_depth'] == 1
            assert queue_page['dlq_settings'][_dlq.Field_Use_DLQ] is True
            assert queue_page['dlq_settings'][_dlq.Field_Action] == _dlq.Action.Keep

            if is_broker_backend():
                assert queue_page['is_queue_browsable'] is False
                assert queue_page['items'] == []
            else:
                assert queue_page['is_queue_browsable'] is True
                assert queue_page['total'] == 1

                row = queue_page['items'][0]
                assert sorted(row) == sorted(Row_Columns)

                assert row['cid'].startswith(waiting['cid']), (row['cid'], waiting)
                assert row['pub_time_iso']
                # A channel's request is queued before any attempt, there is no direct one
                assert row['attempts'] == Attempts_None
                assert row['rounds'] == 0
                assert row['moved_time_iso'] == ''
                assert row['error'] == ''
                assert row['reason'] == ''

                self.t.check_destination(Channel_DLQ_Keep, row['destination'])

            dlq_page = self.browse(client, Channel_DLQ_Keep, Kind_DLQ)

            assert dlq_page['has_queue'] is True
            assert dlq_page['total'] == 1
            assert msg_ids_of(dlq_page['items']) == msg_ids_of(dlq['messages'])

            row = dlq_page['items'][0]
            assert sorted(row) == sorted(Row_Columns)
            assert row['moved_time_iso']
            assert Refused_Error_Text in row['error'], row['error']
            assert row['reason'] == PubSub.Outgoing.DLQ_Reason_Retries_Exhausted

            self.t.check_destination(Channel_DLQ_Keep, row['destination'])

        finally:
            accept_all(client)

        # The second message is delivered or, if its round ran out first, in the DLQ the test's teardown empties
        _ = wait_for_queue_empty(client, conn_name, timeout=_round_timeout)

# ################################################################################################################################
# ################################################################################################################################
