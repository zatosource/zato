# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alerts about queue delivery, on every pub/sub backend - a sweep of the live server raises an alert about a
# connection whose DLQ holds a message and about one whose queue is deeper than the connection's own threshold,
# each filed under the type's audit source and the connection's name, and says nothing once the depths are gone.
# The sweep reads the audit log too, and the refusals the other scenarios scripted are still in it, so only the two
# queue rules are read here - whatever the rules over the audit log say about the same connection is their business.

# Zato
from zato.common.alerting.object_config import storage_name
from zato.common.alerting.seed.rules_queue import DLQ_Messages_Rule, Queue_Backlog_Rule, Queue_Depth_Threshold_Value

# Test support
from queue_delivery.alerting import get_alerts_raised, get_newest_audit_event_id, run_sweep
from queue_delivery.client import edit_connection, get_client, send, wait_for_queue_empty
from queue_delivery.dlq import Discard_All_Messages, get_dlq, invoke, send_to_dlq
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_DLQ_Keep, Conn_No_DLQ, Conn_Orders

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

# The queue depth the backlog scenario has its connection alert at - low enough for a test to reach
_own_queue_depth = 2

# The two rules these scenarios are about
_queue_rules = (DLQ_Messages_Rule, Queue_Backlog_Rule)

# ################################################################################################################################
# ################################################################################################################################

def queue_alerts_raised(object_name:'str', since_id:'int') -> 'anylist':
    """ The alerts one of the two queue rules raised about an object after the given event, oldest first.
    """
    out = []

    for alert in get_alerts_raised(object_name, since_id):
        if alert['rule'] in _queue_rules:
            out.append(alert)

    return out

# ################################################################################################################################

def queue_rules_raised(object_name:'str', since_id:'int') -> 'anylist':
    """ The names of the queue rules that raised an alert about an object after the given event, in order.
    """
    out = [alert['rule'] for alert in queue_alerts_raised(object_name, since_id)]
    return out

# ################################################################################################################################
# ################################################################################################################################

class AlertingScenarios(ScenarioBase):
    """ The alerts a sweep raises about a connection's queue and DLQ.
    """

    def test_a_message_in_the_dlq_raises_an_alert_until_the_dlq_is_emptied(self) -> 'None':
        """ One message in the DLQ is enough at the default threshold, the alert is filed under the type's source
        and the connection's name, and a sweep after the DLQ is emptied says nothing about the connection.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        # Nothing about the connection before the message is there
        since_id = get_newest_audit_event_id()
        run_sweep(client)
        assert queue_rules_raised(conn_name, since_id) == []

        _ = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        receiver.accept_all()

        since_id = get_newest_audit_event_id()
        run_sweep(client)

        alerts = queue_alerts_raised(conn_name, since_id)
        assert [alert['rule'] for alert in alerts] == [DLQ_Messages_Rule], alerts

        alert = alerts[0]
        assert alert['source'] == self.t.audit_source
        assert conn_name in alert['message']
        assert '1 message in the DLQ' in alert['message']

        # The alert is an error, so a second sweep says it again while the message is there ..
        since_id = get_newest_audit_event_id()
        run_sweep(client)
        assert queue_rules_raised(conn_name, since_id) == [DLQ_Messages_Rule]

        # .. and once the DLQ is emptied there is nothing left to say
        dlq = get_dlq(client, conn_name)
        _ = invoke(client, Discard_All_Messages, {'sub_key': dlq['sub_key']})

        since_id = get_newest_audit_event_id()
        run_sweep(client)
        assert queue_rules_raised(conn_name, since_id) == []

# ################################################################################################################################

    def test_a_queue_deeper_than_the_connections_own_threshold_raises_a_backlog_alert(self) -> 'None':
        """ The connection alerts at two waiting messages of its own, so two held back by the endpoint raise the
        backlog alert, and once they are delivered a sweep says nothing about the connection.
        """
        client = get_client()
        receiver = self.receiver(Conn_No_DLQ)
        conn_name = self.conn(Conn_No_DLQ)

        _ = edit_connection(client, conn_name, {storage_name('queue_depth'): _own_queue_depth})

        try:
            receiver.refuse_all()

            for index in range(_own_queue_depth):
                result = send(client, conn_name, {'seq': index + 1})
                assert result['is_in_queue'] is True

            since_id = get_newest_audit_event_id()
            run_sweep(client)

            alerts = queue_alerts_raised(conn_name, since_id)
            assert [alert['rule'] for alert in alerts] == [Queue_Backlog_Rule], alerts

            alert = alerts[0]
            assert alert['source'] == self.t.audit_source
            assert f'{_own_queue_depth} messages in the queue' in alert['message']

            # A connection at the default threshold of a thousand has no backlog to speak of
            other_name = self.conn(Conn_Orders)
            assert queue_rules_raised(other_name, since_id) == []

            receiver.accept_all()
            _ = wait_for_queue_empty(client, conn_name)

            since_id = get_newest_audit_event_id()
            run_sweep(client)
            assert queue_rules_raised(conn_name, since_id) == []

        finally:
            receiver.accept_all()
            _ = edit_connection(client, conn_name, {storage_name('queue_depth'): Queue_Depth_Threshold_Value})

# ################################################################################################################################
# ################################################################################################################################
