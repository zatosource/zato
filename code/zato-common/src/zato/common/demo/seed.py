# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The demo-data seeder - one deterministic run fills the audit database with a week
# of realistic HL7 traffic so every screen has something meaningful to show:
# hourly traffic curves, an error burst, a feed gone silent, alerts in all three
# lifecycle states, a batch with lineage, resubmit chains with the people behind
# them, content-viewed records, dedup ledger entries and a config-change history.
# All content comes from the shipped fakers through the sample feed - nothing is
# authored here. The seeder is a permanent asset, the same run backs
# the dashboard's "Import demo data" action.
#
# Events are not written one at a time - the whole run is collected in memory
# with its final timestamps and lands in the database in one bulk transaction,
# which turns minutes of per-event commits into milliseconds.

# stdlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from json import dumps
from random import Random

# SQLAlchemy
from sqlalchemy import delete, func, select

# Zato
from zato.common.alerting.model import new_finding, AlertAction, AlertSeverity, AlertState, FindingKind
from zato.common.alerting.engine import record_alert_event
from zato.common.alerting.sweep import parse_rule
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import alert_table, event_dedup_table
from zato.common.audit_log.config_audit import record_config_change, record_view_event
from zato.common.audit_log.dedup import build_dedup_key
from zato.common.hl7.audit import audit_ack_received, audit_ack_sent, audit_batch_received, audit_message_received, \
    audit_message_sent, get_audit_attrs, ACKStatus
from zato.common.hl7.feed import generate_feed_items, rewrite_msh_field, FeedConfig, MSH10_Index
from zato.common.util.api import utcnow
from zato.hl7v2 import parse_hl7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.alerting.model import AlertRule, Finding
    from zato.common.audit_log.buffer import pending_event_list
    from zato.common.typing_ import anydict, anylist, anytuple, dictlist, intanydict, intnone

    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    AlertRule = AlertRule
    Connection = Connection
    dictlist = dictlist
    Engine = Engine
    Finding = Finding
    intanydict = intanydict
    intnone = intnone
    pending_event_list = pending_event_list

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

# The fraction of a second a moment is drawn from. A message arrives when it arrives, not on
# a whole second, and a demo whose events all land on one is a demo that reads as made up -
# it is also the fraction that tells two events of the same exchange apart.
Microseconds_Per_Second = 1_000_000

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
In_Flight_Count = 8

# What share of ADT traffic the main channel takes, the clinic gets the rest
Main_Channel_Share = 0.75

# How many failed messages get a resubmit chain of their own -
# the flow page's demo DAGs
Resubmit_Count = 12

# Every chain this many gets a first reprocess that fails and a second one
# that goes through - a two-hop DAG
Second_Hop_Every = 3

# How many content-viewed records the access log carries
View_Count = 40

# The people whose names appear on resubmits and body views
Actors = (Actor_Admin, Actor_Operator)

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
    messages_per_day:'int' = 1200

    # How many extra messages the error burst adds
    burst_message_count:'int' = 180

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
    resubmit_count:'int' = 0
    view_count:'int' = 0
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

@dataclass(init=False)
class _ResubmitSource:
    """ One failed message a resubmit chain reprocesses - captured while
    the week's traffic is written, so nothing needs to be read back later.
    The chain fields are filled in when the chain itself is written, which
    is what the dedup ledger rows are later derived from.
    """

    relative_received_id:'int' = 0
    cid:'str' = ''
    control_id:'str' = ''
    text:'str' = ''
    channel_name:'str' = ''
    when:'datetime' = None # type: ignore[assignment]

    # Filled in by the chain writer - the chain's cid, its stamped moments
    # and who asked for the resubmit
    chain_cid:'str' = ''
    chain_created_iso:'str' = ''
    chain_completed_iso:'str' = ''
    chain_actor:'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _PlannedView:
    """ One content-viewed record planned during the traffic pass - it embeds
    the viewed event's real database id, so it is written after the main commit.
    """

    relative_event_id:'int' = 0
    actor:'str' = ''
    when:'datetime' = None # type: ignore[assignment]

# ################################################################################################################################
# ################################################################################################################################

class _BulkAuditLog(AuditLog):
    """ An audit log that collects events in memory instead of writing each one
    in its own transaction. Every insert returns a relative id - the event's
    1-based position in the collection - and write_collected later lands
    everything in the database in bulk, mapping the relative ids to real ones.
    A settable clock stamps each event with its planned moment at collection
    time, so no backdating pass is needed afterwards.
    """

    def __init__(self, server_name:'str') -> 'None':

        # flush_max_size=1 routes every insert through _write_batch synchronously,
        # which is where this class collects instead of writing
        super().__init__(server_name, flush_max_size=1)

        # Everything collected so far - an event's position here is its relative id
        self.pending_events:'anylist' = []

        # How many of the collected events write_collected has already written
        self.written_count = 0

        # What the collected events are stamped with instead of the wall clock
        self.event_time_iso = ''

