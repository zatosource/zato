# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The notification targets live in the alerting sweep job's extra data - one JSON
# block naming the default webhooks, the email connection and its addressing,
# and the Dashboard address the links point to. The config screen's notifications
# row and enmasse both read and write it through here, so a value shown, a value
# saved and a value imported are always the same value.

from __future__ import annotations

# stdlib
import json

# Zato
from zato.common.api import Alerting
from zato.common.odb.model import Job

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The keys the notifications row edits, in their screen order.
notification_keys = [
    Alerting.Extra_Slack_Webhook,
    Alerting.Extra_Teams_Webhook,
    Alerting.Extra_Webhook_URL,
    Alerting.Extra_Email_Connection,
    Alerting.Extra_Default_To,
    Alerting.Extra_From,
    Alerting.Extra_Dashboard_URL,
]

# ################################################################################################################################
# ################################################################################################################################

def parse_extra(extra:'any_') -> 'stranydict':
    """ The sweep job's extra as a dict - the column is user-editable free text,
    so anything that is not a JSON object simply means nothing was configured.
    """
    if isinstance(extra, bytes):
        extra = extra.decode('utf8')

    if not extra:
        return {}

    try:
        parsed = json.loads(extra)
    except ValueError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed

# ################################################################################################################################

def read_notification_config(extra:'any_') -> 'stranydict':
    """ The notification values the extra holds, every screen key present -
    a key the extra does not carry reads as an empty string.
    """
    parsed = parse_extra(extra)

    # Our response to produce
    out:'stranydict' = {}

    for key in notification_keys:
        if key in parsed:
            out[key] = parsed[key]
        else:
            out[key] = ''

    return out

# ################################################################################################################################

def set_notification_config(session:'any_', cluster_id:'int', values:'stranydict') -> 'bool':
    """ Writes the given notification values into the sweep job's extra, merging
    with whatever other keys the extra already carries - the commit stays with
    the caller. Returns whether the row actually changed.
    """
    job = session.query(Job).\
        filter(Job.name==Alerting.Job_Name).\
        filter(Job.cluster_id==cluster_id).\
        one()

    parsed = parse_extra(job.extra)

    # Only the notification keys are ours to write - an empty value removes
    # its key, so the extra never fills up with blanks.
    for key in notification_keys:

        if key not in values:
            continue

        value = values[key]

        if value:
            parsed[key] = value
        elif key in parsed:
            del parsed[key]

    # An extra with nothing left in it is stored as empty text, not as an empty object
    if parsed:
        new_extra = json.dumps(parsed)
    else:
        new_extra = ''

    current_extra = job.extra

    # The column is nullable, so a job that never carried an extra holds None
    if current_extra is None:
        current_extra = ''

    if isinstance(current_extra, bytes):
        current_extra = current_extra.decode('utf8')

    # The same text means nothing to store
    if current_extra == new_extra:
        return False

    job.extra = new_extra
    session.add(job)

    return True

# ################################################################################################################################
# ################################################################################################################################
