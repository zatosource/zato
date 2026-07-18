# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The demo-data seeder - one deterministic run fills the audit database with a week
# of realistic HL7 traffic so every screen has something meaningful to show:
# hourly traffic curves, an error burst, a feed gone silent, alerts in all three
# lifecycle states, a batch with lineage, a resubmit chain, dedup ledger entries
# and a config-change history. All content comes from the shipped fakers through
# the sample feed - nothing is authored here. The seeder is a permanent asset,
# the same run backs the dashboard's "Import demo data" action.

# stdlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from json import dumps
from random import Random

# SQLAlchemy
from sqlalchemy import delete, select, update

# Zato
from zato.common.alerting.model import new_finding, AlertAction, AlertSeverity, FindingKind
from zato.common.alerting.engine import record_alert_event
from zato.common.alerting.store import observe_alert, raise_alert, resolve_alert
from zato.common.alerting.sweep import parse_rule
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import alert_table, event_dedup_table
from zato.common.audit_log.config_audit import record_config_change, record_view_event
from zato.common.audit_log.dedup import acquire_dedup_key, build_dedup_key, complete_dedup_key
from zato.common.hl7.audit import audit_ack_received, audit_ack_sent, audit_batch_received, audit_message_received, \
    audit_message_sent, get_audit_attrs, ACKStatus
from zato.common.hl7.feed import generate_feed_items, rewrite_msh_field, FeedConfig, MSH10_Index
from zato.common.util.api import utcnow
from zato.hl7v2 import parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, dictlist, intnone

    anylist = anylist
    AuditLog = AuditLog
    dictlist = dictlist
    Engine = Engine
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

# Every demo event's cid starts with this prefix - it is what the purge deletes by
Cid_Prefix = 'demo-'

# Every demo alert rule's name starts with this prefix
Rule_Name_Prefix = 'demo.'

# The demo channels - a busy hospital ADT feed, a lab results feed
# and a small clinic feed that goes silent
Channel_Main   = 'demo.hl7.adt.main'
Channel_Lab    = 'demo.hl7.oru.lab'
Channel_Clinic = 'demo.hl7.adt.clinic'

# The demo outgoing connections - an MLLP forward to an EHR and a FHIR server
Outconn_Forward = 'demo.hl7.forward.ehr'
Outconn_FHIR    = 'demo.fhir.ehr'

# The MSH-3 sending applications routing live messages to the demo channels
Route_Main   = 'DEMO_HOSPITAL_ADT'
Route_Lab    = 'DEMO_LAB_ORU'
Route_Clinic = 'DEMO_CLINIC_ADT'

# The people appearing in the demo's config-change and alert history
Actor_Admin    = 'demo.admin'
Actor_Operator = 'demo.operator'

# The names of the demo alert rules
Rule_Feed_Silent = 'demo.alert.feed-silent-clinic'
Rule_Error_Rate  = 'demo.alert.error-rate-lab'
Rule_Missing_Ack = 'demo.alert.missing-ack-ehr'

# The screen name view-access events are recorded under
Screen_Browser = 'audit-log-browser'

# ################################################################################################################################

# How busy each hour of the day is, midnight first - a hospital's double-peaked
# working day with a quiet night, the weights drive the traffic curve
Hourly_Weights = (2, 1, 1, 1, 1, 2, 4, 7, 10, 12, 14, 13, 11, 12, 14, 13, 11, 9, 7, 5, 4, 3, 3, 2)

# The hour the clinic feed falls silent at on the seed's last day
Clinic_Silent_Hour = 6

# The error burst on the lab channel - which hours of the previous day it spans
Burst_Start_Hour = 14
Burst_End_Hour   = 16

# What fraction of burst messages fail
Burst_Error_Ratio = 0.65

# What fraction of messages fail outside the burst
Base_Error_Ratio = 0.02

# What fraction of accepted main-channel messages are forwarded onwards
Forward_Ratio = 0.5

# What fraction of forwarded messages never receive an acknowledgment
Forward_Timeout_Ratio = 0.03

