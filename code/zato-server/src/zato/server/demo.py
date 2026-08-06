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
import os
from contextlib import closing
from logging import getLogger
from time import sleep

# Zato
from zato.common.api import Audit_Config, HL7
from zato.common.audit_log.api import get_audit_engine
from zato.common.defaults import default_cluster_id
from zato.common.demo.seed import get_demo_rule_defs, purge_demo_data, seed_demo_data, Channel_Clinic, Channel_Lab, \
    Channel_Main, Outconn_FHIR, Outconn_Forward, Route_Clinic, Route_Lab, Route_Main, SeedConfig
from zato.common.hl7.feed import generate_feed_items, rewrite_msh_field, FeedConfig, MSH3_Index
from zato.common.hl7.fhir.fields import Outconn_Config_Defaults as FHIR_Outconn_Defaults
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.fields import Channel_Defaults as MLLP_Channel_Defaults, \
    Outconn_Defaults as MLLP_Outconn_Defaults
from zato.common.json_internal import dumps
from zato.common.odb.model import GenericConn
from zato.common.odb.query.generic import GenericObjectWrapper
from zato.common.util.api import hex_sequence_to_bytes
from zato.common.util.open_ import open_w
from zato.server.generic.api.channel_hl7_mllp import get_internal_port, is_channel_routed

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

# Every field each type carries, so a demo object holds what one made in the Dashboard holds
# rather than only the few fields named below - a reader of any other field finds it there
_type_defaults = {
    _type_channel_mllp: MLLP_Channel_Defaults,
    _type_outconn_mllp: MLLP_Outconn_Defaults,
    _type_outconn_fhir: FHIR_Outconn_Defaults,
}

# The service behind the demo channels - nothing on a fresh server answers an HL7 message
# with an acknowledgment of its own, so the import deploys one, its source below
_channel_service = 'demo.hl7.ack'

# What the demo service is deployed as
_channel_service_file_name = 'demo_hl7_ack.py'

# The addresses the demo outgoing connections point at - reserved names
# that never resolve, the demo only needs the objects to exist
_forward_address = 'demo-ehr.invalid:2575'
_fhir_address = 'https://demo-ehr.invalid/fhir'

# How many live messages the burst sends through the main demo channel
_burst_count = 20

# The seed the burst messages are generated from
_burst_seed = 20260102

# Hot deploy and the channel wrappers both run on their own, so the import waits for what
# it needs rather than assuming it is there - this is how long it waits, in half-second steps
_wait_steps = 20
_wait_step_seconds = 0.5

# ################################################################################################################################
# ################################################################################################################################

# The demo service's own source, deployed as it is - a sender that gets its own message back
# has not been acknowledged, so the demo answers with what the protocol calls for
_channel_service_source = '''\
# -*- coding: utf-8 -*-

# Zato
from zato.common.hl7.audit import ACKStatus
from zato.common.hl7.mllp.ack import build_ack
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _get_message_text(request:'any_') -> 'str':
    """ Returns the ER7 text of what a channel handed over - a REST channel delivers bytes,
    an MLLP channel that parses on input delivers a parsed message, and one that does not
    delivers the text itself.
    """
    if isinstance(request, bytes):
        return request.decode('utf-8')

    if isinstance(request, str):
        return request

    out = request.to_er7()
    return out

# ################################################################################################################################
# ################################################################################################################################

class DemoHL7Ack(Service):
    """ Answers every message with an HL7 acknowledgment - the sender and receiver of the
    message swapped, a control id of this side's own and the sender's echoed back in MSA-2.
    """
    name = '{service_name}'

    def handle(self):

        message_text = _get_message_text(self.request.raw_request)

        # An acknowledgment is built from the MSH line alone, and a sender may end its
        # lines with a carriage return, a newline or both
        msh_line = message_text.splitlines()[0]

        self.response.payload = build_ack(msh_line, ACKStatus.Application_Accept)

# ################################################################################################################################
# ################################################################################################################################
'''.format(service_name=_channel_service)

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

