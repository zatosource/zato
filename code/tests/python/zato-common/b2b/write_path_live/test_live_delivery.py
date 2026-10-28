# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The delivery of received messages to the application - a process stopped after a message was received and before
# its delivery was confirmed delivers it once more after a restart, flagged as a possible duplicate.

# stdlib
import json
from signal import SIGKILL

# SQLAlchemy
from sqlalchemy import select

# Zato
from live_db import Line_Delivered, start_child, wait_for_line
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.schema import message_table
from zato.common.b2b.common.store import MessageStore
from zato.common.b2b.ebms2.common import MessageStatus
from zato.common.b2b.ebms2.inbound_common import new_receive_log, pending_deliveries
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import confirm, deliver, new_exchange, send, Server_Name, Start_Time, use_store

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from live_db import LiveDB
    from zato.common.test.b2b_pki import TestParties
    Engine = Engine
    LiveDB = LiveDB
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a test waits between two commits, in milliseconds.
_interval_ms = 10

# How long a stopped child is waited for, in seconds.
_wait_seconds = 30

# How many deliveries one page of a recovery holds.
_page_size = 100

# The payload of the message the child receives.
_payload_text = 'Zamówienie 請求書 τιμολόγιο'

# ################################################################################################################################
# ################################################################################################################################

def _status_of(engine:'Engine', message_id:'str') -> 'str':
    query = select(message_table.c.status).where(message_table.c.message_id == message_id)

    with engine.connect() as connection:
        out = connection.execute(query).scalar_one()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConfirmation:
    """ A received message stays Received until its delivery is confirmed, on each database.
    """

    def test_confirm(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)

        exchange = new_exchange(parties, settings)
        use_store(exchange.receiver, MessageStore(writer))

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert _status_of(database.engine, outbound.message_id) == MessageStatus.Received
        assert len(pending_deliveries(exchange.receiver.receive_log, _page_size)) == 1

        confirm(exchange, result)

        assert _status_of(database.engine, outbound.message_id) == MessageStatus.Processed
        assert pending_deliveries(exchange.receiver.receive_log, _page_size) == []

# ################################################################################################################################
# ################################################################################################################################

class TestProcessStopped:
    """ A process stopped before the confirmation of a delivery delivers the message once more after a restart.
    """

    def test_kill_before_confirm(self, database:'LiveDB') -> 'None':
        child = start_child(database, 'kill-before-confirm', _payload_text)

        stdout = child.stdout
        assert stdout is not None

        # The report is the first line of the child that is a JSON document, and a child that ended reports nothing.
        line = stdout.readline()

        while line and not line.startswith('{'):
            line = stdout.readline()

        report = json.loads(line)
        message_id = report['message_id']

        wait_for_line(child, Line_Delivered)

        child.send_signal(SIGKILL)
        _ = child.wait(_wait_seconds)

        # The claim was committed and the delivery was not confirmed ..
        assert _status_of(database.engine, message_id) == MessageStatus.Received

        # .. so the restarted process finds the message pending, exactly once and flagged ..
        writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        receive_log = new_receive_log(MessageStore(writer), Server_Name)

        recovered = pending_deliveries(receive_log, _page_size)

        assert len(recovered) == 1

        delivery = recovered[0]

        assert delivery.message_id == message_id
        assert delivery.is_possible_duplicate
        assert delivery.payloads[0].data == _payload_text.encode('utf8')

        # .. and once it confirms the delivery, nothing is pending.
        receive_log.confirm(delivery.identity, delivery.cpa_id)

        assert _status_of(database.engine, message_id) == MessageStatus.Processed
        assert pending_deliveries(receive_log, _page_size) == []

        writer.stop()

# ################################################################################################################################
# ################################################################################################################################