# How many recent sends are still awaiting their acknowledgment -
# the outstanding filter's demo cases
In_Flight_Count = 3

# What share of ADT traffic the main channel takes, the clinic gets the rest
Main_Channel_Share = 0.75

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SeedConfig:
    """ How one seed run behaves - its size, its span and its reproducibility.
    """

    # The seed every random draw comes from - one value fixes the whole run
    seed:'int' = 20260101

    # How many days back the traffic reaches
    days:'int' = 7

    # How many messages one day carries on average
    messages_per_day:'int' = 240

    # How many extra messages the error burst adds
    burst_message_count:'int' = 60

    # How many FHIR request/response pairs the run writes
    fhir_pair_count:'int' = 30

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SeedResult:
    """ What one seed run produced - the counts the caller reports onwards.
    """

    message_count:'int' = 0
    event_count:'int' = 0
    alert_count:'int' = 0
    fhir_pair_count:'int' = 0
    config_event_count:'int' = 0
    dedup_count:'int' = 0
    channel_names:'list' = field(default_factory=list)
    rule_names:'list' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _PlannedMessage:
    """ One message the plan places in time before anything is written.
    """

    when:'datetime' = None # type: ignore[assignment]
    channel_name:'str' = ''
    text:'str' = ''
    control_id:'str' = ''
    is_error:'bool' = False
    is_forwarded:'bool' = False

# ################################################################################################################################
# ################################################################################################################################

def get_demo_rule_defs() -> 'dictlist':
    """ Returns the demo alert rules in the dict shape they are stored in -
    the same defs parse into AlertRule objects for the seeded alert history.
    """
    out = [
        {
            'name': Rule_Feed_Silent,
            'is_active': True,
            'kind': FindingKind.Feed_Silent,
            'source': AuditSource.HL7,
            'object_name': Channel_Clinic,
            'action': AlertAction.Email_Digest,
            'action_config': {},
            'config': {'silent_after_seconds': 7200},
            'dedup_window_seconds': 86400,
        },
        {
            'name': Rule_Error_Rate,
            'is_active': True,
            'kind': FindingKind.Error_Rate,
            'source': AuditSource.HL7,
            'object_name': Channel_Lab,
            'action': AlertAction.Email_Digest,
            'action_config': {},
            'config': {'window_seconds': 900, 'threshold': 10},
            'dedup_window_seconds': 7200,
        },
        {
            'name': Rule_Missing_Ack,
            'is_active': True,
            'kind': FindingKind.Missing_Followup,
            'source': AuditSource.HL7,
            'object_name': Outconn_Forward,
            'action': AlertAction.Email_Digest,
            'action_config': {},
            'config': {'deadline_seconds': 300},
            'dedup_window_seconds': 7200,
        },
    ]

    return out

# ################################################################################################################################

def purge_demo_data(engine:'Engine') -> 'None':
    """ Removes everything a previous seed run wrote - running the import twice
    leaves one clean data set, not two stacked ones.
    """

    # The demo events are found by their cid prefix ..
    statement = select(event_table.c.id).where(event_table.c.cid.like(Cid_Prefix + '%'))

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    event_ids = [row[0] for row in rows]

    with engine.begin() as connection:

        # .. their dependent rows go first ..
        if event_ids:
            _ = connection.execute(delete(event_body_table).where(event_body_table.c.event_id.in_(event_ids)))
            _ = connection.execute(delete(event_attr_table).where(event_attr_table.c.event_id.in_(event_ids)))
            _ = connection.execute(delete(event_link_table).where(event_link_table.c.child_event_id.in_(event_ids)))
            _ = connection.execute(delete(event_table).where(event_table.c.id.in_(event_ids)))

        # .. the demo alerts are filed under demo rule names ..
        _ = connection.execute(delete(alert_table).where(alert_table.c.rule_name.like(Rule_Name_Prefix + '%')))

        # .. and the demo dedup entries share the event cid prefix.
        _ = connection.execute(delete(event_dedup_table).where(event_dedup_table.c.cid.like(Cid_Prefix + '%')))