def ensure_demo_service(server:'ParallelServer') -> 'bool':
    """ Deploys the service the demo channels answer with, unless it is already there, and waits
    for it to come up. Returns whether the channels can be pointed at it.
    """

    # Already deployed, so there is nothing to write and nothing to wait for
    if server.service_store.is_deployed(_channel_service):
        return True

    file_path = os.path.join(server.hot_deploy_config.pickup_dir, _channel_service_file_name)

    with open_w(file_path) as f:
        _ = f.write(_channel_service_source)

    # Hot deploy picks the file up on its own, so the service is not there the moment
    # its source is - the channels and the burst that follow both need it to be
    steps_left = _wait_steps

    while steps_left:

        if server.service_store.is_deployed(_channel_service):
            logger.info('Deployed the demo service `%s` from %s', _channel_service, file_path)
            return True

        sleep(_wait_step_seconds)
        steps_left -= 1

    logger.warning('The demo service `%s` did not deploy from %s', _channel_service, file_path)
    return False

# ################################################################################################################################

def ensure_demo_connections(server:'ParallelServer') -> 'strlist':
    """ Creates the demo channels and outgoing connections, replacing any left by an earlier
    import so that each run lays down the current definition. Returns the names created.
    """

    # What already exists is read straight from the database
    demo_names = [connection_def['name'] for connection_def in _connection_defs]

    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.id, GenericConn.name).filter(GenericConn.name.in_(demo_names)).all()

    # A connection from an earlier import would keep whatever it was created with, a channel
    # its service among it, so what is already there goes before anything new is created
    for connection_id, connection_name in rows:
        _ = server.invoke('zato.generic.connection.delete', {'id': connection_id, 'cluster_id': default_cluster_id})
        logger.info('Deleted the demo connection `%s` left by an earlier import', connection_name)

    # Our response to produce
    out:'strlist' = []

    for connection_def in _connection_defs:

        # The type's own defaults go in first so that what the demo asks for wins over them,
        # the audit log being on among it
        request = dict(_type_defaults[connection_def['type_']])

        request.update({
            'cluster_id': default_cluster_id,
            'is_active': True,
            'is_internal': False,
            'pool_size': 1,
            'is_audit_log_active': True,
        })
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

def _wait_for_main_channel() -> 'int':
    """ Waits for the listener the burst sends through and for the main demo channel's own
    route in it, returning the port to send to - zero when neither came up in time. A message
    that arrives before the route is registered matches no channel and is turned away.
    """
    steps_left = _wait_steps

    while steps_left:

        port = get_internal_port()

        if port:
            if is_channel_routed(Channel_Main):
                return port

        sleep(_wait_step_seconds)
        steps_left -= 1

    return 0

# ################################################################################################################################

def send_demo_burst() -> 'int':
    """ Sends a short burst of live messages through the main demo channel
    so the in-process counters and the last-message times show current life,
    not just the seeded history. Returns how many messages went out.
    """

    # The channel wrappers start asynchronously after their connections are created
    port = _wait_for_main_channel()

    # With no channel to receive them there is nothing to send - the seeded history
    # is still complete, only the live counters stay at zero.
    if not port:
        logger.info('The main demo channel did not come up, skipping the live demo burst')
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

    # The channels name this service, so it goes in before they do
    service_deployed = ensure_demo_service(server)

    created_names = ensure_demo_connections(server)
    rule_names = store_demo_rules(server)

    # The seeded history goes into the same audit database the server writes to,
    # collected in memory first and landing in one bulk transaction
    engine = get_audit_engine()

    result = seed_demo_data(engine, server_name=server.name, config=config)

    # The live burst fills the in-process counters
    burst_count = send_demo_burst()

    # Our response to produce
    out = {
        'created_connections': created_names,
        'service_deployed': service_deployed,
        'rule_names': rule_names,
        'message_count': result.message_count,
        'event_count': result.event_count,
        'alert_count': result.alert_count,
        'fhir_pair_count': result.fhir_pair_count,
        'config_event_count': result.config_event_count,
        'dedup_count': result.dedup_count,
        'resubmit_count': result.resubmit_count,
        'view_count': result.view_count,
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
