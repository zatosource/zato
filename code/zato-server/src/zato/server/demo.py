# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The server side of the demo-data import - plain functions the server calls,
# no service of their own. The data itself comes from zato.common.demo.seed,
# this module adds what needs a live server - the demo connections, the alert
# rules stored as generic objects and a burst of live MLLP traffic that fills
# the in-process channel counters.

# stdlib
from contextlib import closing
from logging import getLogger
from time import sleep

# Zato
from zato.common.api import Audit_Config, HL7
from zato.common.audit_log.api import get_audit_engine, AuditLog
from zato.common.defaults import default_cluster_id
from zato.common.demo.seed import get_demo_rule_defs, purge_demo_data, seed_demo_data, Channel_Clinic, Channel_Lab, \
    Channel_Main, Outconn_FHIR, Outconn_Forward, Route_Clinic, Route_Lab, Route_Main, SeedConfig
from zato.common.hl7.feed import generate_feed_items, rewrite_msh_field, FeedConfig, MSH3_Index
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn
from zato.common.odb.query.generic import GenericObjectWrapper
from zato.common.util.api import hex_sequence_to_bytes
from zato.server.generic.api.channel_hl7_mllp import get_internal_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The generic-connection types the demo objects are created as
_type_channel_mllp = 'channel-hl7-mllp'
_type_outconn_mllp = 'outconn-hl7-mllp'
_type_outconn_fhir = 'outconn-hl7-fhir'

# The service behind the demo channels - it exists on every server
_channel_service = 'helpers.echo'

# The addresses the demo outgoing connections point at - reserved names
# that never resolve, the demo only needs the objects to exist
_forward_address = 'demo-ehr.invalid:2575'
_fhir_address = 'https://demo-ehr.invalid/fhir'

# How many live messages the burst sends through the main demo channel
_burst_count = 20

# The seed the burst messages are generated from
_burst_seed = 20260102

# The channel wrappers start asynchronously after their connections are created -
# this is how long the listener is given to come up, in half-second steps
_listener_wait_steps = 20
_listener_wait_step_seconds = 0.5

# ################################################################################################################################
# ################################################################################################################################

# What each demo connection is created with, beyond the shared boilerplate
_connection_defs = (
    {
        'name': Channel_Main,
        'type_': _type_channel_mllp,
        'is_channel': True,
        'is_outconn': False,
        'service': _channel_service,
        'msh3_sending_app': Route_Main,
    },
    {
        'name': Channel_Lab,
        'type_': _type_channel_mllp,
        'is_channel': True,
        'is_outconn': False,
        'service': _channel_service,
        'msh3_sending_app': Route_Lab,
    },
    {
        'name': Channel_Clinic,
        'type_': _type_channel_mllp,
        'is_channel': True,
        'is_outconn': False,
        'service': _channel_service,
        'msh3_sending_app': Route_Clinic,
    },
    {
        'name': Outconn_Forward,
        'type_': _type_outconn_mllp,
        'is_channel': False,
        'is_outconn': True,
        'address': _forward_address,
    },
    {
        'name': Outconn_FHIR,
        'type_': _type_outconn_fhir,
        'is_channel': False,
        'is_outconn': True,
        'address': _fhir_address,
    },
)

# ################################################################################################################################
# ################################################################################################################################

def ensure_demo_connections(server:'ParallelServer') -> 'strlist':
    """ Creates the demo channels and outgoing connections unless they exist -
    running the import twice changes nothing here. Returns the names created.
    """

    # What already exists is read straight from the database
    demo_names = [connection_def['name'] for connection_def in _connection_defs]

    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.name).filter(GenericConn.name.in_(demo_names)).all()

    existing = {row[0] for row in rows}

    # Our response to produce
    out:'strlist' = []

    for connection_def in _connection_defs:

        if connection_def['name'] in existing:
            continue

        request = {
            'cluster_id': default_cluster_id,
            'is_active': True,
            'is_internal': False,
            'pool_size': 1,
            'is_audit_log_active': True,
        }
        request.update(connection_def)

        _ = server.invoke('zato.generic.connection.create', request)
        out.append(connection_def['name'])

    return out

# ################################################################################################################################

