# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The server side of the demo-data import - plain functions the server calls,
# no service of their own. The data itself comes from zato.common.demo.seed,
# this module adds what needs a live server - the demo connections and a burst
# of live MLLP traffic that fills the in-process channel counters.

# stdlib
import os
from contextlib import closing
from logging import getLogger
from time import monotonic, sleep

# Zato
from zato.common.api import HL7
from zato.common.audit_log.api import get_audit_engine
from zato.common.defaults import default_cluster_id
from zato.common.demo.seed import get_demo_rule_defs, purge_demo_data, seed_demo_data, Channel_Clinic, Channel_Lab, \
    Channel_Main, Facilities_By_Channel, Outconn_FHIR, Outconn_Forward, Route_Clinic, Route_Lab, Route_Main, SeedConfig
from zato.common.destination.constants import DestinationType
from zato.common.hl7.feed import generate_feed_items, rewrite_msh_field, FeedConfig, MSH3_Index, MSH4_Index
from zato.common.hl7.fhir.fields import Outconn_Config_Defaults as FHIR_Outconn_Defaults
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.fields import Channel_Defaults as MLLP_Channel_Defaults, \
    Outconn_Defaults as MLLP_Outconn_Defaults
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn, HTTPSOAP
from zato.common.typing_ import cast_
from zato.common.util.api import hex_sequence_to_bytes
from zato.common.util.open_ import open_w
from zato.server.generic.api.channel_hl7_mllp import get_internal_port, is_channel_routed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, stranydict, strlist
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    anytuple = anytuple
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

# The service behind the demo MLLP channels and the one behind the archive's REST intake -
# both deployed from the one file whose source is below
_channel_service = 'demo.hl7.ack'
_archive_service = 'demo.hl7.archive'

# What the demo services are deployed as
_channel_service_file_name = 'demo_hl7_ack.py'

# The REST pieces the archive destination runs on - the outgoing connection the channels
# deliver through and the channel that receives what they deliver, both on this very server
_archive_outconn = 'demo.hl7.archive'
_archive_intake_channel = 'demo.hl7.archive.intake'
_archive_url_path = '/demo/hl7/archive'

# The addresses the demo outgoing connections point at - reserved names
# that never resolve, the demo only needs the objects to exist
_forward_address = 'demo-ehr.invalid:2575'
_fhir_address = 'https://demo-ehr.invalid/fhir'

# How many live messages the burst sends through the main demo channel
_burst_count = 20

# The seed the burst messages are generated from
_burst_seed = 20260102

# Hot deploy and the channel wrappers both run on their own, so the import waits for what
# it needs rather than assuming it is there - this is how long it waits, in steps short
# enough that no time is lost once the awaited thing is up
_wait_steps = 200
_wait_step_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

# The demo services' own source, deployed as it is. The channel handles the protocol itself -
# the acknowledgment goes back to the sender and each destination receives a copy of every
# accepted message with no help from the services below.
_channel_service_source = '''\
# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

# ################################################################################################################################

class DemoHL7Ack(Service):
    """ Runs for each message an MLLP channel accepts.
    """
    name = '{ack_service}'

    def handle(self):

        message = self.request.raw_request
        control_id = message.get('msh.message_control_id')

        self.logger.info('Received message `%s`', control_id)

# ################################################################################################################################

class DemoHL7Archive(Service):
    """ Receives a copy of each accepted message through a REST destination.
    """
    name = '{archive_service}'

    def handle(self):

        message = self.request.raw_request
        self.logger.info('Archived message `%s`', message)

# ################################################################################################################################
'''.format(ack_service=_channel_service, archive_service=_archive_service)

# ################################################################################################################################
# ################################################################################################################################

# Every demo channel delivers a copy of each accepted message to the archive
_channel_destinations = dumps([{
    'name': _archive_outconn,
    'type': DestinationType.REST,
    'connection': _archive_outconn,
    'is_active': True,
    'options': {'method': 'POST'},
}])

# ################################################################################################################################
# ################################################################################################################################