# ################################################################################################################################

def _draw_time(rng:'Random', now:'datetime', days:'int') -> 'datetime':
    """ Draws one timestamp within the seeded span - a uniform day, an hour
    from the working-day curve, and a uniform minute and second.
    """
    day_offset = rng.randrange(days)
    hour = rng.choices(range(24), weights=Hourly_Weights)[0]
    minute = rng.randrange(60)
    second = rng.randrange(60)

    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=day_offset)
    out = day_start + timedelta(hours=hour, minutes=minute, seconds=second)

    return out

# ################################################################################################################################

def _build_ack_text(ack_code:'str', control_id:'str') -> 'str':
    """ Builds the minimal acknowledgment message a channel would send back.
    """
    msh = 'MSH|^~\\&|ZATO|ZATO|DEMO|DEMO|20260101000000||ACK|{}|P|2.4'.format(control_id)
    msa = 'MSA|{}|{}'.format(ack_code, control_id)

    out = msh + '\r' + msa
    return out

# ################################################################################################################################

def _build_plan(config:'SeedConfig', now:'datetime') -> 'anylist':
    """ Lays the whole week of messages out in time before anything is written -
    writing in chronological order keeps event ids aligned with event times.
    """
    rng = Random(config.seed)

    total_count = config.days * config.messages_per_day + config.burst_message_count

    feed_config = FeedConfig()
    feed_config.seed = config.seed

    items = generate_feed_items(total_count, feed_config)

    # The lab burst draws from the ORU items, everything else flows normally
    oru_items = [item for item in items if item.msg_type.startswith('ORU')]
    burst_items = oru_items[:config.burst_message_count]
    burst_ids = {id(item) for item in burst_items}

    # The moments the special windows hinge on
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    clinic_cutoff = today_start + timedelta(hours=Clinic_Silent_Hour)
    burst_start = today_start - timedelta(days=1) + timedelta(hours=Burst_Start_Hour)
    burst_seconds = (Burst_End_Hour - Burst_Start_Hour) * 3600

    # Our response to produce
    out:'anylist' = []

    for item in items:

        planned = _PlannedMessage()
        planned.text = item.text
        planned.control_id = item.control_id

        # A burst message lands inside the previous day's two-hour window
        # and fails most of the time ..
        if id(item) in burst_ids:
            planned.channel_name = Channel_Lab
            planned.when = burst_start + timedelta(seconds=rng.randrange(burst_seconds))
            planned.is_error = rng.random() < Burst_Error_Ratio

        # .. everything else follows the working-day curve.
        else:

            if item.msg_type.startswith('ORU'):
                planned.channel_name = Channel_Lab
            elif rng.random() < Main_Channel_Share:
                planned.channel_name = Channel_Main
            else:
                planned.channel_name = Channel_Clinic

            when = _draw_time(rng, now, config.days)

            # Nothing is dated into the future ..
            while when > now:
                when = _draw_time(rng, now, config.days)

            # .. and the clinic went silent this morning, so its later
            # messages are redrawn into the time it was still alive.
            if planned.channel_name == Channel_Clinic:
                while when > clinic_cutoff:
                    when = _draw_time(rng, now, config.days)

            planned.when = when
            planned.is_error = rng.random() < Base_Error_Ratio

        # Accepted main-channel messages flow onwards to the EHR
        is_forward_candidate = planned.channel_name == Channel_Main and not planned.is_error
        planned.is_forwarded = is_forward_candidate and rng.random() < Forward_Ratio

        out.append(planned)

    # Chronological order keeps ids and times aligned
    out.sort(key=lambda planned: planned.when)

    return out

# ################################################################################################################################

