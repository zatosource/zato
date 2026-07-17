# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic, sleep

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_attr_table, event_link_table, event_table, get_audit_engine, \
    AuditBody, AuditClassification, AuditEvent, AuditLink, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.body import register_body_resolver, resolve_body

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, intlist, strnone

    # Dummy assignments to satisfy type checkers
    anydict = anydict
    anylist = anylist
    intlist = intlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-server'

# The channels the token-usage events belong to
_usage_channel_name = 'audit.test.usage-channel'
_other_usage_channel_name = 'audit.test.other-usage-channel'

# A source whose bodies live outside the audit database
_external_body_source = 'audit-test-external-body'

# How long the time-based flush may take before the scenario gives up
_flush_wait_seconds = 5.0

# ################################################################################################################################
# ################################################################################################################################

def _get_event_row(event_id:'int') -> 'anydict':
    """ Returns one event row as a dict.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.id == event_id)

    with engine.connect() as connection:
        result = connection.execute(query)
        row = result.first()

    out = dict(row._mapping)
    return out

# ################################################################################################################################

def _get_attr_map(event_id:'int') -> 'anydict':
    """ Returns the attributes of one event as a dict of name to (value, value_number).
    """
    engine = get_audit_engine()

    query = select(event_attr_table)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            mapping = row._mapping
            out[mapping['name']] = (mapping['value'], mapping['value_number'])

    return out

# ################################################################################################################################

def _count_source_events(source:'str') -> 'int':
    """ Counts the events of one source.
    """
    engine = get_audit_engine()

    query = select(func.count())
    query = query.select_from(event_table)
    query = query.where(event_table.c.source == source)

    with engine.connect() as connection:
        result = connection.execute(query)
        out = result.scalar()

    return out

# ################################################################################################################################

def _run_attrs_checks(audit_log:'AuditLog') -> 'intlist':
    """ Writes events with string and numeric attributes and confirms how they are stored -
    numbers land in both columns, identifiers with leading zeros stay text only
    and overlong values are capped. Returns the ids of the usage events written.
    """

    # Token-usage events - two channels so aggregation has something to group by ..
    first_id = audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, _usage_channel_name,
        cid='cid-usage-1', outcome=AuditOutcome.OK,
        attrs={'token_count': 100, 'latency': 12.5, 'mrn': '000123'})

    second_id = audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, _usage_channel_name,
        cid='cid-usage-2', outcome=AuditOutcome.OK,
        attrs={'token_count': 250})

    third_id = audit_log.insert(AuditSource.MCP, AuditEvent.MCP_Tools_Call, _other_usage_channel_name,
        cid='cid-usage-3', outcome=AuditOutcome.OK,
        attrs={'token_count': 40, 'note': 'A' * 300})

    # .. synchronous writes return the id of the new event ..
    assert isinstance(first_id, int)
    assert isinstance(second_id, int)
    assert isinstance(third_id, int)

    # .. numbers are stored in both columns ..
    attr_map = _get_attr_map(first_id)

    assert attr_map['token_count'][0] == '100'
    assert float(attr_map['token_count'][1]) == 100.0
    assert float(attr_map['latency'][1]) == 12.5

    # .. an identifier with leading zeros stays text only ..
    assert attr_map['mrn'] == ('000123', None)

    # .. and overlong values are capped at the column length.
    attr_map = _get_attr_map(third_id)
    assert attr_map['note'][0] == 'A' * 255

    out = [first_id, second_id, third_id]
    return out

# ################################################################################################################################

def _run_aggregation_checks() -> 'None':
    """ Runs the usage-report query shape - a sum over the numeric attribute column
    grouped by the object the events belong to.
    """
    engine = get_audit_engine()

    query = select(event_table.c.object_name, func.sum(event_attr_table.c.value_number))
    query = query.select_from(event_table.join(event_attr_table, event_attr_table.c.event_id == event_table.c.id))
    query = query.where(event_attr_table.c.name == 'token_count')
    query = query.group_by(event_table.c.object_name)

    totals:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):

            # Each backend returns its own numeric type for a sum, hence the conversion
            totals[row[0]] = float(row[1])

    assert totals == {_usage_channel_name: 350.0, _other_usage_channel_name: 40.0}, totals

# ################################################################################################################################

def _run_attr_search_checks(expected_event_id:'int') -> 'None':
    """ Finds events through an indexed attribute - the string value matches exactly,
    leading zeros included.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.event_id)
    query = query.where(event_attr_table.c.name == 'mrn')
    query = query.where(event_attr_table.c.value == '000123')

    matches:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            matches.append(row[0])

    assert matches == [expected_event_id], matches