# What each demo connection is created with, beyond the shared boilerplate
_connection_defs:'anytuple' = (
    {
        'name': Channel_Main,
        'type_': _type_channel_mllp,
        'is_channel': True,
        'is_outconn': False,
        'service': _channel_service,
        'msh3_sending_app': Route_Main,
        'should_return_errors': True,
        'destinations': _channel_destinations,
    },
    {
        'name': Channel_Lab,
        'type_': _type_channel_mllp,
        'is_channel': True,
        'is_outconn': False,
        'service': _channel_service,
        'msh3_sending_app': Route_Lab,
        'should_return_errors': True,
        'destinations': _channel_destinations,
    },
    {
        'name': Channel_Clinic,
        'type_': _type_channel_mllp,
        'is_channel': True,
        'is_outconn': False,
        'service': _channel_service,
        'msh3_sending_app': Route_Clinic,
        'should_return_errors': True,
        'destinations': _channel_destinations,
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
    """ Deploys the demo services and waits for them to come up. The file is always written,
    so a rerun replaces an earlier version in place. Returns whether the channels can be
    pointed at what it deploys.
    """
    file_path = os.path.join(server.hot_deploy_config.pickup_dir, _channel_service_file_name)

    with open_w(file_path) as f:
        _ = f.write(_channel_service_source)

    # Hot deploy picks the file up on its own, so the services are not there the moment
    # their source is - the channels and the burst that follow both need them to be
    steps_left = _wait_steps

    while steps_left:

        if server.service_store.is_deployed(_channel_service):
            if server.service_store.is_deployed(_archive_service):
                logger.info('Deployed the demo services from %s', file_path)
                return True

        sleep(_wait_step_seconds)
        steps_left -= 1

    logger.warning('The demo services did not deploy from %s', file_path)
    return False

# ################################################################################################################################

def _build_connection_request(connection_def:'stranydict') -> 'stranydict':
    """ Builds the request a demo connection is created or corrected with - the type's own
    defaults first so that what the demo asks for wins over them, the audit log being on among it.
    """
    out = dict(_type_defaults[connection_def['type_']])

    out.update({
        'cluster_id': default_cluster_id,
        'is_active': True,
        'is_internal': False,
        'pool_size': 1,
        'is_audit_log_active': True,
    })
    out.update(connection_def)

    return out

# ################################################################################################################################

def _connection_matches(connection_def:'stranydict', existing:'any_') -> 'bool':
    """ Whether a connection stored in the database still says what its demo definition says.
    Only the fields a definition pins down are compared - the address of an outgoing connection
    and the destinations of a channel, the latter kept in the opaque attributes the row carries.
    """
    if 'address' in connection_def:
        if existing[2] != connection_def['address']:
            return False

    if 'destinations' in connection_def:

        if existing[3]:
            opaque = loads(existing[3])
        else:
            opaque = {}

        if opaque.get('destinations') != connection_def['destinations']:
            return False

    return True

# ################################################################################################################################

def ensure_demo_connections(server:'ParallelServer') -> 'strlist':
    """ Creates the demo channels and outgoing connections that are not there yet. The ones
    already in place keep running as they are - recreating them would restart their wrappers
    and every rerun would then wait for the listeners to come back up. The one exception is
    a connection that no longer stores what the demo definition says - an earlier import's
    address or destinations left in place would keep the old wiring alive, so such a
    connection is corrected in place. Returns the names created or corrected.
    """

    # What already exists is read straight from the database, the address and the opaque
    # attributes included, because stale ones are what a rerun does correct
    demo_names = [connection_def['name'] for connection_def in _connection_defs]

    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.id, GenericConn.name, GenericConn.address, GenericConn.opaque1).filter(
            GenericConn.name.in_(demo_names)).all()

    existing_by_name = {}

    for row in rows:
        existing_by_name[row[1]] = row

    # Our response to produce
    out:'strlist' = []

    for connection_def in _connection_defs:

        name = connection_def['name']

        # A connection an earlier import created keeps running as it is,
        # unless what it stores no longer matches the definition
        if name in existing_by_name:

            existing = existing_by_name[name]

            if not _connection_matches(connection_def, existing):

                request = _build_connection_request(connection_def)
                request['id'] = existing[0]

                _ = server.invoke('zato.generic.connection.edit', request)
                out.append(name)

            continue

        request = _build_connection_request(connection_def)

        _ = server.invoke('zato.generic.connection.create', request)
        out.append(name)

    return out

# ################################################################################################################################

def _build_archive_outconn_request(archive_host:'str') -> 'stranydict':
    """ The request the archive's outgoing REST connection is created or corrected with -
    the audit log is on so the usage page sees what goes out through it.
    """
    out = {
        'cluster_id': default_cluster_id,
        'name': _archive_outconn,
        'is_active': True,
        'is_internal': False,
        'connection': 'outgoing',
        'transport': 'plain_http',
        'host': archive_host,
        'url_path': _archive_url_path,
        'is_audit_log_active': True,
    }

    return out

# ################################################################################################################################

def _build_archive_channel_request() -> 'stranydict':
    """ The request the archive's intake REST channel is created with - the same shape
    the Dashboard gives an HL7 REST channel, with the audit log on so the usage page
    sees what it receives.
    """
    out = {
        'cluster_id': default_cluster_id,
        'name': _archive_intake_channel,
        'is_active': True,
        'is_internal': False,
        'connection': 'channel',
        'transport': 'plain_http',
        'url_path': _archive_url_path,
        'service': _archive_service,
        'data_format': HL7.Const.Version.v2.id,
        'should_parse_on_input': True,
        'match_slash': False,
        'merge_url_params_req': True,
        'is_audit_log_active': True,
    }

    return out

# ################################################################################################################################

def _is_rest_audit_on(opaque_text:'str | None') -> 'bool':
    """ Whether an http-soap row's opaque attributes say its audit log is on -
    a row from before the flag was set stores it as null, which counts as off.
    """
    if opaque_text:
        opaque = loads(opaque_text)
    else:
        opaque = {}

    if 'is_audit_log_active' in opaque:
        out = opaque['is_audit_log_active'] is True
    else:
        out = False

    return out

# ################################################################################################################################

def ensure_demo_rest_objects(server:'ParallelServer') -> 'strlist':
    """ Creates the REST pieces the archive destination runs on - the outgoing connection
    the channels deliver through and the channel that receives what they deliver, both on
    this very server. What is already in place is left alone, except a host that no longer
    points back here or an audit log left off by an earlier import - the usage page needs
    it on. Returns the names created or corrected.
    """
    archive_host = f'http://127.0.0.1:{server.port}'

    demo_names = [_archive_outconn, _archive_intake_channel]
    rest_name_column = cast_('any_', HTTPSOAP.name)

    with closing(server.odb.session()) as session:
        rows = session.query(HTTPSOAP.id, HTTPSOAP.name, HTTPSOAP.host, HTTPSOAP.opaque1).filter(
            rest_name_column.in_(demo_names)).all()

    existing_by_name = {}

    for row in rows:
        existing_by_name[row[1]] = row

    # Our response to produce
    out:'strlist' = []

    # The outgoing connection points back at this very server, so an earlier import's
    # host is corrected when the server's own address has changed since, as is
    # an audit log an earlier import left off ..
    if _archive_outconn in existing_by_name:

        existing = existing_by_name[_archive_outconn]

        if existing[2] != archive_host or not _is_rest_audit_on(existing[3]):

            request = _build_archive_outconn_request(archive_host)
            request['id'] = existing[0]

            _ = server.invoke('zato.http-soap.edit', request)
            out.append(_archive_outconn)
    else:
        request = _build_archive_outconn_request(archive_host)

        _ = server.invoke('zato.http-soap.create', request)
        out.append(_archive_outconn)

    # .. and the intake channel receives what goes out through it.
    if _archive_intake_channel in existing_by_name:

        existing = existing_by_name[_archive_intake_channel]

        if not _is_rest_audit_on(existing[3]):

            request = _build_archive_channel_request()
            request['id'] = existing[0]

            _ = server.invoke('zato.http-soap.edit', request)
            out.append(_archive_intake_channel)
    else:
        request = _build_archive_channel_request()

        _ = server.invoke('zato.http-soap.create', request)
        out.append(_archive_intake_channel)

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

    # The live messages come from the same facilities the seeded week does, so the channel
    # has one set of callers rather than one for its history and another for its live traffic
    facilities = Facilities_By_Channel[Channel_Main]
    facility_count = len(facilities)

    for index, item in enumerate(items):

        # Every burst message routes to the main demo channel ..
        text = rewrite_msh_field(item.text, MSH3_Index, Route_Main)

        # .. and the facilities take turns sending them.
        facility = facilities[index % facility_count]
        text = rewrite_msh_field(text, MSH4_Index, facility)

        _ = client.send(text.encode('utf-8'), item.control_id)

    return len(items)

# ################################################################################################################################

def import_demo_data(server:'ParallelServer', *, config:'SeedConfig | None'=None) -> 'stranydict':
    """ Runs the whole demo import on a live server - the connections, the seeded
    week of history and the live burst. Rerunning replaces the previous demo data
    instead of stacking on it.
    """
    if config is None:
        config = SeedConfig()

    # The channels and the archive intake name these services, so they go in first
    phase_start = monotonic()
    service_deployed = ensure_demo_service(server)

    service_seconds = monotonic() - phase_start
    logger.info('Demo import: services ready in %.2fs', service_seconds)

    # The channels deliver to the archive, so its REST pieces go in before they do
    phase_start = monotonic()
    rest_names = ensure_demo_rest_objects(server)

    rest_seconds = monotonic() - phase_start
    logger.info('Demo import: REST archive ready in %.2fs', rest_seconds)

    phase_start = monotonic()
    created_names = ensure_demo_connections(server)

    connections_seconds = monotonic() - phase_start
    logger.info('Demo import: connections ready in %.2fs', connections_seconds)

    # The rule names the seeded alert history is composed under - the alert rules
    # themselves live in the rule engine's alerts ruleset, not in the ODB
    rule_names = [rule_def['name'] for rule_def in get_demo_rule_defs()]

    # The seeded history goes into the same audit database the server writes to,
    # collected in memory first and landing in one bulk transaction
    engine = get_audit_engine()

    phase_start = monotonic()
    result = seed_demo_data(engine, server_name=server.name, config=config)

    seed_seconds = monotonic() - phase_start
    logger.info('Demo import: history seeded in %.2fs', seed_seconds)

    # The live burst fills the in-process counters
    phase_start = monotonic()
    burst_count = send_demo_burst()

    burst_seconds = monotonic() - phase_start
    logger.info('Demo import: live burst sent in %.2fs', burst_seconds)

    # Our response to produce
    out = {
        'created_connections': created_names,
        'created_rest_objects': rest_names,
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
    """ Undoes the demo import - the connections and every demo row
    in the audit database. Returns the names of what was deleted.
    """
    demo_names = [connection_def['name'] for connection_def in _connection_defs]

    # The connections go first, so nothing writes new demo events meanwhile
    with closing(server.odb.session()) as session:
        rows = session.query(GenericConn.id, GenericConn.name).filter(GenericConn.name.in_(demo_names)).all()

    deleted_connections:'strlist' = []

    for connection_id, connection_name in rows:
        _ = server.invoke('zato.generic.connection.delete', {'id': connection_id, 'cluster_id': default_cluster_id})
        deleted_connections.append(connection_name)

    # The archive's REST pieces go the same way
    rest_name_column = cast_('any_', HTTPSOAP.name)

    with closing(server.odb.session()) as session:
        rest_rows = session.query(HTTPSOAP.id, HTTPSOAP.name).filter(
            rest_name_column.in_([_archive_outconn, _archive_intake_channel])).all()

    for rest_id, rest_name in rest_rows:
        _ = server.invoke('zato.http-soap.delete', {'id': rest_id, 'cluster_id': default_cluster_id})
        deleted_connections.append(rest_name)

    # The audit rows go next
    engine = get_audit_engine()
    purge_demo_data(engine)

    # The services file the import once wrote goes away too, so a restart does not redeploy it
    file_path = os.path.join(server.hot_deploy_config.pickup_dir, _channel_service_file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

    # Our response to produce
    out = {
        'deleted_connections': deleted_connections,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