def _write_messages(
    audit_log:'AuditLog',
    plan:'anylist',
    rng:'Random',
    backdates:'anylist',
    ) -> 'int':
    """ Writes the planned messages through the same producers the live wire uses -
    a received event and its acknowledgment per message, plus the forwarded pair
    on the outgoing connection where the plan says so. Returns the message count.
    """

    for index, planned in enumerate(plan):

        cid = f'{Cid_Prefix}{index + 1:08d}'
        when_iso = planned.when.isoformat()

        message = parse_hl7(planned.text, validate=False)
        attrs = get_audit_attrs(message)

        # The receipt itself
        received_id = audit_message_received(
            audit_log, planned.channel_name, planned.text,
            cid=cid, msg_id=planned.control_id, attrs=attrs, endpoint='mllp://demo')
        backdates.append((received_id, when_iso))

        # The acknowledgment follows within the handling time
        if planned.is_error:
            ack_code = ACKStatus.Application_Error
            duration_ms = rng.randrange(40, 400)
        else:
            ack_code = ACKStatus.Application_Accept
            duration_ms = rng.randrange(5, 120)

        ack_text = _build_ack_text(ack_code, planned.control_id)
        ack_when = planned.when + timedelta(milliseconds=duration_ms)

        ack_id = audit_ack_sent(
            audit_log, planned.channel_name, ack_code, ack_text,
            cid=cid, msg_id=planned.control_id, duration_ms=duration_ms)
        backdates.append((ack_id, ack_when.isoformat()))

        # The forwarded pair on the outgoing connection
        if planned.is_forwarded:

            sent_when = ack_when + timedelta(milliseconds=rng.randrange(50, 300))
            sent_id = audit_message_sent(
                audit_log, Outconn_Forward, planned.text,
                cid=cid, msg_id=planned.control_id, attrs=attrs, endpoint='mllp://demo-ehr')
            backdates.append((sent_id, sent_when.isoformat()))

            # A small share of forwards never hears back
            if rng.random() < Forward_Timeout_Ratio:
                forward_ack_code = ACKStatus.Timeout
                forward_duration_ms = 30_000
            else:
                forward_ack_code = ACKStatus.Application_Accept
                forward_duration_ms = rng.randrange(20, 250)

            forward_ack_when = sent_when + timedelta(milliseconds=forward_duration_ms)
            forward_ack_id = audit_ack_received(
                audit_log, Outconn_Forward, forward_ack_code,
                cid=cid, msg_id=planned.control_id, duration_ms=forward_duration_ms)
            backdates.append((forward_ack_id, forward_ack_when.isoformat()))

    return len(plan)

# ################################################################################################################################

def _write_in_flight_sends(
    audit_log:'AuditLog',
    config:'SeedConfig',
    now:'datetime',
    rng:'Random',
    backdates:'anylist',
    ) -> 'None':
    """ Writes a few very recent sends with no acknowledgment following them -
    what the outstanding filter surfaces as the open exchanges.
    """

    feed_config = FeedConfig()
    feed_config.seed = config.seed + 2

    items = generate_feed_items(In_Flight_Count, feed_config)

    for index, item in enumerate(items):

        # Control ids of their own - the week's acknowledged messages must not
        # close these exchanges through a shared control id.
        control_id = f'DEMO-IF-{index + 1:08d}'
        text = rewrite_msh_field(item.text, MSH10_Index, control_id)

        message = parse_hl7(text, validate=False)
        attrs = get_audit_attrs(message)

        # Each send went out within the last minutes and nothing has come back yet
        when = now - timedelta(minutes=rng.randrange(2, 30))
        cid = f'{Cid_Prefix}if-{index + 1:08d}'

        sent_id = audit_message_sent(
            audit_log, Outconn_Forward, text,
            cid=cid, msg_id=control_id, attrs=attrs, endpoint='mllp://demo-ehr')
        backdates.append((sent_id, when.isoformat()))

# ################################################################################################################################