# ################################################################################################################################

    def set_event_time(self, when:'datetime') -> 'None':
        """ Sets the moment the next collected events are stamped with.
        """
        self.event_time_iso = when.isoformat()

# ################################################################################################################################

    def _write_batch(self, batch:'pending_event_list') -> 'intnone':
        """ Collects instead of writing - the returned relative id is the event's
        1-based position in the collection.
        """

        # Our response to produce
        out:'intnone' = None

        for pending in batch:

            # The planned moment replaces the wall-clock time assigned by insert
            pending.values['event_time_iso'] = self.event_time_iso

            self.pending_events.append(pending)
            out = len(self.pending_events)

        return out

# ################################################################################################################################

    def write_collected(self, connection:'Connection') -> 'intanydict':
        """ Writes everything collected but not yet written, in bulk, on the given
        connection - one executemany per table. Returns the relative-to-real id map
        covering all collected events.
        """

        to_write = self.pending_events[self.written_count:]

        # The event rows go first, so everything else can reference their ids
        if to_write:
            event_rows = [pending.values for pending in to_write]
            _ = connection.execute(event_table.insert(), event_rows)

        # The real ids come from one read-back - (cid, cid_sequence) is unique
        # per event within one writer, so it keys the map exactly
        statement = select(event_table.c.id, event_table.c.cid, event_table.c.cid_sequence)
        statement = statement.where(event_table.c.cid.like(Cid_Prefix + '%'))

        rows = connection.execute(statement).fetchall()
        real_id_by_key = {(row[1], row[2]): row[0] for row in rows}

        # Our response to produce
        out:'intanydict' = {}

        for index, pending in enumerate(self.pending_events):
            key = (pending.values['cid'], pending.values['cid_sequence'])
            out[index + 1] = real_id_by_key[key]

        # The companion rows of the newly written events, with real ids filled in
        attr_rows:'anylist' = []
        body_rows:'anylist' = []
        link_rows:'anylist' = []

        for index, pending in enumerate(to_write, start=self.written_count):

            event_id = out[index + 1]

            if pending.attrs:
                attr_rows.extend(self._build_attr_rows(event_id, pending.attrs))

            for kind, body_data in pending.bodies.items():
                body_rows.append({
                    'event_id': event_id,
                    'kind': kind,
                    'event_time_iso': pending.values['event_time_iso'],
                    'data': body_data,
                })

            # The collected parent references are relative ids - they map the same way
            for parent_relative_id in pending.parents:
                link_rows.append({
                    'child_event_id': event_id,
                    'parent_event_id': out[parent_relative_id],
                    'link_type': pending.parent_link_type,
                })

        if attr_rows:
            _ = connection.execute(event_attr_table.insert(), attr_rows)

        if body_rows:
            _ = connection.execute(event_body_table.insert(), body_rows)

        if link_rows:
            _ = connection.execute(event_link_table.insert(), link_rows)

        self.written_count = len(self.pending_events)

        return out

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

def _delete_demo_rows(connection:'Connection') -> 'None':
    """ Deletes everything a previous seed run wrote, on the given connection -
    running the import twice leaves one clean data set, not two stacked ones.
    """

    # The demo events are found by their cid prefix ..
    demo_event_ids = select(event_table.c.id).where(event_table.c.cid.like(Cid_Prefix + '%'))

    # .. their dependent rows go first ..
    _ = connection.execute(delete(event_body_table).where(event_body_table.c.event_id.in_(demo_event_ids)))
    _ = connection.execute(delete(event_attr_table).where(event_attr_table.c.event_id.in_(demo_event_ids)))
    _ = connection.execute(delete(event_link_table).where(event_link_table.c.child_event_id.in_(demo_event_ids)))
    _ = connection.execute(delete(event_table).where(event_table.c.cid.like(Cid_Prefix + '%')))

    # .. the demo alerts are filed under demo rule names ..
    _ = connection.execute(delete(alert_table).where(alert_table.c.rule_name.like(Rule_Name_Prefix + '%')))

    # .. and the demo dedup entries share the event cid prefix.
    _ = connection.execute(delete(event_dedup_table).where(event_dedup_table.c.cid.like(Cid_Prefix + '%')))

