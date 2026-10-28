# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.business_log import BusinessLog
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import SignalKind
from zato.common.b2b.common.schema import message_table
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import fill_width, Greek_Text, Japanese_Text, non_ascii_body, \
    non_ascii_business_message, non_ascii_identity, non_ascii_sent_message, new_stored_message, receipt_outcome, Server, \
    Source, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_db import LiveDB
    LiveDB = LiveDB

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a test waits between two commits, in milliseconds.
_interval_ms = 10

# ################################################################################################################################
# ################################################################################################################################

class TestNonASCIIClaims:
    """ Greek and Japanese identities that fill their columns are claimed, told apart and read back unchanged.
    """

    def test_claims(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        store = MessageStore(writer)

        identity = non_ascii_identity('一')
        other = non_ascii_identity('二')

        assert store.claim(identity, new_stored_message())
        assert store.claim(other, new_stored_message())
        assert not store.claim(identity, new_stored_message())

        store.set_status(identity, 'Processed')

        stored = store.get(identity, Start_Time)

        assert stored is not None
        assert stored.status == 'Processed'

        columns = (message_table.c.protocol, message_table.c.from_party, message_table.c.to_party,
            message_table.c.message_id)
        query = select(*columns).where(message_table.c.message_id == identity.message_id)

        with database.engine.connect() as connection:
            row = connection.execute(query).one()

        assert tuple(row) == tuple(identity)

# ################################################################################################################################
# ################################################################################################################################

class TestNonASCIIMessages:
    """ A message sent with Greek and Japanese agreement, parties, attributes and bytes is stored, read back
    and recovered unchanged.
    """

    def test_send_and_recover(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        ended_id = fill_width(Japanese_Text, '終')
        awaiting_id = fill_width(Greek_Text, 'Ω')

        ended = non_ascii_sent_message(ended_id)
        wire_body = ended.wire_body

        send_log.record_first_attempt(ended, non_ascii_business_message(ended_id, 60))
        assert send_log.wire_body(ended_id) == wire_body

        send_log.record_signal(ended, {}, non_ascii_body(Greek_Text), SignalKind.Receipt, '', '')
        send_log.record_completion(ended, receipt_outcome())

        # The exchange ended, so the message and its bytes are read from the audit log.
        stored = send_log.get(ended_id)
        expected = non_ascii_sent_message(ended_id)

        assert stored.message_id == ended_id
        assert stored.cpa_id == expected.cpa_id
        assert stored.from_party == expected.from_party
        assert stored.to_party == expected.to_party
        assert stored.attrs[B2BAttr.Service] == expected.attrs[B2BAttr.Service]
        assert stored.attrs[B2BAttr.Action] == expected.attrs[B2BAttr.Action]
        assert stored.details == expected.details
        assert send_log.wire_body(ended_id) == wire_body

        query = select(event_attr_table.c.value).where(event_attr_table.c.name == B2BAttr.Service)

        with database.engine.connect() as connection:
            for value in connection.execute(query).scalars():
                assert value == expected.attrs[B2BAttr.Service]

        # A business transaction still awaits its response when the process stops ..
        business_log.record_sent(non_ascii_business_message(awaiting_id, 60))
        writer.stop()

        # .. and another process recovers both transactions as they were sent.
        new_writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        new_business_log = BusinessLog(Source, Server, new_writer)

        assert new_business_log.recover() == 2

        for message_id in (ended_id, awaiting_id):

            recovered = new_business_log.read(message_id)
            sent = non_ascii_business_message(message_id, 60)

            assert recovered is not None
            assert recovered.message_id == message_id
            assert recovered.cpa_id == sent.cpa_id
            assert recovered.conversation_id == sent.conversation_id
            assert recovered.from_party == sent.from_party
            assert recovered.to_party == sent.to_party
            assert recovered.service == sent.service
            assert recovered.action == sent.action

        new_writer.stop()

# ################################################################################################################################
# ################################################################################################################################