def _write_batch(
    audit_log:'AuditLog',
    engine:'Engine',
    config:'SeedConfig',
    now:'datetime',
    backdates:'anylist',
    ) -> 'None':
    """ Writes one FHS/BHS batch with its parent row and per-message children -
    the lineage view's demo case.
    """

    feed_config = FeedConfig()
    feed_config.seed = config.seed + 1

    items = generate_feed_items(3, feed_config)
    body = '\r'.join(item.text for item in items)

    batch_text = 'BHS|^~\\&|DEMO_BATCH|GENERAL_HOSPITAL|ZATO|ZATO|20260101000000\r' + body + '\rBTS|3'

    batch_cid = f'{Cid_Prefix}batch-00000001'
    _ = audit_batch_received(audit_log, Channel_Main, batch_text, cid=batch_cid, endpoint='mllp://demo')

    # The parent and all its children share one cid, so they are backdated together
    batch_when = now.replace(hour=11, minute=0, second=0, microsecond=0) - timedelta(days=2)
    batch_when_iso = batch_when.isoformat()

    statement = select(event_table.c.id).where(event_table.c.cid == batch_cid)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    for row in rows:
        backdates.append((row[0], batch_when_iso))

# ################################################################################################################################

def _write_resubmit_chain(
    audit_log:'AuditLog',
    engine:'Engine',
    now:'datetime',
    rng:'Random',
    backdates:'anylist',
    ) -> 'intnone':
    """ Writes the repair story - one of the burst's failed messages reprocessed
    successfully, the new events linked to the original by the correlation id.
    Returns the original event's id.
    """

    # The original is the burst's first failed receipt
    statement = select(event_table.c.id, event_table.c.cid, event_table.c.msg_id, event_table.c.object_name)
    statement = statement.where(event_table.c.object_name == Channel_Lab)
    statement = statement.where(event_table.c.event_type == AuditEvent.Message_Received)
    statement = statement.order_by(event_table.c.id)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    # The failed one is found through its error acknowledgment
    original = None

    for row in rows:
        ack_statement = select(event_table.c.id).where(event_table.c.cid == row[1])
        ack_statement = ack_statement.where(event_table.c.event_type == AuditEvent.Ack_Sent)
        ack_statement = ack_statement.where(event_table.c.outcome == AuditOutcome.Error)

        with engine.connect() as connection:
            ack_rows = connection.execute(ack_statement).fetchall()

        if ack_rows:
            original = row
            break

    if not original:
        return None

    # The payload comes from the original's stored body
    body_statement = select(event_body_table.c.data).where(event_body_table.c.event_id == original[0])

    with engine.connect() as connection:
        body_rows = connection.execute(body_statement).fetchall()

    payload = body_rows[0][0]

    # The repair happened this morning, two hours ago
    repair_when = now - timedelta(hours=2)
    repair_cid = f'{Cid_Prefix}rp-00000001'

    message = parse_hl7(payload, validate=False)
    attrs = get_audit_attrs(message)

    # The reprocessed receipt mirrors what the reprocess handler writes
    reprocess_id = audit_log.insert(
        AuditSource.HL7, AuditEvent.Message_Received, original[3],
        cid=repair_cid,
        msg_id=original[2],
        correl_id=original[1],
        size=len(payload),
        outcome=AuditOutcome.OK,
        data=dumps({'payload': payload}),
        attrs=attrs,
        parents=[original[0]],
    )
    backdates.append((reprocess_id, repair_when.isoformat()))

    # This time the acknowledgment accepts
    duration_ms = rng.randrange(5, 120)
    ack_text = _build_ack_text(ACKStatus.Application_Accept, original[2])
    ack_when = repair_when + timedelta(milliseconds=duration_ms)

    ack_id = audit_ack_sent(
        audit_log, original[3], ACKStatus.Application_Accept, ack_text,
        cid=repair_cid, msg_id=original[2], duration_ms=duration_ms)
    backdates.append((ack_id, ack_when.isoformat()))

    # The reprocess went through the dedup ledger too - one completed claim
    dedup_key = build_dedup_key('reprocess', original[0], payload)
    _ = acquire_dedup_key(engine, dedup_key, repair_cid, 'reprocess')
    complete_dedup_key(engine, dedup_key, AuditOutcome.OK)

    return original[0]

# ################################################################################################################################