def store_demo_rules(server:'ParallelServer') -> 'strlist':
    """ Writes the demo alert rules as generic objects - the same rows the enmasse
    importer would create, so the sweep and the rules screen see them. Returns
    the rule names.
    """

    # Our response to produce
    out:'strlist' = []

    with closing(server.odb.session()) as session:

        wrapper = GenericObjectWrapper(session, server.cluster_id)
        wrapper.type_ = Audit_Config.Type.Alert_Rule

        for rule_def in get_demo_rule_defs():

            rule_def = dict(rule_def)
            name = rule_def.pop('name')
            opaque = dumps(rule_def)

            existing = wrapper.get(name)

            if existing:
                statement = wrapper.update(name, opaque, id=existing['id'])
            else:
                statement = wrapper.create(name, opaque)

            _ = session.execute(statement)
            out.append(name)

        session.commit()

    return out

# ################################################################################################################################

def send_demo_burst() -> 'int':
    """ Sends a short burst of live messages through the main demo channel
    so the in-process counters and the last-message times show current life,
    not just the seeded history. Returns how many messages went out.
    """

    # The channel wrappers start asynchronously after their connections
    # are created - the listener is given a moment to come up.
    port = get_internal_port()
    steps_left = _listener_wait_steps

    while not port and steps_left:
        sleep(_listener_wait_step_seconds)
        port = get_internal_port()
        steps_left -= 1

    # With no listener there is nothing to send through - the seeded history
    # is still complete, only the live counters stay at zero.
    if not port:
        logger.info('No MLLP listener came up, skipping the live demo burst')
        return 0

    start_sequence = hex_sequence_to_bytes(HL7.Default.start_seq)
    end_sequence = hex_sequence_to_bytes(HL7.Default.end_seq)

    client = HL7MLLPClient('127.0.0.1', port, start_sequence, end_sequence)

    feed_config = FeedConfig()
    feed_config.seed = _burst_seed

    items = generate_feed_items(_burst_count, feed_config)

    for item in items:

        # Every burst message routes to the main demo channel
        text = rewrite_msh_field(item.text, MSH3_Index, Route_Main)

        _ = client.send(text.encode('utf-8'), item.control_id)

    return len(items)

# ################################################################################################################################

def import_demo_data(server:'ParallelServer', *, config:'SeedConfig | None'=None) -> 'stranydict':
    """ Runs the whole demo import on a live server - the connections, the alert
    rules, the seeded week of history and the live burst. Rerunning replaces
    the previous demo data instead of stacking on it.
    """
    if config is None:
        config = SeedConfig()

    created_names = ensure_demo_connections(server)
    rule_names = store_demo_rules(server)

    # The seeded history goes into the same audit database the server writes to
    audit_log = AuditLog(server.name, flush_max_size=1)
    engine = get_audit_engine()

    result = seed_demo_data(audit_log, engine, config=config)

    # The live burst fills the in-process counters
    burst_count = send_demo_burst()

    # Our response to produce
    out = {
        'created_connections': created_names,
        'rule_names': rule_names,
        'message_count': result.message_count,
        'event_count': result.event_count,
        'alert_count': result.alert_count,
        'fhir_pair_count': result.fhir_pair_count,
        'config_event_count': result.config_event_count,
        'dedup_count': result.dedup_count,
        'channel_names': result.channel_names,
        'burst_count': burst_count,
    }

    return out

# ################################################################################################################################

def remove_demo_data(server:'ParallelServer') -> 'stranydict':
    """ Undoes the demo import - the connections, the alert rules and every
    demo row in the audit database. Returns the names of what was deleted.
    """
    demo_names = [connection_def['name'] for connection_def in _connection_defs]

    # The connections go first, so nothing writes new demo events meanwhile
    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.id, GenericConn.name).filter(GenericConn.name.in_(demo_names)).all()

    deleted_connections:'strlist' = []

    for connection_id, connection_name in rows:
        _ = server.invoke('zato.generic.connection.delete', {'id': connection_id, 'cluster_id': default_cluster_id})
        deleted_connections.append(connection_name)

    # The alert rules follow
    deleted_rules:'strlist' = []

    with closing(server.odb.session()) as session:

        wrapper = GenericObjectWrapper(session, server.cluster_id)
        wrapper.type_ = Audit_Config.Type.Alert_Rule

        for rule_def in get_demo_rule_defs():

            name = rule_def['name']

            if wrapper.get(name):
                statement = wrapper.delete_by_name(name)
                _ = session.execute(statement)
                deleted_rules.append(name)

        session.commit()

    # The audit rows go last
    engine = get_audit_engine()
    purge_demo_data(engine)

    # Our response to produce
    out = {
        'deleted_connections': deleted_connections,
        'deleted_rules': deleted_rules,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
