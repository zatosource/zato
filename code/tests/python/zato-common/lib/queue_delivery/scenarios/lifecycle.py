# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A connection's queue and DLQ follow the connection - a rename moves them, a delete takes them along.

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name
from zato.common.pubsub.outgoing import get_outgoing_sub_key, get_outgoing_topic_name
from zato.common.pubsub.sql.schema import message_table

# Test support
from queue_delivery.client import create_connection, delete_connection, edit_connection, get_client, get_pubsub_db_engine, \
    get_queue, get_topic_subscribers, is_broker_backend, msg_ids_of, send, wait_for_queue_empty
from queue_delivery.dlq import get_dlq, send_to_dlq
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_DLQ_Keep

# ################################################################################################################################
# ################################################################################################################################

_broker_skip_reason = 'The topics of a broker backend are bound to their queues by name in enmasse'

_renamed_suffix = '.renamed'
_throwaway_suffix = '.throwaway'

# A rename or a delete holds the queue still first, which means waiting for the round of the message at its head to end -
# and with the DLQ on, a round that ends with the endpoint still refusing moves that message to the DLQ. This is why the
# tests below send two messages behind the one already in the DLQ, the head goes to the DLQ while the queue is held
# and the one behind it is what waits in the queue through the rename or the delete.
_head = {'seq': 2}
_behind = {'seq': 3}

# ################################################################################################################################
# ################################################################################################################################

def count_topic_messages(topic_name:'str') -> 'int':
    """ How many message rows the pub/sub database holds under a topic.
    """
    engine = get_pubsub_db_engine()

    query = select(func.count()).select_from(message_table)
    query = query.where(message_table.c.topic_name == topic_name.lower())

    with engine.connect() as connection:
        out = connection.execute(query).scalar()

    return out

# ################################################################################################################################
# ################################################################################################################################

class LifecycleScenarios(ScenarioBase):

    def test_a_rename_moves_the_queue_and_the_dlq_to_the_new_name(self) -> 'None':
        """ A message waits in the queue and another in the DLQ when the connection is renamed.
        """
        if is_broker_backend():
            pytest.skip(_broker_skip_reason)

        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)

        old_name = self.conn(Conn_DLQ_Keep)
        new_name = old_name + _renamed_suffix

        conn_type = self.t.conn_type

        in_dlq = send_to_dlq(client, old_name, receiver, {'seq': 1})

        receiver.refuse_all()

        head = send(client, old_name, _head)
        waiting = send(client, old_name, _behind)

        assert head['is_in_queue'] is True
        assert waiting['is_in_queue'] is True

        conn_id = edit_connection(client, old_name, {'name': new_name})

        try:
            queue = get_queue(client, new_name)
            assert queue['depth'] == 1, queue
            assert msg_ids_of(queue['messages']) == [waiting['msg_id']]

            dlq = get_dlq(client, new_name)
            assert msg_ids_of(dlq['messages']) == [in_dlq['msg_id'], head['msg_id']], dlq

            assert get_topic_subscribers(client, get_outgoing_topic_name(conn_type, old_name)) == []
            assert get_topic_subscribers(client, get_dlq_topic_name(conn_type, old_name)) == []

            assert get_topic_subscribers(client, get_outgoing_topic_name(conn_type, new_name)) == \
                [get_outgoing_sub_key(conn_type, conn_id)]
            assert get_topic_subscribers(client, get_dlq_topic_name(conn_type, new_name)) == \
                [get_dlq_sub_key(conn_type, conn_id)]

            receiver.accept_all()

            accepted = receiver.wait_for_accepted(1)
            assert self.bodies(accepted) == [_behind]

            queue = wait_for_queue_empty(client, new_name)
            assert queue['depth'] == 0

        finally:
            receiver.accept_all()
            _ = edit_connection(client, new_name, {'name': old_name})

        assert msg_ids_of(get_dlq(client, old_name)['messages']) == [in_dlq['msg_id'], head['msg_id']]

# ################################################################################################################################

    def test_a_delete_takes_the_queue_and_the_dlq_along(self) -> 'None':
        """ A message waits in the queue and another in the DLQ when the connection is deleted.
        """
        if is_broker_backend():
            pytest.skip(_broker_skip_reason)

        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)

        like_name = self.conn(Conn_DLQ_Keep)
        conn_name = like_name + _throwaway_suffix

        conn_type = self.t.conn_type

        conn_id = create_connection(client, conn_name, like_name)
        is_deleted = False

        try:
            _ = send_to_dlq(client, conn_name, receiver, {'seq': 1})

            receiver.refuse_all()

            head = send(client, conn_name, _head)
            waiting = send(client, conn_name, _behind)

            assert head['is_in_queue'] is True
            assert waiting['is_in_queue'] is True

            queue_topic = get_outgoing_topic_name(conn_type, conn_name)
            dlq_topic = get_dlq_topic_name(conn_type, conn_name)

            assert get_topic_subscribers(client, queue_topic) == [get_outgoing_sub_key(conn_type, conn_id)]
            assert get_topic_subscribers(client, dlq_topic) == [get_dlq_sub_key(conn_type, conn_id)]
            assert count_topic_messages(queue_topic) == 2
            assert count_topic_messages(dlq_topic) == 1

            deleted_id = delete_connection(client, conn_name)
            is_deleted = True

            assert deleted_id == conn_id

            assert get_topic_subscribers(client, queue_topic) == []
            assert get_topic_subscribers(client, dlq_topic) == []
            assert count_topic_messages(queue_topic) == 0
            assert count_topic_messages(dlq_topic) == 0

        finally:
            receiver.accept_all()

            # A throwaway that a failed check left behind goes too
            if not is_deleted:
                _ = delete_connection(client, conn_name)

# ################################################################################################################################
# ################################################################################################################################