def _write_dedup_entries(engine:'Engine') -> 'int':
    """ Writes the dedup ledger's remaining demo entries - one more completed claim
    and one still in doubt, the ledger screen's demo cases. Returns how many
    ledger rows the whole run owns.
    """

    # A completed resend claim from earlier today
    completed_key = build_dedup_key('resend', 2, 'demo-resend-payload')
    _ = acquire_dedup_key(engine, completed_key, f'{Cid_Prefix}dd-00000001', 'resend')
    complete_dedup_key(engine, completed_key, AuditOutcome.OK)

    # A claim that never completed - the in-doubt screen's demo case
    in_doubt_key = build_dedup_key('resend', 3, 'demo-in-doubt-payload')
    _ = acquire_dedup_key(engine, in_doubt_key, f'{Cid_Prefix}dd-00000002', 'resend')

    statement = select(event_dedup_table.c.id).where(event_dedup_table.c.cid.like(Cid_Prefix + '%'))

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    return len(rows)

# ################################################################################################################################

def _write_alerts(
    audit_log:'AuditLog',
    engine:'Engine',
    now:'datetime',
    backdates:'anylist',
    ) -> 'int':
    """ Writes the alert history - one alert in each lifecycle state, each with
    its audit trail, so the alerts screen shows all three colors. Returns
    the alert count.
    """

    rules = {}

    for rule_def in get_demo_rule_defs():
        rules[rule_def['name']] = parse_rule(rule_def['name'], rule_def)

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # The unobserved alert - the clinic feed fell silent this morning
    # and the finding repeated every half hour since
    silent_rule = rules[Rule_Feed_Silent]
    silent_finding = new_finding(
        FindingKind.Feed_Silent, AuditSource.HL7, Channel_Clinic,
        f'Feed on {Channel_Clinic} has been silent since {Clinic_Silent_Hour:02d}:00 UTC',
        severity=AlertSeverity.Warning)

    silent_when = today_start + timedelta(hours=Clinic_Silent_Hour, minutes=30)
    silent_index = 0

    while silent_when < now:
        result = raise_alert(engine, silent_rule, silent_finding, silent_when)
        silent_index += 1

        event_cid = f'{Cid_Prefix}al-silent-{silent_index:04d}'
        record_alert_event(audit_log, silent_rule, silent_finding, result.count, event_cid)
        backdates.append((_get_latest_event_id(engine, event_cid), silent_when.isoformat()))

        silent_when = silent_when + timedelta(minutes=30)

    # The observed alert - yesterday's error burst, acknowledged that evening
    error_rule = rules[Rule_Error_Rate]
    error_finding = new_finding(
        FindingKind.Error_Rate, AuditSource.HL7, Channel_Lab,
        f'Error rate on {Channel_Lab} exceeded 10 failures within 15 minutes',
        severity=AlertSeverity.Critical)

    burst_day = today_start - timedelta(days=1)
    error_alert_id = 0

    for minutes_offset in (10, 40, 80):
        error_when = burst_day + timedelta(hours=Burst_Start_Hour, minutes=minutes_offset)
        result = raise_alert(engine, error_rule, error_finding, error_when)
        error_alert_id = result.alert_id

        event_cid = f'{Cid_Prefix}al-error-{minutes_offset:04d}'
        record_alert_event(audit_log, error_rule, error_finding, result.count, event_cid)
        backdates.append((_get_latest_event_id(engine, event_cid), error_when.isoformat()))

    observed_when = burst_day + timedelta(hours=Burst_End_Hour, minutes=5)
    observe_alert(engine, error_alert_id, Actor_Admin, observed_when)

    # The resolved alert - a delivery stall from three days ago, repaired the same day
    missing_rule = rules[Rule_Missing_Ack]
    missing_finding = new_finding(
        FindingKind.Missing_Followup, AuditSource.HL7, Outconn_Forward,
        f'Messages sent through {Outconn_Forward} received no acknowledgment within 5 minutes',
        severity=AlertSeverity.Warning)

    missing_when = today_start - timedelta(days=3) + timedelta(hours=9)
    result = raise_alert(engine, missing_rule, missing_finding, missing_when)

    event_cid = f'{Cid_Prefix}al-missing-0001'
    record_alert_event(audit_log, missing_rule, missing_finding, result.count, event_cid)
    backdates.append((_get_latest_event_id(engine, event_cid), missing_when.isoformat()))

    resolved_when = missing_when + timedelta(hours=2, minutes=30)
    resolve_alert(engine, result.alert_id, Actor_Operator, resolved_when)

    # Three alerts exist - the increments folded into them
    return 3

