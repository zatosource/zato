# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.rule_engine.sql.constants import Event_Type_Advisory_Run, Event_Type_Decisions_Spiked, \
    Event_Type_Version_Published, Event_Type_Version_Restored

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleEventRecord
    from zato.common.typing_ import dictlist

# ################################################################################################################################
# ################################################################################################################################

# The complete, fixed set of events that destinations are notified about -
# each entry names the event the way a business admin sees it, with its internal code alongside.
Notification_Matrix = (
    {
        'code': Event_Type_Version_Published,
        'name': 'A version goes live',
        'description': 'Someone publishes a version of this ruleset, making it the one that decides from now on.',
        'example': "'Loan approval' version 12 is live, published by Sarah - 2 rules updated (Preferential_rate).",
    },
    {
        'code': Event_Type_Version_Restored,
        'name': 'A rollback happens',
        'description': 'Someone restores an earlier version of this ruleset, which goes live as a new version.',
        'example': "'Loan approval' was rolled back to version 11 by Mike, now live as version 14.",
    },
    {
        'code': Event_Type_Advisory_Run,
        'name': 'Advisory tests fail',
        'description': 'A new version fails the test suites attached to this ruleset - passing runs stay quiet.',
        'example': "2 of 9 scenarios fail against version 12 of 'Loan approval' (suite 'Loan suite').",
    },
    {
        'code': Event_Type_Decisions_Spiked,
        'name': 'Decision traffic spikes',
        'description': 'This ruleset suddenly decides far more often than it typically does.',
        'example': "'Loan approval' decided 4,200 times in the last hour against a typical 300.",
    },
)

# The event types the notify loop reads from the feed for delivery.
Notified_Event_Types = [
    Event_Type_Version_Published,
    Event_Type_Version_Restored,
    Event_Type_Advisory_Run,
    Event_Type_Decisions_Spiked,
]

# ################################################################################################################################
# ################################################################################################################################

def notification_matrix() -> 'dictlist':
    """ Returns the complete event matrix as a serializable list.
    """
    out = []

    for entry in Notification_Matrix:
        out.append(dict(entry))

    return out

# ################################################################################################################################

def should_notify(event:'RuleEventRecord') -> 'bool':
    """ Decides whether one feed event turns into a message - most notified types always do,
    advisory runs only when they carry failures.
    """
    # Advisory runs stay quiet unless something failed ..
    if event.event_type == Event_Type_Advisory_Run:

        # The payload column is nullable in the database, though advisory events always write one.
        if event.payload is None:
            out = False
        else:
            payload = json.loads(event.payload)
            out = payload['failed'] > 0

    # .. while every other notified type always produces a message.
    else:
        out = event.event_type in Notified_Event_Types

    return out

# ################################################################################################################################
# ################################################################################################################################