# ################################################################################################################################

def _run_cid_sequence_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms events sharing a cid receive consecutive sequence numbers
    while other cids count independently.
    """
    first_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'audit.test.sequence',
        cid='cid-sequence-a')
    second_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Sent, 'audit.test.sequence',
        cid='cid-sequence-a')
    third_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, 'audit.test.sequence',
        cid='cid-sequence-a')
    other_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'audit.test.sequence',
        cid='cid-sequence-b')

    assert _get_event_row(first_id)['cid_sequence'] == 1
    assert _get_event_row(second_id)['cid_sequence'] == 2
    assert _get_event_row(third_id)['cid_sequence'] == 3
    assert _get_event_row(other_id)['cid_sequence'] == 1

# ################################################################################################################################

def _run_classification_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms the two outcome layers are stored and failures are classified -
    derived from the outcome texts unless the caller already knows better.
    """

    # A timeout is transient - resubmitting as-is can work ..
    timeout_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.classify',
        cid='cid-classify-1', outcome=AuditOutcome.Error, status='Connection timeout after 30 seconds')

    row = _get_event_row(timeout_id)
    assert row['classification'] == AuditClassification.Transient

    # .. a validation failure is permanent - the message needs to change first ..
    validation_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.classify',
        cid='cid-classify-2', outcome=AuditOutcome.Error, application_outcome='Schema validation failed')

    row = _get_event_row(validation_id)
    assert row['classification'] == AuditClassification.Permanent
    assert row['application_outcome'] == 'Schema validation failed'

    # .. an explicit classification given by the caller always wins ..
    explicit_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.classify',
        cid='cid-classify-3', outcome=AuditOutcome.Error, status='Connection timeout after 30 seconds',
        classification=AuditClassification.Operator_Fixable)

    row = _get_event_row(explicit_id)
    assert row['classification'] == AuditClassification.Operator_Fixable

    # .. and successful events are never classified.
    ok_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, 'audit.test.classify',
        cid='cid-classify-4', outcome=AuditOutcome.OK, status='Connection timeout after 30 seconds')

    row = _get_event_row(ok_id)
    assert row['classification'] == ''

# ################################################################################################################################

def _external_body_resolver(event_id:'int', kind:'str') -> 'strnone':
    """ The resolver of a source whose bodies live outside the audit database.
    """
    out = f'external-body-{event_id}-{kind}'
    return out

# ################################################################################################################################