# ################################################################################################################################

def _get_latest_event_id(engine:'Engine', cid:'str') -> 'int':
    """ Returns the newest event id under one cid - how a just-written
    event is found for backdating when the producer does not return it.
    """
    statement = select(event_table.c.id).where(event_table.c.cid == cid)
    statement = statement.order_by(event_table.c.id.desc()).limit(1)

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    return rows[0][0]

# ################################################################################################################################

def _write_config_history(
    audit_log:'AuditLog',
    now:'datetime',
    viewed_event_id:'intnone',
    backdates:'anylist',
    ) -> 'int':
    """ Writes the config-change history - the demo objects created a week ago,
    one edit later on and one view-access record. Returns the event count.
    """

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    created_when = today_start - timedelta(days=6) + timedelta(hours=9)

    # The creation of every demo connection, one minute apart
    created_names = [Channel_Main, Channel_Lab, Channel_Clinic, Outconn_Forward, Outconn_FHIR]
    count = 0

    for index, object_name in enumerate(created_names):

        after = {
            'name': object_name,
            'is_active': True,
            'pool_size': 1,
            'is_audit_log_active': True,
        }

        event_id = record_config_change(
            audit_log,
            action=AuditEvent.Config_Created,
            object_type='generic-connection',
            object_name=object_name,
            actor=Actor_Admin,
            cid=f'{Cid_Prefix}cfg-{index + 1:04d}',
            after=after,
        )

        change_when = created_when + timedelta(minutes=index)
        backdates.append((event_id, change_when.isoformat()))
        count += 1

    # The lab channel's pool grew two days ago
    edited_when = today_start - timedelta(days=2) + timedelta(hours=15)

    event_id = record_config_change(
        audit_log,
        action=AuditEvent.Config_Edited,
        object_type='generic-connection',
        object_name=Channel_Lab,
        actor=Actor_Operator,
        cid=f'{Cid_Prefix}cfg-0006',
        before={'name': Channel_Lab, 'pool_size': 1},
        after={'name': Channel_Lab, 'pool_size': 2},
    )
    backdates.append((event_id, edited_when.isoformat()))
    count += 1

    # Somebody opened the failed message's body yesterday evening
    if viewed_event_id:

        viewed_when = today_start - timedelta(days=1) + timedelta(hours=16, minutes=10)

        event_id = record_view_event(
            audit_log,
            actor=Actor_Admin,
            viewed_event_id=viewed_event_id,
            screen=Screen_Browser,
            cid=f'{Cid_Prefix}cfg-0007',
        )
        backdates.append((event_id, viewed_when.isoformat()))
        count += 1

    return count

# ################################################################################################################################

