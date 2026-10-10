# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An item marked should_delete in any enmasse section is resolved to its row by name, or by security for the pub/sub
# sections keyed that way, and deleted through the admin service the Dashboard invokes, with the id of the row.
# The import refuses a file that both deletes and defines or references an object, deletes before it creates,
# defers quota tiers until after the create and update pass, and reports what it deleted.

# stdlib
from datetime import datetime
from json import dumps, loads

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importer import delete_targets as targets
from zato.cli.enmasse.importers.custom import custom_key_to_connection_type
from zato.cli.enmasse.util.secrets import Session_Key_Crypto_Manager
from zato.cli.enmasse_command import write_result_file
from zato.common.api import AMQP, HTTP_SOAP, SCHEDULER, SEC_DEF_TYPE
from zato.common.crypto.api import ServerCryptoManager
from zato.common.odb.model import Base, ChannelAMQP, Cluster, GenericConn, GenericObject, HTTPBasicAuth, HTTPSOAP, IMAP, \
    IntervalBasedJob, Job, OutgoingAMQP, OutgoingOdoo, PubSubPermission, PubSubSubscription, PubSubTopic, SecurityBase, \
    Service, SMTP, SQLConnectionPool
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The cluster every object in the test database belongs to
_cluster_id = 1

# The service the channels and jobs point to
_service_name = 'enmasse.should_delete.service'

# The name every object under test is created with, and the security definition the pub/sub sections are keyed by
_object_name   = 'enmasse.should_delete.object'
_security_name = 'enmasse.should_delete.security'

# A custom connector section, which resolves its type from its key
_custom_section = 'custom_crm'

# Persistent delivery, the mode an outgoing AMQP row is stored with
_amqp_delivery_mode = 2

# Every section that supports deletion, in the order the registry deletes them in, with the deferred one last
_sections:'strlist' = []

for _section in targets.delete_order:
    if _section == targets.Custom_Sections_Marker:
        _sections.append(_custom_section)
    else:
        _sections.append(_section)

_sections.extend(targets.deferred_sections)

# ################################################################################################################################
# ################################################################################################################################

class _Response:
    def __init__(self, ok:'bool', details:'str') -> 'None':
        self.ok = ok
        self.details = details
        self.data = {}

# ################################################################################################################################