def _run_body_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms bodies are stored by reference and resolved per kind,
    and that a source with its own body store answers through its resolver.
    """
    engine = get_audit_engine()

    event_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'audit.test.bodies',
        cid='cid-bodies-1', outcome=AuditOutcome.Error,
        bodies={
            AuditBody.Request: '<the full request body>',
            AuditBody.Response: '<the full response body>',
            AuditBody.Error: '<what the other side said when it failed>',
        })

    # Each kind resolves to its own content ..
    body = resolve_body(engine, AuditSource.REST_Channel, event_id, AuditBody.Request)
    assert body == '<the full request body>'

    body = resolve_body(engine, AuditSource.REST_Channel, event_id, AuditBody.Error)
    assert body == '<what the other side said when it failed>'

    # .. no kind means the newest body of any kind ..
    body = resolve_body(engine, AuditSource.REST_Channel, event_id)
    assert body == '<what the other side said when it failed>'

    # .. an event with no bodies resolves to nothing ..
    empty_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, 'audit.test.bodies',
        cid='cid-bodies-2')

    body = resolve_body(engine, AuditSource.REST_Channel, empty_id)
    assert body is None

    # .. and a source with its own body store answers through its registered resolver.
    register_body_resolver(_external_body_source, _external_body_resolver)

    body = resolve_body(engine, _external_body_source, event_id, AuditBody.Request)
    assert body == f'external-body-{event_id}-request'

# ################################################################################################################################

def _get_link_rows(child_event_id:'int') -> 'anylist':
    """ Returns the lineage links of one child event as (parent_event_id, link_type) tuples.
    """
    engine = get_audit_engine()

    query = select(event_link_table.c.parent_event_id, event_link_table.c.link_type)
    query = query.where(event_link_table.c.child_event_id == child_event_id)
    query = query.order_by(event_link_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(tuple(row))

    return out

# ################################################################################################################################

def _run_lineage_checks(audit_log:'AuditLog') -> 'None':
    """ Confirms lineage links - multiple parents at insert time and links added
    after the fact, as when a resubmission points back to its original.
    """
    first_parent_id = audit_log.insert(AuditSource.X12, AuditEvent.Message_Received, 'audit.test.lineage',
        cid='cid-lineage-parent-1')
    second_parent_id = audit_log.insert(AuditSource.X12, AuditEvent.Message_Received, 'audit.test.lineage',
        cid='cid-lineage-parent-2')

    # One message aggregated out of two parents ..
    child_id = audit_log.insert(AuditSource.X12, AuditEvent.Message_Sent, 'audit.test.lineage',
        cid='cid-lineage-child', parents=[first_parent_id, second_parent_id],
        parent_link_type=AuditLink.Aggregated_From)

    links = _get_link_rows(child_id)
    assert links == [
        (first_parent_id, AuditLink.Aggregated_From),
        (second_parent_id, AuditLink.Aggregated_From),
    ], links

    # .. and a resubmission linked to its original after both were written.
    resubmit_id = audit_log.insert(AuditSource.X12, AuditEvent.Message_Sent, 'audit.test.lineage',
        cid='cid-lineage-resubmit')
    audit_log.add_links(resubmit_id, [child_id], AuditLink.Resubmit_Of)

    links = _get_link_rows(resubmit_id)
    assert links == [(child_id, AuditLink.Resubmit_Of)], links

# ################################################################################################################################

def _run_buffered_writer_checks() -> 'None':
    """ Confirms the buffered writer flushes when the batch is full, on an explicit flush
    and, at the latest, when the oldest event has waited long enough.
    """
    buffered = AuditLog(_server_name, flush_max_size=3, flush_max_wait_ms=300)

    # Buffered writes return no id and nothing is visible yet ..
    result = buffered.insert(AuditSource.AS2, AuditEvent.Message_Sent, 'audit.test.buffered', cid='cid-buffered')
    assert result is None
    assert _count_source_events(AuditSource.AS2) == 0

    # .. the third event fills the batch up and everything lands at once ..
    _ = buffered.insert(AuditSource.AS2, AuditEvent.Message_Sent, 'audit.test.buffered', cid='cid-buffered')
    _ = buffered.insert(AuditSource.AS2, AuditEvent.Message_Sent, 'audit.test.buffered', cid='cid-buffered')
    assert _count_source_events(AuditSource.AS2) == 3

    # .. an explicit flush writes out a partial batch ..
    _ = buffered.insert(AuditSource.AS2, AuditEvent.Message_Sent, 'audit.test.buffered', cid='cid-buffered')
    assert _count_source_events(AuditSource.AS2) == 3

    buffered.flush()
    assert _count_source_events(AuditSource.AS2) == 4

    # .. and an event left in the buffer is flushed by time, without any further writes.
    _ = buffered.insert(AuditSource.AS2, AuditEvent.Message_Sent, 'audit.test.buffered', cid='cid-buffered')

    deadline = monotonic() + _flush_wait_seconds

    while monotonic() < deadline:

        if _count_source_events(AuditSource.AS2) == 5:
            break

        sleep(0.1)

    assert _count_source_events(AuditSource.AS2) == 5, 'The time-based flush never ran'

# ################################################################################################################################
# ################################################################################################################################

def run_structured_events_scenario() -> 'None':
    """ The structured-events scenario every backend must pass: searchable attributes
    with numeric aggregation, per-cid sequence numbers, two-layer outcomes with failure
    classification, bodies by reference with pluggable resolvers, multi-parent lineage
    and the buffered writer.
    """
    delete_all_events()

    audit_log = AuditLog(_server_name)

    usage_ids = _run_attrs_checks(audit_log)

    _run_aggregation_checks()
    _run_attr_search_checks(usage_ids[0])
    _run_cid_sequence_checks(audit_log)
    _run_classification_checks(audit_log)
    _run_body_checks(audit_log)
    _run_lineage_checks(audit_log)
    _run_buffered_writer_checks()

# ################################################################################################################################
# ################################################################################################################################