# ################################################################################################################################

def purge_demo_data(engine:'Engine') -> 'None':
    """ Removes everything a previous seed run wrote, in one transaction.
    """
    with engine.begin() as connection:
        _delete_demo_rows(connection)

# ################################################################################################################################

def _draw_fraction(rng:'Random') -> 'timedelta':
    """ Draws the fraction of a second a moment falls on. Nothing is written down on a whole
    second - a message arrives when it arrives, and a check that comes round on the half hour
    still takes a moment to reach the point of writing its finding down.
    """
    out = timedelta(microseconds=rng.randrange(Microseconds_Per_Second))
    return out

# ################################################################################################################################

def _draw_time(rng:'Random', now:'datetime', days:'int') -> 'datetime':
    """ Draws one timestamp within the seeded span - a uniform day, an hour
    from the working-day curve, a uniform minute and second, and the fraction
    of a second the clock would have caught the message at.
    """
    day_offset = rng.randrange(days)
    hour = rng.choices(range(24), weights=Hourly_Weights)[0]
    minute = rng.randrange(60)
    second = rng.randrange(60)

    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=day_offset)
    out = day_start + timedelta(hours=hour, minutes=minute, seconds=second) + _draw_fraction(rng)

    return out

# ################################################################################################################################

def _to_hl7_timestamp(when:'datetime') -> 'str':
    """ Renders a moment as an HL7 TS with a four-digit fraction - a message body
    whose MSH-7 sits on a whole second reads as made up.
    """
    out = when.strftime('%Y%m%d%H%M%S.%f')[:19]
    return out

# ################################################################################################################################

def _build_ack_text(ack_code:'str', control_id:'str', when:'datetime') -> 'str':
    """ Builds the minimal acknowledgment message a channel would send back,
    its MSH-7 carrying the acknowledgment's own moment.
    """
    msh = 'MSH|^~\\&|ZATO|ZATO|DEMO|DEMO|{}||ACK|{}|P|2.4'.format(_to_hl7_timestamp(when), control_id)
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
            planned.when = burst_start + timedelta(seconds=rng.randrange(burst_seconds)) + _draw_fraction(rng)
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
    audit_log:'_BulkAuditLog',
    plan:'anylist',
    rng:'Random',
    ) -> 'anytuple':
    """ Writes the planned messages through the same producers the live wire uses -
    a received event and its acknowledgment per message, plus the forwarded pair
    on the outgoing connection where the plan says so. Returns the message count,
    the failed messages the resubmit chains reprocess and the receipts
    the content-viewed records draw from.
    """

    # The failed lab and main messages the resubmit chains reprocess
    resubmit_sources:'anylist' = []

    # The receipts somebody may have opened later - every failure and a sparse
    # sample of accepted ones, as (relative id, moment) pairs
    failed_candidates:'anylist' = []
    ok_candidates:'anylist' = []

    # Every this many accepted receipts, one goes into the view candidates
    ok_sample_step = 100

    for index, planned in enumerate(plan):

        cid = f'{Cid_Prefix}{index + 1:08d}'

        message = parse_hl7(planned.text, validate=False)
        attrs = get_audit_attrs(message)

        # The receipt itself
        audit_log.set_event_time(planned.when)
        received_id = audit_message_received(
            audit_log, planned.channel_name, planned.text,
            cid=cid, msg_id=planned.control_id, attrs=attrs, endpoint='mllp://demo')

        # Failed lab and main receipts feed the resubmit chains, up to the fixed count
        needs_chain = planned.channel_name in (Channel_Lab, Channel_Main) and planned.is_error

        if needs_chain and len(resubmit_sources) < Resubmit_Count:
            source = _ResubmitSource()
            source.relative_received_id = received_id
            source.cid = cid
            source.control_id = planned.control_id
            source.text = planned.text
            source.channel_name = planned.channel_name
            source.when = planned.when
            resubmit_sources.append(source)

        # Every failure may have been looked at, accepted ones only now and then
        if planned.is_error:
            failed_candidates.append((received_id, planned.when))
        elif index % ok_sample_step == 0:
            ok_candidates.append((received_id, planned.when))

        # The acknowledgment follows within the handling time
        if planned.is_error:
            ack_code = ACKStatus.Application_Error
            duration_ms = rng.randrange(40, 400)
        else:
            ack_code = ACKStatus.Application_Accept
            duration_ms = rng.randrange(5, 120)

        ack_when = planned.when + timedelta(milliseconds=duration_ms)
        ack_text = _build_ack_text(ack_code, planned.control_id, ack_when)

        audit_log.set_event_time(ack_when)
        _ = audit_ack_sent(
            audit_log, planned.channel_name, ack_code, ack_text,
            cid=cid, msg_id=planned.control_id, duration_ms=duration_ms)

        # The forwarded pair on the outgoing connection
        if planned.is_forwarded:

            sent_when = ack_when + timedelta(milliseconds=rng.randrange(50, 300))

            audit_log.set_event_time(sent_when)
            _ = audit_message_sent(
                audit_log, Outconn_Forward, planned.text,
                cid=cid, msg_id=planned.control_id, attrs=attrs, endpoint='mllp://demo-ehr')

            # A small share of forwards never hears back
            if rng.random() < Forward_Timeout_Ratio:
                forward_ack_code = ACKStatus.Timeout
                forward_duration_ms = 30_000
            else:
                forward_ack_code = ACKStatus.Application_Accept
                forward_duration_ms = rng.randrange(20, 250)

            forward_ack_when = sent_when + timedelta(milliseconds=forward_duration_ms)

            audit_log.set_event_time(forward_ack_when)
            _ = audit_ack_received(
                audit_log, Outconn_Forward, forward_ack_code,
                cid=cid, msg_id=planned.control_id, duration_ms=forward_duration_ms)

    return len(plan), resubmit_sources, failed_candidates, ok_candidates