class _RecordingClient:
    """ Stands in for the server client - records every invocation, lets a test observe the state at the time
    of each one, and refuses the services it is told to refuse.
    """
    def __init__(self) -> 'None':
        self.invocations:'anylist' = []
        self.refused:'strlist' = []
        self.observer:'callable_ | None' = None

    def invoke(self, service:'str', request:'anydict') -> '_Response':
        self.invocations.append((service, dict(request)))

        if self.observer is not None:
            self.observer(service)

        if service in self.refused:
            out = _Response(False, f'Refused by the test: {service}')
        else:
            out = _Response(True, '')

        return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database with the whole schema, one cluster and the service
    the channels and jobs point to.
    """
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    session.info[Session_Key_Crypto_Manager] = ServerCryptoManager.from_secret_key(ServerCryptoManager.generate_key())

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    session.add(Service(None, _service_name, True, 'enmasse.should_delete.Service', False, cluster))
    session.add(Service(None, HTTP_SOAP.HealthCheck.Dispatch_Service, True,
        'zato.server.service.internal.connection.HealthCheckRun', True, cluster))

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def importer() -> 'any_':
    """ An importer whose delete services are recorded rather than invoked on a server.
    """
    out = EnmasseYAMLImporter()
    out.delete_client = cast_('any_', _RecordingClient())
    return out

# ################################################################################################################################
# ################################################################################################################################

def _add_security(session:'any_', name:'str') -> 'any_':
    cluster = session.query(Cluster).one()
    row = HTTPBasicAuth(None, name, True, 'user', 'realm', 'password', cluster)
    session.add(row)
    session.commit()
    return row

# ################################################################################################################################

def _insert(session:'any_', table:'any_', **values:'any_') -> 'any_':
    """ Inserts one row through the table directly - for the models whose constructors do not accept every column.
    """
    result = session.execute(table.insert().values(**values))
    session.commit()

    out = result.inserted_primary_key[0]
    return out

# ################################################################################################################################

def _insert_amqp(section:'str', session:'any_', name:'str') -> 'any_':
    _, subtype, service = targets.amqp_sections[section]

    # The subtype is stored the way the AMQP importers store it - a serialized document assigned to the JSON column
    opaque1 = dumps({'subtype': subtype})

    if service == targets.Service_Channel_AMQP:
        service_row = session.query(Service).filter_by(name=_service_name).one()
        out = _insert(session, ChannelAMQP.__table__, name=name, is_active=True, address='localhost:5672', username='user',
            password='password', queue='queue', pool_size=1, ack_mode='ack', prefetch_count=1, service_id=service_row.id,
            opaque1=opaque1)
    else:
        out = _insert(session, OutgoingAMQP.__table__, name=name, is_active=True, address='localhost:5672', username='user',
            password='password', delivery_mode=_amqp_delivery_mode, priority=AMQP.DEFAULT.PRIORITY, pool_size=1,
            opaque1=opaque1)

    return out

# ################################################################################################################################

def _insert_model(section:'str', session:'any_', name:'str') -> 'any_':
    cluster = session.query(Cluster).one()

    if section == 'scheduler':
        service_row = session.query(Service).filter_by(name=_service_name).one()
        row = Job(None, name, True, SCHEDULER.JOB_TYPE.INTERVAL_BASED, datetime.utcnow(), None, cluster, service=service_row)
        _ = IntervalBasedJob(None, row, seconds=60)

    elif section == 'sql':
        out = _insert(session, SQLConnectionPool.__table__, name=name, is_active=True, username='user', password='password',
            db_name='db', engine='postgresql+pg8000', host='localhost', port=5432, pool_size=1, cluster_id=_cluster_id)
        return out

    elif section == 'email_smtp':
        row = SMTP(name=name, is_active=True, host='localhost', port=25, timeout=10, is_debug=False, mode='plain',
            ping_address='test@example.com', cluster=cluster)

    elif section == 'email_imap':
        row = IMAP(name=name, is_active=True, host='localhost', port=993, timeout=10, debug_level=0, mode='ssl',
            get_criteria='UNSEEN', cluster=cluster)

    elif section == 'odoo':
        out = _insert(session, OutgoingOdoo.__table__, name=name, is_active=True, host='localhost', port=8069, user='user',
            database='db', protocol='jsonrpc', pool_size=1, password='password', cluster_id=_cluster_id)
        return out

    else:
        row = PubSubTopic(name=name, is_active=True, cluster_id=_cluster_id)

    session.add(row)
    session.commit()

    out = row.id
    return out

# ################################################################################################################################

def _add_security_keyed(section:'str', session:'any_') -> 'any_':
    security = _add_security(session, _security_name)

    if section == 'pubsub_permission':
        row = PubSubPermission(pattern='orders.*', access_type='publisher', sec_base_id=security.id, cluster_id=_cluster_id)
    else:
        row = PubSubSubscription(sub_key='zpsk.test', delivery_type='pull', sec_base_id=security.id, cluster_id=_cluster_id)

    return row

# ################################################################################################################################

def _create_object(section:'str', session:'any_', name:'str'=_object_name) -> 'any_':
    """ Creates the row an item of the section resolves to and returns its id.
    """
    cluster = session.query(Cluster).one()

    if section in targets.model_sections:
        out = _insert_model(section, session, name)
        return out

    if section in targets.amqp_sections:
        out = _insert_amqp(section, session, name)
        return out

    if section in targets.http_soap_sections:
        connection, transport = targets.http_soap_sections[section]
        row = HTTPSOAP(name=name, is_active=True, is_internal=False, connection=connection, transport=transport,
            url_path='/enmasse/should-delete', soap_action='', cluster=cluster)

    elif section in targets.generic_sections or targets.is_custom_section(section):
        if targets.is_custom_section(section):
            type_ = custom_key_to_connection_type(section)
        else:
            type_ = targets.generic_sections[section]
        row = GenericConn(name=name, type_=type_, is_active=True, is_channel=False, is_outconn=True,
            cluster_id=_cluster_id)

    elif section in targets.generic_object_sections:
        type_, subtype, _ = targets.generic_object_sections[section]
        row = GenericObject(name=name, type_=type_, subtype=subtype, cluster_id=_cluster_id)

    elif section == 'security':
        row = _add_security(session, name)

    else:
        row = _add_security_keyed(section, session)

    session.add(row)
    session.commit()

    out = row.id
    return out

# ################################################################################################################################

def _section_object_name(section:'str') -> 'str':
    """ The name of the section's object when every section has one object of its own.
    """
    out = f'{_object_name}.{section}'
    return out

# ################################################################################################################################

def _expected_service(section:'str') -> 'str':
    """ The service the registry invokes for the row _create_object builds for the section.
    """
    if section in targets.http_soap_sections:
        out = targets.Service_HTTP_SOAP

    elif section in targets.generic_sections or targets.is_custom_section(section):
        out = targets.Service_Generic

    elif section in targets.generic_object_sections:
        out = targets.generic_object_sections[section][2]

    elif section in targets.model_sections:
        out = targets.model_sections[section][1]

    elif section in targets.amqp_sections:
        out = targets.amqp_sections[section][2]

    elif section == 'security':
        out = targets.security_services[SEC_DEF_TYPE.BASIC_AUTH]

    elif section == 'pubsub_permission':
        out = targets.Service_Permission

    else:
        out = targets.Service_Subscription

    return out

# ################################################################################################################################

def _marked_item(section:'str', name:'str'=_object_name) -> 'stranydict':
    """ The smallest item that marks the section's object for deletion.
    """
    key_field = targets.get_key_field(section)

    if key_field == targets.Key_Field_Security:
        key = _security_name
    else:
        key = name

    out = {key_field: key, targets.Should_Delete_Key: True}
    return out

# ################################################################################################################################

def _key_of(section:'str') -> 'str':
    out = _marked_item(section)[targets.get_key_field(section)]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResolutionAndServices:

    @pytest.mark.parametrize('section', _sections)
    def test_a_marked_item_deletes_through_the_service_of_its_section(
        self, section:'str', session:'any_', importer:'any_') -> 'None':

        row_id = _create_object(section, session)
        key = _key_of(section)
        service = _expected_service(section)

        _ = importer.sync_from_yaml({section: [_marked_item(section)]}, session)

        # The item was taken out of the file under its canonical section ..
        assert importer.deletions == {section: [key]}

        # .. the row it resolved to was reported ..
        assert importer.deleted_objects == {section: [{'name': key, 'id': row_id}]}

        if service:
            # .. and the service of the section received the id and the cluster, never the name.
            assert importer.delete_client.invocations == [(service, {'cluster_id': _cluster_id, 'id': row_id})]
        else:
            # .. or, for a section no service deletes, the row was removed in the session.
            assert importer.delete_client.invocations == []
            assert session.query(GenericObject).filter_by(id=row_id).first() is None

# ################################################################################################################################

    @pytest.mark.parametrize('alias', sorted(targets.section_aliases))
    def test_an_alias_deletes_under_its_canonical_section(self, alias:'str', session:'any_', importer:'any_') -> 'None':
        section = targets.section_aliases[alias]
        row_id = _create_object(section, session)

        _ = importer.sync_from_yaml({alias: [_marked_item(section)]}, session)

        assert importer.deletions == {section: [_object_name]}
        assert importer.delete_client.invocations == [(_expected_service(section), {'cluster_id': _cluster_id, 'id': row_id})]

# ################################################################################################################################

    @pytest.mark.parametrize('type_', sorted(targets.generic_type_to_section))
    def test_a_generic_connection_item_deletes_under_the_section_of_its_type(
        self, type_:'str', session:'any_', importer:'any_') -> 'None':

        section = targets.generic_type_to_section[type_]
        row_id = _create_object(section, session)

        item = dict(_marked_item(section), type=type_)
        _ = importer.sync_from_yaml({targets.Section_Generic_Connection: [item]}, session)

        assert importer.deletions == {section: [_object_name]}
        assert importer.delete_client.invocations == [(targets.Service_Generic, {'cluster_id': _cluster_id, 'id': row_id})]

# ################################################################################################################################

    def test_the_security_service_follows_the_stored_type(self, session:'any_', importer:'any_') -> 'None':

        # The row is stored as a bearer token definition, which YAML spells differently from the stored type ..
        row = _add_security(session, _object_name)
        row.sec_type = SEC_DEF_TYPE.OAUTH
        session.commit()

        # .. and the item names neither a type nor anything else beyond its name.
        _ = importer.sync_from_yaml({'security': [_marked_item('security')]}, session)

        service = targets.security_services[SEC_DEF_TYPE.OAUTH]
        assert importer.delete_client.invocations == [(service, {'cluster_id': _cluster_id, 'id': row.id})]

# ################################################################################################################################

    def test_every_permission_of_a_security_definition_is_deleted(self, session:'any_', importer:'any_') -> 'None':
        security = _add_security(session, _security_name)

        first = PubSubPermission(pattern='orders.*', access_type='publisher', sec_base_id=security.id, cluster_id=_cluster_id)
        second = PubSubPermission(pattern='invoices.*', access_type='subscriber', sec_base_id=security.id,
            cluster_id=_cluster_id)
        session.add_all([first, second])
        session.commit()

        _ = importer.sync_from_yaml({'pubsub_permission': [_marked_item('pubsub_permission')]}, session)

        invoked_ids = sorted(request['id'] for _, request in importer.delete_client.invocations)
        assert invoked_ids == sorted([first.id, second.id])
        assert len(importer.deleted_objects['pubsub_permission']) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestTheMarker:

    @pytest.mark.parametrize('section,item,model', [
        ('outgoing_rest', {'name': _object_name, 'host': 'https://rest.example.com', 'url_path': '/api'}, HTTPSOAP),
        ('llm', {'name': _object_name, 'address': 'https://api.openai.com/v1', 'model': 'gpt-4o', 'api_key': 'key'},
            GenericConn),
    ])
    def test_a_false_marker_creates_the_object_without_the_key(
        self, section:'str', item:'stranydict', model:'any_', session:'any_', importer:'any_') -> 'None':

        definition = dict(item, should_delete=False)
        created, _ = importer.sync_from_yaml({section: [definition]}, session)

        assert len(created[section]) == 1
        assert importer.deletions == {}
        assert importer.delete_client.invocations == []

        row = session.query(model).filter_by(name=_object_name).one()
        opaque = parse_instance_opaque_attr(row)

        assert targets.Should_Delete_Key not in opaque
        assert not hasattr(row, targets.Should_Delete_Key)

# ################################################################################################################################

    def test_a_marked_item_for_an_absent_object_is_skipped(self, session:'any_', importer:'any_') -> 'None':
        _ = importer.sync_from_yaml({'channel_rest': [_marked_item('channel_rest')]}, session)

        assert importer.deletions == {'channel_rest': [_object_name]}
        assert importer.deleted_objects == {}
        assert importer.delete_client.invocations == []

# ################################################################################################################################

    def test_a_file_without_deletions_never_acquires_a_client(self, session:'any_', importer:'any_') -> 'None':
        importer.delete_client = None

        item = {'name': _object_name, 'host': 'https://rest.example.com', 'url_path': '/api'}
        _ = importer.sync_from_yaml({'outgoing_rest': [item]}, session)

        assert importer.delete_client is None

# ################################################################################################################################

    def test_the_marker_is_refused_in_alert_rules(self, session:'any_', importer:'any_') -> 'None':
        section = targets.Section_Alert_Rules

        with pytest.raises(Exception, match=section):
            _ = importer.sync_from_yaml({section: [{'name': 'rule', 'should_delete': True}]}, session)

        assert importer.delete_client.invocations == []

# ################################################################################################################################

    def test_the_marker_is_refused_in_alert_notifications(self, session:'any_', importer:'any_') -> 'None':
        config = {targets.Section_Alert_Notifications: {'email_connection': 'smtp:mail', 'should_delete': True}}

        with pytest.raises(Exception, match=targets.Section_Alert_Notifications):
            _ = importer.sync_from_yaml(config, session)

        assert importer.delete_client.invocations == []

# ################################################################################################################################
# ################################################################################################################################

class TestRefusals:

    def test_the_same_key_marked_and_unmarked_is_refused(self, session:'any_', importer:'any_') -> 'None':
        _ = _create_object('outgoing_rest', session)

        defined = {'name': _object_name, 'host': 'https://rest.example.com', 'url_path': '/api'}
        config = {'outgoing_rest': [defined, _marked_item('outgoing_rest')]}

        with pytest.raises(Exception, match='both marked'):
            _ = importer.sync_from_yaml(config, session)

        # Nothing was written - the row is still there and no service ran
        assert importer.delete_client.invocations == []
        assert session.query(HTTPSOAP).filter_by(name=_object_name).count() == 1

# ################################################################################################################################

    def test_a_conflict_across_includes_is_refused(self, tmp_path:'any_', session:'any_', importer:'any_') -> 'None':

        included = tmp_path / 'included.yaml'
        _ = included.write_text(f'outgoing_rest:\n  - name: {_object_name}\n    should_delete: true\n')

        main = tmp_path / 'enmasse.yaml'
        _ = main.write_text(
            'include:\n  - included.yaml\n' +
            f'outgoing_rest:\n  - name: {_object_name}\n    host: https://rest.example.com\n    url_path: /api\n')

        config = importer.from_path(str(main))

        with pytest.raises(Exception, match='both marked'):
            _ = importer.sync_from_yaml(config, session)

        assert importer.delete_client.invocations == []

# ################################################################################################################################

    @pytest.mark.parametrize('config', [
        {'security': [{'name': _security_name, 'should_delete': True}],
         'channel_rest': [{'name': 'c', 'service': _service_name, 'url_path': '/c', 'security': _security_name}]},
        {'security': [{'name': _security_name, 'should_delete': True}],
         'outgoing_rest': [{'name': 'o', 'host': 'https://h', 'url_path': '/o', 'security_name': _security_name}]},
        {'security': [{'name': _security_name, 'should_delete': True}],
         'pubsub_permission': [{'security': _security_name, 'pub': ['orders.*']}]},
        {'security': [{'name': _security_name, 'should_delete': True}],
         'groups': [{'name': 'g', 'members': [_security_name]}]},
        {'groups': [{'name': 'g', 'should_delete': True}],
         'channel_rest': [{'name': 'c', 'service': _service_name, 'url_path': '/c', 'groups': ['g']}]},
        {'groups': [{'name': 'g', 'should_delete': True}],
         'mcp_gateway': [{'name': 'm', 'security_groups': ['g']}]},
        {'groups': [{'name': 'g', 'should_delete': True}],
         'rule_engine_api': [{'name': 'r', 'security_groups': ['g']}]},
        {'quota_tier': [{'name': 't', 'should_delete': True}],
         'security': [{'name': 's', 'type': 'basic_auth', 'username': 'u', 'quota_tier': 't'}]},
        {'quota_tier': [{'name': 't', 'should_delete': True}],
         'groups': [{'name': 'g', 'quota_tier': 't'}]},
        {'pubsub_topic': [{'name': 't', 'should_delete': True}],
         'pubsub_subscription': [{'security': 's', 'topic_list': ['t']}]},
        {'outgoing_rest': [{'name': 'o', 'should_delete': True}],
         'pubsub_subscription': [{'security': 's', 'topic_list': ['x'], 'push_rest_endpoint': 'o'}]},
        {'channel_rest': [{'name': 'c', 'should_delete': True}],
         'channel_openapi': [{'name': 'a', 'rest_channel_list': ['c']}]},
        {'pubsub_topic': [{'name': 't', 'should_delete': True}],
         'outgoing_as2': [{'name': 'a', 'inbound_topic': 't'}]},
        {'pubsub_topic': [{'name': 't', 'should_delete': True}],
         'channel_as4': [{'name': 'a', 'service': _service_name, 'url_path': '/a', 'as4_inbound_topic': 't'}]},
        {'email_smtp': [{'name': 'mail', 'should_delete': True}],
         'channel_rest': [{'name': 'c', 'service': _service_name, 'url_path': '/c',
            'alerts': {'email_connection': 'smtp:mail'}}]},
        {'llm': [{'name': 'brain', 'should_delete': True}],
         'channel_rest': [{'name': 'c', 'service': _service_name, 'url_path': '/c',
            'alerts': {'llm_connection': 'brain'}}]},
        {'email_imap': [{'name': 'mail', 'should_delete': True}],
         'alert_notifications': {'email_connection': 'imap:mail'}},
        {'sql': [{'name': 'db', 'should_delete': True}],
         'mcp_gateway': [{'name': 'm', 'sql_connections': ['db']}]},
    ])
    def test_a_reference_to_a_deleted_object_is_refused(self, config:'stranydict', session:'any_', importer:'any_') -> 'None':
        with pytest.raises(Exception, match='marks `should_delete`'):
            _ = importer.sync_from_yaml(config, session)

        assert importer.delete_client.invocations == []

# ################################################################################################################################

    def test_a_refusal_by_the_service_stops_the_import(self, session:'any_', importer:'any_') -> 'None':
        _ = _create_object('channel_rest', session)
        importer.delete_client.refused.append(targets.Service_HTTP_SOAP)

        replacement = {'name': 'enmasse.should_delete.replacement', 'host': 'https://rest.example.com', 'url_path': '/api'}
        config = {'channel_rest': [_marked_item('channel_rest')], 'outgoing_rest': [replacement]}

        with pytest.raises(Exception, match='Refused by the test'):
            _ = importer.sync_from_yaml(config, session)

        # The create and update pass never ran
        assert importer.created_objects == {}
        assert session.query(HTTPSOAP).filter_by(name=replacement['name']).first() is None

# ################################################################################################################################
# ################################################################################################################################

class TestOrderAndReporting:

    def test_deletions_follow_the_dependency_order(self, session:'any_', importer:'any_') -> 'None':

        # One object in every section, including the deferred one, each named after its section because
        # the AMQP and Azure Service Bus sections of one direction share a table with a unique name ..
        for section in _sections:
            if section not in targets.security_keyed_sections:
                _ = _create_object(section, session, _section_object_name(section))

        config:'stranydict' = {}

        for section in _sections:
            if section not in targets.security_keyed_sections:
                config[section] = [_marked_item(section, _section_object_name(section))]

        _ = importer.sync_from_yaml(config, session)

        # .. the services were invoked in the order of the registry, with the sections no service deletes
        # absent from the invocations and the quota tier last.
        expected:'strlist' = []

        for section in _sections:
            if section in targets.security_keyed_sections:
                continue
            service = _expected_service(section)
            if service:
                expected.append(service)

        invoked = [service for service, _ in importer.delete_client.invocations]

        assert invoked == expected
        assert invoked[-1] == targets.Service_Quota_Tier

# ################################################################################################################################

    def test_a_quota_tier_is_deleted_after_the_create_and_update_pass(self, session:'any_', importer:'any_') -> 'None':
        tier_id = _create_object('quota_tier', session)

        # A security definition in the same file is created before the tier is deleted ..
        security = {'name': 'enmasse.should_delete.new', 'type': 'basic_auth', 'username': 'user', 'realm': 'realm'}
        config = {'quota_tier': [_marked_item('quota_tier')], 'security': [security]}

        # .. which the count of such definitions at the time of the tier's deletion shows.
        counts_at_deletion:'list[int]' = []

        def observe(service:'str') -> 'None':
            count = session.query(SecurityBase).filter_by(name=security['name']).count()
            counts_at_deletion.append(count)

        importer.delete_client.observer = observe

        created, _ = importer.sync_from_yaml(config, session)

        assert len(created['security']) == 1
        assert importer.delete_client.invocations == [(targets.Service_Quota_Tier, {'cluster_id': _cluster_id, 'id': tier_id})]
        assert counts_at_deletion == [1]

# ################################################################################################################################

    def test_the_result_file_carries_the_deleted_counts(self, tmp_path:'any_', session:'any_', importer:'any_') -> 'None':
        _ = _create_object('channel_rest', session)
        _ = _create_object('llm', session)

        config = {'channel_rest': [_marked_item('channel_rest')], 'llm': [_marked_item('llm')]}
        created, updated = importer.sync_from_yaml(config, session)

        path = tmp_path / 'result.json'
        write_result_file(str(path), created, updated, importer.deleted_objects)

        data = loads(path.read_text())

        assert data['created'] == {}
        assert data['updated'] == {}
        assert data['deleted'] == {'channel_rest': 1, 'llm': 1}

        # The totals a repository deployment reports sum the same map
        assert sum(data['deleted'].values()) == 2

# ################################################################################################################################
# ################################################################################################################################
