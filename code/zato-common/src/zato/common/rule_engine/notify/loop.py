# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger
from time import sleep

# Zato
from zato.common.rule_engine.notify.advisory import run_advisory_suites
from zato.common.rule_engine.notify.delivery import build_clients, send_message
from zato.common.rule_engine.notify.matrix import Notified_Event_Types, should_notify
from zato.common.rule_engine.notify.messages import build_message
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Event_Type_Version_Created, Job_Cursor_Advisory

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many feed events one pass reads per cursor.
Batch_Size = 50

# How long the resident loop sleeps between passes.
Default_Interval_Seconds = 5

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class NotifyRunResult:
    """ What one pass over the feed accomplished.
    """

    advisory_runs:     'int' = 0
    messages_sent:     'int' = 0
    delivery_failures: 'int' = 0

# ################################################################################################################################
# ################################################################################################################################

def _run_advisory_pass(backend:'RuleSQLBackend') -> 'int':
    """ Runs advisory suites for every new ruleset version past the advisory cursor.
    """
    out = 0

    # Read the feed strictly past where the previous pass ended ..
    cursor = backend.notifications.get_job_cursor(Job_Cursor_Advisory)
    events = backend.events.list_since(
        since_id=cursor,
        event_types=[Event_Type_Version_Created],
        limit=Batch_Size,
    )

    for event in events:

        # .. version events of vocabularies and suites also flow through here, only rulesets run suites ..
        definition = backend.definitions.get(event.definition_id)
        is_ruleset = definition.object_type == Definition_Type_Ruleset

        if is_ruleset:
            if event.version is not None:

                # .. one broken version must never block the whole feed, so failures
                # .. are logged loudly and the cursor still moves past the event.
                try:
                    results = run_advisory_suites(backend, event.definition_id, event.version)
                    out += len(results)
                except Exception:
                    logger.exception('Advisory suites failed for definition %s version %s',
                        event.definition_id, event.version)

        # .. every processed event moves the cursor, so a crash never repeats completed runs.
        backend.notifications.set_job_cursor(Job_Cursor_Advisory, event.id)

    return out

# ################################################################################################################################

def _run_delivery_pass(backend:'RuleSQLBackend', clients:'anydict', result:'NotifyRunResult') -> 'None':
    """ Delivers pending feed events to every active destination, each over its own cursor.
    """
    destinations = backend.notifications.list_destinations()

    for destination in destinations:

        # Read this destination's slice of the feed strictly past its cursor ..
        events = backend.events.list_since(
            since_id=destination.cursor_id,
            definition_id=destination.definition_id,
            event_types=Notified_Event_Types,
            limit=Batch_Size,
        )

        for event in events:

            # .. events below the notification threshold, like passing advisory runs,
            # .. move the cursor without producing a message ..
            if not should_notify(event):
                backend.notifications.advance_cursor(destination.id, event.id)
                continue

            # .. build and deliver the message, recording either outcome on the destination ..
            try:
                text = build_message(backend, event)
                send_message(clients, destination.kind, destination.target, text)

            # .. a failure leaves the cursor in place so the next pass retries,
            # .. and the error becomes visible in the dashboard.
            except Exception as e:
                logger.warning('Delivery to %s `%s` failed for event %s -> %s',
                    destination.kind, destination.target, event.id, e)
                backend.notifications.mark_failed(destination.id, str(e))
                result.delivery_failures += 1
                break

            # .. a success moves the cursor past the delivered event.
            else:
                backend.notifications.mark_delivered(destination.id, event.id)
                result.messages_sent += 1

# ################################################################################################################################
# ################################################################################################################################

def run_once(backend:'RuleSQLBackend', clients:'anydict | None' = None) -> 'NotifyRunResult':
    """ One complete pass - advisory runs first, so their failures are deliverable in the same pass,
    then message delivery over every destination's cursor.
    """

    # Our response to produce
    out = NotifyRunResult()

    # Advisory suites run before delivery so a failing run notifies without waiting a pass ..
    out.advisory_runs = _run_advisory_pass(backend)

    # .. clients are rebuilt each pass unless the caller supplies them, picking up credential changes ..
    if clients is None:
        clients = build_clients(backend)

    # .. and pending events flow out to their destinations.
    _run_delivery_pass(backend, clients, out)

    return out

# ################################################################################################################################

def run_forever(backend:'RuleSQLBackend', interval_seconds:'int' = Default_Interval_Seconds) -> 'None':
    """ The resident notify loop - one pass every few seconds, each pass isolated from the previous one's errors.
    """
    logger.info('Rule engine notify loop starting, interval %ss', interval_seconds)

    while True:

        # One broken pass must never end the resident process.
        try:
            result = run_once(backend)

            if result.messages_sent:
                suffix = 'message' if result.messages_sent == 1 else 'messages'
                logger.info('Notify pass sent %d %s', result.messages_sent, suffix)

        except Exception:
            logger.exception('Notify pass failed')

        sleep(interval_seconds)

# ################################################################################################################################
# ################################################################################################################################
