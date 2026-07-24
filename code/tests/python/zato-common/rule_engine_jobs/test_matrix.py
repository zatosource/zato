# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from datetime import datetime

# Zato
from zato.common.rule_engine.notify.matrix import notification_matrix, Notified_Event_Types, should_notify
from zato.common.rule_engine.sql import RuleEventRecord
from zato.common.rule_engine.sql.constants import Event_Type_Advisory_Run, Event_Type_Decisions_Spiked, \
    Event_Type_Follow_Changed, Event_Type_Version_Created, Event_Type_Version_Published, Event_Type_Version_Restored

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def _event(event_type:'str', payload:'anydict | None') -> 'RuleEventRecord':
    """ Builds a detached feed event of one type.
    """
    if payload is None:
        payload_text = None
    else:
        payload_text = json.dumps(payload)

    out = RuleEventRecord(
        id=1,
        cluster_id=1,
        definition_id=1,
        version=1,
        event_type=event_type,
        actor='sarah.p',
        subject_id=None,
        bucket_start=None,
        event_count=None,
        created_at=datetime(2026, 7, 20, 10, 15),
        payload=payload_text,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_matrix_lists_every_notified_event() -> 'None':
    """ Each matrix entry pairs a business name with its internal code, a description and an example.
    """
    items = notification_matrix()

    codes = []
    for item in items:
        codes.append(item['code'])
        assert item['name']
        assert item['description']
        assert item['example']

    assert codes == Notified_Event_Types

# ################################################################################################################################

def test_quiet_events_are_not_in_the_notified_set() -> 'None':
    """ Follows and mere version saves stay out of the notified set by default.
    """
    assert Event_Type_Follow_Changed not in Notified_Event_Types
    assert Event_Type_Version_Created not in Notified_Event_Types

# ################################################################################################################################

def test_publications_rollbacks_and_spikes_always_notify() -> 'None':
    """ The always-on notified types produce a message no matter their payload.
    """
    published = _event(Event_Type_Version_Published, {'published_version': 2})
    restored = _event(Event_Type_Version_Restored, {'source_version': 1, 'comment': 'Roll back'})
    spiked = _event(Event_Type_Decisions_Spiked, {'hour': '2026-07-20T10', 'count': 4200, 'typical': 300})

    assert should_notify(published) is True
    assert should_notify(restored) is True
    assert should_notify(spiked) is True

# ################################################################################################################################

def test_advisory_runs_notify_only_on_failures() -> 'None':
    """ A passing advisory run stays quiet, a failing one notifies.
    """
    passing_payload = {'test_set_id': 2, 'test_set_name': 'Loan suite', 'total': 3, 'passed': 3, 'failed': 0, 'explored': 0}
    failing_payload = {'test_set_id': 2, 'test_set_name': 'Loan suite', 'total': 3, 'passed': 1, 'failed': 2, 'explored': 0}

    passing = _event(Event_Type_Advisory_Run, passing_payload)
    failing = _event(Event_Type_Advisory_Run, failing_payload)

    assert should_notify(passing) is False
    assert should_notify(failing) is True

# ################################################################################################################################
# ################################################################################################################################