def _write_fhir_traffic(
    audit_log:'AuditLog',
    config:'SeedConfig',
    now:'datetime',
    rng:'Random',
    backdates:'anylist',
    ) -> 'int':
    """ Writes the FHIR side of the demo - request/response pairs on the FHIR
    outgoing connection, spread over the same span as the HL7 traffic.
    Returns the pair count.
    """

    resource_types = ('Patient', 'Observation', 'Encounter')

    for index in range(config.fhir_pair_count):

        when = _draw_time(rng, now, config.days)

        while when > now:
            when = _draw_time(rng, now, config.days)

        cid = f'{Cid_Prefix}fhir-{index + 1:08d}'
        resource_type = rng.choice(resource_types)
        resource_id = rng.randrange(1000, 9999)
        path = f'/{resource_type}/{resource_id}'

        attrs = {
            'resource_type': resource_type,
            'method': 'GET',
        }

        stored_data = dumps({
            'payload': '',
            'method': 'get',
            'path': path,
        })

        request_id = audit_log.insert(
            AuditSource.FHIR, AuditEvent.Request_Sent, Outconn_FHIR,
            cid=cid,
            endpoint=f'GET {path}',
            outcome=AuditOutcome.OK,
            data=stored_data,
            attrs=attrs,
        )
        backdates.append((request_id, when.isoformat()))

        duration_ms = rng.randrange(15, 350)
        response_when = when + timedelta(milliseconds=duration_ms)

        response_id = audit_log.insert(
            AuditSource.FHIR, AuditEvent.Response_Received, Outconn_FHIR,
            cid=cid,
            outcome=AuditOutcome.OK,
            duration_ms=duration_ms,
            attrs=attrs,
        )
        backdates.append((response_id, response_when.isoformat()))

    return config.fhir_pair_count

# ################################################################################################################################

def _apply_backdates(engine:'Engine', backdates:'anylist') -> 'None':
    """ Moves every written event to its planned moment - the events and their
    stored bodies alike, in one transaction.
    """
    with engine.begin() as connection:

        for event_id, when_iso in backdates:

            statement = update(event_table).where(event_table.c.id == event_id)
            statement = statement.values(event_time_iso=when_iso)
            _ = connection.execute(statement)

            body_statement = update(event_body_table).where(event_body_table.c.event_id == event_id)
            body_statement = body_statement.values(event_time_iso=when_iso)
            _ = connection.execute(body_statement)

# ################################################################################################################################

def seed_demo_data(
    audit_log:'AuditLog',
    engine:'Engine',
    *,
    now:'datetime | None' = None,
    config:'SeedConfig | None' = None,
    ) -> 'SeedResult':
    """ Runs one full seed - a previous run's data is purged first, then the week
    of traffic, the batch, the resubmit chain, the dedup entries, the alerts,
    the config history and the FHIR side are written and backdated in place.
    The same seed always produces the same data set.
    """

    if now is None:
        now = utcnow()

    if config is None:
        config = SeedConfig()

    # A rerun replaces the previous data set instead of stacking on it
    purge_demo_data(engine)

    rng = Random(config.seed)

    # Every write records where it belongs in time, the move happens once at the end
    backdates:'anylist' = []

    # Our response to produce
    out = SeedResult()
    out.channel_names = [Channel_Main, Channel_Lab, Channel_Clinic]
    out.rule_names = [rule_def['name'] for rule_def in get_demo_rule_defs()]

    # The week of wire traffic
    plan = _build_plan(config, now)
    out.message_count = _write_messages(audit_log, plan, rng, backdates)

    # The open exchanges the outstanding filter surfaces
    _write_in_flight_sends(audit_log, config, now, rng, backdates)

    # The batch with its lineage
    _write_batch(audit_log, engine, config, now, backdates)

    # The repair story - reprocess plus its dedup claim
    repaired_event_id = _write_resubmit_chain(audit_log, engine, now, rng, backdates)

    # The rest of the dedup ledger
    out.dedup_count = _write_dedup_entries(engine)

    # The three alert lifecycles
    out.alert_count = _write_alerts(audit_log, engine, now, backdates)

    # The config-change history, including who viewed the repaired message
    out.config_event_count = _write_config_history(audit_log, now, repaired_event_id, backdates)

    # The FHIR request/response pairs
    out.fhir_pair_count = _write_fhir_traffic(audit_log, config, now, rng, backdates)

    # Everything moves to its planned moment at once
    _apply_backdates(engine, backdates)

    # The final count is what the database actually holds
    statement = select(event_table.c.id).where(event_table.c.cid.like(Cid_Prefix + '%'))

    with engine.connect() as connection:
        rows = connection.execute(statement).fetchall()

    out.event_count = len(rows)

    return out

# ################################################################################################################################
# ################################################################################################################################