# ################################################################################################################################

def _write_in_flight_sends(
    audit_log:'_BulkAuditLog',
    config:'SeedConfig',
    now:'datetime',
    rng:'Random',
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
        when = now - timedelta(minutes=rng.randrange(2, 30)) + _draw_fraction(rng)
        cid = f'{Cid_Prefix}if-{index + 1:08d}'

        audit_log.set_event_time(when)
        _ = audit_message_sent(
            audit_log, Outconn_Forward, text,
            cid=cid, msg_id=control_id, attrs=attrs, endpoint='mllp://demo-ehr')

# ################################################################################################################################

def _write_batch(
    audit_log:'_BulkAuditLog',
    config:'SeedConfig',
    now:'datetime',
    rng:'Random',
    ) -> 'None':
    """ Writes one FHS/BHS batch with its parent row and per-message children -
    the lineage view's demo case. The parent and all its children share
    one moment, set once on the collector's clock.
    """

    feed_config = FeedConfig()
    feed_config.seed = config.seed + 1

    items = generate_feed_items(3, feed_config)
    body = '\r'.join(item.text for item in items)

    batch_cid = f'{Cid_Prefix}batch-00000001'
    batch_when = now.replace(hour=11, minute=0, second=0, microsecond=0) - timedelta(days=2) + _draw_fraction(rng)

    # The batch header carries the batch's own moment
    batch_header = 'BHS|^~\\&|DEMO_BATCH|GENERAL_HOSPITAL|ZATO|ZATO|{}'.format(_to_hl7_timestamp(batch_when))
    batch_text = batch_header + '\r' + body + '\rBTS|3'

    audit_log.set_event_time(batch_when)
    _ = audit_batch_received(audit_log, Channel_Main, batch_text, cid=batch_cid, endpoint='mllp://demo')

# ################################################################################################################################

def _write_one_hop(
    audit_log:'_BulkAuditLog',
    source:'_ResubmitSource',
    *,
    cid:'str',
    when:'datetime',
    correl_id:'str',
    parent_relative_id:'int',
    actor:'str',
    ack_code:'str',
    duration_ms:'int',
    ) -> 'anytuple':
    """ Writes one hop of a resubmit chain, mirroring what the reprocess handler
    writes - the new receipt linked to its parent, then the acknowledgment.
    Returns the receipt's relative id and the acknowledgment's moment.
    """

    message = parse_hl7(source.text, validate=False)
    attrs = get_audit_attrs(message)

    # Who asked for the resubmit travels with the receipt
    attrs['actor'] = actor

    audit_log.set_event_time(when)
    received_id = audit_log.insert(
        AuditSource.HL7, AuditEvent.Message_Received, source.channel_name,
        cid=cid,
        msg_id=source.control_id,
        correl_id=correl_id,
        size=len(source.text),
        outcome=AuditOutcome.OK,
        data=dumps({'payload': source.text}),
        attrs=attrs,
        parents=[parent_relative_id],
    )

    ack_when = when + timedelta(milliseconds=duration_ms)
    ack_text = _build_ack_text(ack_code, source.control_id, ack_when)

    audit_log.set_event_time(ack_when)
    _ = audit_ack_sent(
        audit_log, source.channel_name, ack_code, ack_text,
        cid=cid, msg_id=source.control_id, duration_ms=duration_ms)

    return received_id, ack_when

# ################################################################################################################################

def _write_resubmit_chains(
    audit_log:'_BulkAuditLog',
    resubmit_sources:'anylist',
    now:'datetime',
    rng:'Random',
    ) -> 'None':
    """ Writes the resubmit chains - each failed message captured during the week's
    traffic reprocessed by a person, the new events linked to the original by the
    correlation id and a resubmit link. Every few chains the first reprocess fails
    too and a second one goes through - a two-hop DAG. Each chain's stamped moments
    are written back onto its source, which the dedup ledger rows are built from.
    """

    for index, source in enumerate(resubmit_sources):

        chain_number = index + 1

        # Who asked for this resubmit
        actor = rng.choice(Actors)

        # The reprocess follows the failure within hours, never reaching past now
        chain_when = source.when + timedelta(minutes=rng.randrange(30, 720)) + _draw_fraction(rng)

        if chain_when > now:
            chain_when = now - timedelta(minutes=rng.randrange(1, 30)) + _draw_fraction(rng)

        chain_cid = f'{Cid_Prefix}rp-{chain_number:08d}'

        # Every few chains the first reprocess fails as well
        has_second_hop = chain_number % Second_Hop_Every == 0

        if has_second_hop:
            first_ack_code = ACKStatus.Application_Error
        else:
            first_ack_code = ACKStatus.Application_Accept

        first_hop_id, first_ack_when = _write_one_hop(
            audit_log, source,
            cid=chain_cid,
            when=chain_when,
            correl_id=source.cid,
            parent_relative_id=source.relative_received_id,
            actor=actor,
            ack_code=first_ack_code,
            duration_ms=rng.randrange(5, 120),
        )

        completed_when = first_ack_when

        # The second hop hangs off the first and goes through
        if has_second_hop:

            second_when = first_ack_when + timedelta(minutes=rng.randrange(5, 60)) + _draw_fraction(rng)

            if second_when > now:
                second_when = now - timedelta(seconds=rng.randrange(30, 300)) + _draw_fraction(rng)

            _, completed_when = _write_one_hop(
                audit_log, source,
                cid=f'{Cid_Prefix}rp2-{chain_number:08d}',
                when=second_when,
                correl_id=chain_cid,
                parent_relative_id=first_hop_id,
                actor=actor,
                ack_code=ACKStatus.Application_Accept,
                duration_ms=rng.randrange(5, 120),
            )

        # The chain's own moments and actor, which its dedup ledger row reports
        source.chain_cid = chain_cid
        source.chain_created_iso = chain_when.isoformat()
        source.chain_completed_iso = completed_when.isoformat()
        source.chain_actor = actor

# ################################################################################################################################

def _build_dedup_rows(
    now:'datetime',
    resubmit_sources:'anylist',
    id_map:'intanydict',
    rng:'Random',
    ) -> 'dictlist':
    """ Composes the dedup ledger's demo rows - one reprocess claim per resubmit
    chain, one more completed resend and one still in doubt, the ledger screen's
    demo cases.
    """

    # Our response to produce
    out:'dictlist' = []

    # Every chain went through the dedup ledger too - one completed claim each,
    # keyed by the original event's real id, the same key the reprocess handler
    # would build for it, stamped with the chain's own moments
    for source in resubmit_sources:

        original_event_id = id_map[source.relative_received_id]

        out.append({
            'dedup_key': build_dedup_key('reprocess', original_event_id, source.text),
            'cid': source.chain_cid,
            'action': 'reprocess',
            'actor': source.chain_actor,
            'created_iso': source.chain_created_iso,
            'outcome': AuditOutcome.OK,
            'completed_iso': source.chain_completed_iso,
        })

    # A completed resend claim from earlier today
    resend_when = now - timedelta(minutes=rng.randrange(30, 240)) + _draw_fraction(rng)

    out.append({
        'dedup_key': build_dedup_key('resend', 2, 'demo-resend-payload'),
        'cid': f'{Cid_Prefix}dd-00000001',
        'action': 'resend',
        'actor': rng.choice(Actors),
        'created_iso': resend_when.isoformat(),
        'outcome': AuditOutcome.OK,
        'completed_iso': (resend_when + timedelta(milliseconds=rng.randrange(20, 250))).isoformat(),
    })

    # A claim that never completed - the in-doubt screen's demo case
    in_doubt_when = now - timedelta(minutes=rng.randrange(5, 30)) + _draw_fraction(rng)

    out.append({
        'dedup_key': build_dedup_key('resend', 3, 'demo-in-doubt-payload'),
        'cid': f'{Cid_Prefix}dd-00000002',
        'action': 'resend',
        'actor': rng.choice(Actors),
        'created_iso': in_doubt_when.isoformat(),
        'outcome': '',
        'completed_iso': '',
    })

    return out

# ################################################################################################################################

def _build_alert_row(
    rule:'AlertRule',
    finding:'Finding',
    *,
    count:'int',
    state:'str',
    first_raised:'datetime',
    last_raised:'datetime',
    observed_by:'str' = '',
    observed_iso:'str' = '',
    resolved_by:'str' = '',
    resolved_iso:'str' = '',
    ) -> 'anydict':
    """ Composes one alert row in its final lifecycle state - the same columns
    the alert store's raise, observe and resolve sequence would have produced.
    """
    out = {
        'rule_name': rule.name,
        'source': finding.source,
        'object_name': finding.object_name,
        'kind': finding.kind,
        'severity': finding.severity,
        'message': finding.message,
        'link': finding.link,
        'count': count,
        'state': state,
        'first_raised_iso': first_raised.isoformat(),
        'last_raised_iso': last_raised.isoformat(),
        'observed_by': observed_by,
        'observed_iso': observed_iso,
        'resolved_by': resolved_by,
        'resolved_iso': resolved_iso,
    }

    return out

# ################################################################################################################################

def _write_alerts(audit_log:'_BulkAuditLog', now:'datetime', rng:'Random') -> 'dictlist':
    """ Writes the alert history's audit events and composes the alert rows -
    one alert in each lifecycle state, so the alerts screen shows all three
    colors. Returns the alert rows for the bulk insert.
    """

    rules = {}

    for rule_def in get_demo_rule_defs():
        rules[rule_def['name']] = parse_rule(rule_def['name'], rule_def)

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Our response to produce
    out:'dictlist' = []

    # The unobserved alert - the clinic feed fell silent this morning
    # and the finding repeated every half hour since
    silent_rule = rules[Rule_Feed_Silent]
    silent_finding = new_finding(
        FindingKind.Feed_Silent, AuditSource.HL7, Channel_Clinic,
        f'Feed on {Channel_Clinic} has been silent since {Clinic_Silent_Hour:02d}:00 UTC',
        severity=AlertSeverity.Warning)

    silent_when = today_start + timedelta(hours=Clinic_Silent_Hour, minutes=30)

    # The moments the repeated findings were written down at, which is what the alert reports -
    # a check comes round on the half hour but writes its finding a moment after
    silent_stamps:'anylist' = []

    while silent_when < now:
        stamped = silent_when + _draw_fraction(rng)
        silent_stamps.append(stamped)
        silent_count = len(silent_stamps)

        audit_log.set_event_time(stamped)
        record_alert_event(
            audit_log, silent_rule, silent_finding, silent_count, f'{Cid_Prefix}al-silent-{silent_count:04d}')

        # The next round is counted off the half hour itself, so the fractions do not accumulate
        silent_when = silent_when + timedelta(minutes=30)

    # A run whose moment is before the silence window has no repetitions to fold
    if silent_stamps:
        out.append(_build_alert_row(
            silent_rule, silent_finding,
            count=len(silent_stamps), state=AlertState.Unobserved,
            first_raised=silent_stamps[0], last_raised=silent_stamps[-1]))

    # The observed alert - yesterday's error burst, acknowledged that evening
    error_rule = rules[Rule_Error_Rate]
    error_finding = new_finding(
        FindingKind.Error_Rate, AuditSource.HL7, Channel_Lab,
        f'Error rate on {Channel_Lab} exceeded 10 failures within 15 minutes',
        severity=AlertSeverity.Critical)

    burst_day = today_start - timedelta(days=1)
    error_offsets = (10, 40, 80)

    # The moments the findings were written down at, which the alert reports as its own
    error_stamps:'anylist' = []

    for minutes_offset in error_offsets:
        stamped = burst_day + timedelta(hours=Burst_Start_Hour, minutes=minutes_offset) + _draw_fraction(rng)
        error_stamps.append(stamped)

        audit_log.set_event_time(stamped)
        record_alert_event(
            audit_log, error_rule, error_finding, len(error_stamps), f'{Cid_Prefix}al-error-{minutes_offset:04d}')

    observed_when = burst_day + timedelta(hours=Burst_End_Hour, minutes=5) + _draw_fraction(rng)

    out.append(_build_alert_row(
        error_rule, error_finding,
        count=len(error_stamps), state=AlertState.Observed,
        first_raised=error_stamps[0], last_raised=error_stamps[-1],
        observed_by=Actor_Admin, observed_iso=observed_when.isoformat()))

    # The resolved alert - a delivery stall from three days ago, resolved the same day
    missing_rule = rules[Rule_Missing_Ack]
    missing_finding = new_finding(
        FindingKind.Missing_Followup, AuditSource.HL7, Outconn_Forward,
        f'Messages sent through {Outconn_Forward} received no acknowledgment within 5 minutes',
        severity=AlertSeverity.Warning)

    missing_when = today_start - timedelta(days=3) + timedelta(hours=9) + _draw_fraction(rng)

    audit_log.set_event_time(missing_when)
    record_alert_event(audit_log, missing_rule, missing_finding, 1, f'{Cid_Prefix}al-missing-0001')

    resolved_when = missing_when + timedelta(hours=2, minutes=30)

    out.append(_build_alert_row(
        missing_rule, missing_finding,
        count=1, state=AlertState.Resolved,
        first_raised=missing_when, last_raised=missing_when,
        resolved_by=Actor_Operator, resolved_iso=resolved_when.isoformat()))

    return out

# ################################################################################################################################

def _write_config_history(audit_log:'_BulkAuditLog', now:'datetime', rng:'Random') -> 'int':
    """ Writes the config-change history - the demo objects created a week ago
    and one edit later on. The view-access record follows separately, once
    the real id of the viewed event is known. Returns the event count.
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

        audit_log.set_event_time(created_when + timedelta(minutes=index) + _draw_fraction(rng))
        _ = record_config_change(
            audit_log,
            action=AuditEvent.Config_Created,
            object_type='generic-connection',
            object_name=object_name,
            actor=Actor_Admin,
            cid=f'{Cid_Prefix}cfg-{index + 1:04d}',
            after=after,
        )
        count += 1

    # The lab channel's pool grew two days ago
    edited_when = today_start - timedelta(days=2) + timedelta(hours=15) + _draw_fraction(rng)

    audit_log.set_event_time(edited_when)
    _ = record_config_change(
        audit_log,
        action=AuditEvent.Config_Edited,
        object_type='generic-connection',
        object_name=Channel_Lab,
        actor=Actor_Operator,
        cid=f'{Cid_Prefix}cfg-0006',
        before={'name': Channel_Lab, 'pool_size': 1},
        after={'name': Channel_Lab, 'pool_size': 2},
    )
    count += 1

    return count

# ################################################################################################################################

def _draw_view_time(rng:'Random', message_when:'datetime', now:'datetime') -> 'datetime':
    """ Draws the moment somebody opened a message's body - within hours of the
    message's own moment, never reaching past now.
    """
    out = message_when + timedelta(minutes=rng.randrange(10, 600)) + _draw_fraction(rng)

    if out > now:
        out = now - timedelta(minutes=rng.randrange(1, 15)) + _draw_fraction(rng)

    return out

# ################################################################################################################################

def _plan_views(
    resubmit_sources:'anylist',
    failed_candidates:'anylist',
    ok_candidates:'anylist',
    now:'datetime',
    rng:'Random',
    ) -> 'anylist':
    """ Plans the content-viewed records - every resubmitted message was looked at
    before it was reprocessed, then other failures and a few accepted ones fill
    the list up to the fixed count.
    """

    # Our response to produce
    out:'anylist' = []

    # A resubmitted message's body was on somebody's screen first
    resubmitted_ids = set()

    for source in resubmit_sources:

        resubmitted_ids.add(source.relative_received_id)

        view = _PlannedView()
        view.relative_event_id = source.relative_received_id
        view.actor = rng.choice(Actors)
        view.when = _draw_view_time(rng, source.when, now)
        out.append(view)

    # Other failures and a few accepted ones fill the rest, failures first
    remaining = [item for item in failed_candidates if item[0] not in resubmitted_ids]
    remaining.extend(ok_candidates)

    for relative_event_id, message_when in remaining:

        if len(out) >= View_Count:
            break

        view = _PlannedView()
        view.relative_event_id = relative_event_id
        view.actor = rng.choice(Actors)
        view.when = _draw_view_time(rng, message_when, now)
        out.append(view)

    return out

# ################################################################################################################################

def _write_view_events(audit_log:'_BulkAuditLog', planned_views:'anylist', id_map:'intanydict') -> 'int':
    """ Writes the view-access records - who opened which message's body and when.
    This runs after the main commit because each record embeds the viewed event's
    real database id. Returns how many were written.
    """

    for index, view in enumerate(planned_views):

        audit_log.set_event_time(view.when)
        _ = record_view_event(
            audit_log,
            actor=view.actor,
            viewed_event_id=id_map[view.relative_event_id],
            screen=Screen_Browser,
            cid=f'{Cid_Prefix}view-{index + 1:04d}',
        )

    return len(planned_views)

# ################################################################################################################################

def _write_fhir_traffic(
    audit_log:'_BulkAuditLog',
    config:'SeedConfig',
    now:'datetime',
    rng:'Random',
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

        audit_log.set_event_time(when)
        _ = audit_log.insert(
            AuditSource.FHIR, AuditEvent.Request_Sent, Outconn_FHIR,
            cid=cid,
            endpoint=f'GET {path}',
            outcome=AuditOutcome.OK,
            data=stored_data,
            attrs=attrs,
        )

        duration_ms = rng.randrange(15, 350)
        response_when = when + timedelta(milliseconds=duration_ms)

        audit_log.set_event_time(response_when)
        _ = audit_log.insert(
            AuditSource.FHIR, AuditEvent.Response_Received, Outconn_FHIR,
            cid=cid,
            outcome=AuditOutcome.OK,
            duration_ms=duration_ms,
            attrs=attrs,
        )

    return config.fhir_pair_count

# ################################################################################################################################

def seed_demo_data(
    engine:'Engine',
    *,
    server_name:'str',
    now:'datetime | None' = None,
    config:'SeedConfig | None' = None,
    ) -> 'SeedResult':
    """ Runs one full seed - the week of traffic, the batch, the resubmit chain,
    the dedup entries, the alerts, the config history and the FHIR side are all
    collected in memory with their final timestamps first, then a previous run's
    data is purged and everything lands in the database in one bulk transaction.
    The same seed always produces the same data set.
    """

    if now is None:
        now = utcnow()

    if config is None:
        config = SeedConfig()

    rng = Random(config.seed)

    # Everything is collected here first and written in bulk at the end
    audit_log = _BulkAuditLog(server_name)

    # Our response to produce
    out = SeedResult()
    out.channel_names = [Channel_Main, Channel_Lab, Channel_Clinic]
    out.rule_names = [rule_def['name'] for rule_def in get_demo_rule_defs()]

    # The week of wire traffic, which also yields the resubmit chains' sources
    # and the receipts the content-viewed records draw from
    plan = _build_plan(config, now)
    out.message_count, resubmit_sources, failed_candidates, ok_candidates = _write_messages(audit_log, plan, rng)

    # The open exchanges the outstanding filter surfaces
    _write_in_flight_sends(audit_log, config, now, rng)

    # The batch with its lineage
    _write_batch(audit_log, config, now, rng)

    # The resubmit chains - the failed messages reprocessed by a person
    _write_resubmit_chains(audit_log, resubmit_sources, now, rng)
    out.resubmit_count = len(resubmit_sources)

    # The three alert lifecycles - their audit events plus the composed alert rows
    alert_rows = _write_alerts(audit_log, now, rng)
    out.alert_count = len(alert_rows)

    # The config-change history, without the view record yet
    out.config_event_count = _write_config_history(audit_log, now, rng)

    # The FHIR request/response pairs
    out.fhir_pair_count = _write_fhir_traffic(audit_log, config, now, rng)

    # The content-viewed records are planned now and written after the main
    # commit, once the real database ids of the viewed events exist
    planned_views = _plan_views(resubmit_sources, failed_candidates, ok_candidates, now, rng)

    # Everything lands in the database at once - a rerun replaces the previous
    # data set inside the same transaction, so a failed import changes nothing
    with engine.begin() as connection:

        _delete_demo_rows(connection)

        id_map = audit_log.write_collected(connection)

        dedup_rows = _build_dedup_rows(now, resubmit_sources, id_map, rng)
        _ = connection.execute(event_dedup_table.insert(), dedup_rows)
        out.dedup_count = len(dedup_rows)

        if alert_rows:
            _ = connection.execute(alert_table.insert(), alert_rows)

    # Each view-access record embeds the viewed event's real database id,
    # which exists only after the main commit - they follow in a write of their own
    if planned_views:

        out.view_count = _write_view_events(audit_log, planned_views, id_map)

        with engine.begin() as connection:
            _ = audit_log.write_collected(connection)

        out.config_event_count += out.view_count

    # The final count is what the database actually holds
    statement = select(func.count()).select_from(event_table).where(event_table.c.cid.like(Cid_Prefix + '%'))

    with engine.connect() as connection:
        out.event_count = connection.execute(statement).scalar()

    return out

# ################################################################################################################################
# ################################################################################################################################
