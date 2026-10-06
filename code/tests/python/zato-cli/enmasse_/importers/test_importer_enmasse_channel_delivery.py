# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a REST or SOAP channel's delivery keys are compared and taken out of a definition on import - they are never
# columns of the channel's row, they are compared through their own helper and the file is the source of truth for them.

# stdlib
from json import loads

# pytest
import pytest

# PyYAML
import yaml

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.channel_soap import ChannelSOAPImporter
from zato.cli.enmasse.util import Channel_Delivery_Fields, channel_delivery_needs_update, prepare_channel_delivery_fields, \
    take_channel_delivery_attrs
from zato.cli.enmasse.util.delivery import Channel_Delivery_Defaults
from zato.common.api import HTTP_SOAP
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ
_retry = HTTP_SOAP.Retry

_cluster_id = 1

_service_name = 'enmasse.channel.delivery.service'

_rest_channel_name = 'enmasse.channel.delivery.rest'
_soap_channel_name = 'enmasse.channel.delivery.soap'

_yaml_text = f"""
channel_rest:
  - name: {_rest_channel_name}
    service: {_service_name}
    url_path: /enmasse/channel/delivery/rest
    use_queue: true
    dlq_retries: 7
    queue_response: '{{"accepted": true}}'

channel_soap:
  - name: {_soap_channel_name}
    service: {_service_name}
    url_path: /enmasse/channel/delivery/soap
    soap_action: urn:orders
    soap_version: '1.1'
    use_queue: true
    dlq_retries: 7
    queue_response: '<ack/>'
"""

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def yaml_config() -> 'stranydict':
    out = yaml.safe_load(_yaml_text)
    return out

# ################################################################################################################################

@pytest.fixture
def session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding one cluster and the service the channels invoke.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        GenericObject.__table__,
        SMTP.__table__,
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    service = Service(None, _service_name, True, 'enmasse.channel.delivery.Service', False, cluster)
    session.add(service)

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def rest_importer() -> 'ChannelImporter':
    out = ChannelImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def soap_importer() -> 'ChannelSOAPImporter':
    out = ChannelSOAPImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

def _definitions(section:'str') -> 'any_':
    out = yaml.safe_load(_yaml_text)[section]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestChannelDeliveryHelpers:

    def test_the_keys_leave_the_definition_and_the_absent_ones_take_their_defaults(self) -> 'None':

        definition = {'name': 'orders', 'url_path': '/orders', _queue.Field_Use_Queue: True, _dlq.Field_Retries: 7}

        prepare_channel_delivery_fields(definition, 'channel_rest')
        attrs = take_channel_delivery_attrs(definition)

        # Nothing of the delivery keys stays behind, the channel's own keys do
        assert definition == {'name': 'orders', 'url_path': '/orders'}

        # Every key is there - the two the definition gave and the rest at their defaults
        assert set(attrs) == set(Channel_Delivery_Fields)
        assert attrs[_queue.Field_Use_Queue] is True
        assert attrs[_dlq.Field_Retries] == 7
        assert attrs[_retry.Field_Max_Retries] == _retry.Default_Max_Retries
        assert attrs[_queue.Field_Queue_Response] == _queue.Default_Queue_Response

# ################################################################################################################################

    def test_a_definition_without_the_keys_is_all_defaults(self) -> 'None':

        definition = {'name': 'orders', 'url_path': '/orders'}

        prepare_channel_delivery_fields(definition, 'channel_rest')
        attrs = take_channel_delivery_attrs(definition)

        assert attrs == Channel_Delivery_Defaults

# ################################################################################################################################

    def test_a_row_that_predates_the_keys_matches_a_definition_without_them(self) -> 'None':

        definition = {'name': 'orders'}
        db_def = {'name': 'orders', 'opaque1': None}

        assert not channel_delivery_needs_update(definition, db_def)

# ################################################################################################################################

    def test_a_row_that_predates_the_keys_differs_from_a_definition_with_them(self) -> 'None':

        definition = {'name': 'orders', _queue.Field_Use_Queue: True}
        db_def = {'name': 'orders', 'opaque1': None}

        assert channel_delivery_needs_update(definition, db_def)

# ################################################################################################################################

    def test_a_static_response_without_the_queue_names_both_keys(self) -> 'None':

        definition = {'name': 'orders', _queue.Field_Queue_Response: 'OK'}

        with pytest.raises(Exception) as context:
            prepare_channel_delivery_fields(definition, 'channel_rest')

        message = str(context.value)
        assert _queue.Field_Queue_Response in message
        assert _queue.Field_Use_Queue in message
        assert 'orders' in message

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelDeliveryCompare:

    def test_the_delivery_keys_are_not_columns_of_the_row(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'ChannelImporter',
    ) -> 'None':
        created, _ = rest_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        channel = created[0]

        # The keys live in the opaque attributes and nowhere else
        opaque = loads(channel.opaque1)
        for name in Channel_Delivery_Fields:
            assert name in opaque, name
            assert name not in HTTPSOAP.__table__.columns, name

# ################################################################################################################################

    def test_the_same_file_compares_as_unchanged(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'ChannelImporter',
    ) -> 'None':
        _, _ = rest_importer.sync_channel_rest(yaml_config['channel_rest'], session)

        db_defs = rest_importer.get_rest_channels_from_db(session, _cluster_id)
        to_create, to_update = rest_importer.compare_channel_rest(_definitions('channel_rest'), db_defs)

        assert to_create == []
        assert to_update == []

# ################################################################################################################################

    def test_a_changed_delivery_key_compares_as_an_update(
        self,
        yaml_config:'stranydict',
        session:'any_',
        rest_importer:'ChannelImporter',
    ) -> 'None':
        _, _ = rest_importer.sync_channel_rest(yaml_config['channel_rest'], session)
        db_defs = rest_importer.get_rest_channels_from_db(session, _cluster_id)

        for name, value in ((_dlq.Field_Retries, 1), (_queue.Field_Queue_Response, '{"accepted": false}'), (_retry.Field_Max_Retries, 2)):
            definitions = _definitions('channel_rest')
            definitions[0][name] = value

            _, to_update = rest_importer.compare_channel_rest(definitions, db_defs)
            assert len(to_update) == 1, name

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelDeliveryCompare:

    def test_the_delivery_keys_are_not_columns_of_the_row(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)
        channel = created[0]

        opaque = loads(channel.opaque1)
        for name in Channel_Delivery_Fields:
            assert name in opaque, name
            assert name not in HTTPSOAP.__table__.columns, name

# ################################################################################################################################

    def test_the_same_file_compares_as_unchanged(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        _, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)

        db_defs = soap_importer.get_soap_channels_from_db(session, _cluster_id)
        to_create, to_update = soap_importer.compare_channel_soap(_definitions('channel_soap'), db_defs)

        assert to_create == []
        assert to_update == []

# ################################################################################################################################

    def test_a_changed_delivery_key_compares_as_an_update(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        _, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)
        db_defs = soap_importer.get_soap_channels_from_db(session, _cluster_id)

        for name, value in ((_dlq.Field_Retries, 1), (_queue.Field_Queue_Response, '<nack/>'), (_retry.Field_Max_Retries, 2)):
            definitions = _definitions('channel_soap')
            definitions[0][name] = value

            _, to_update = soap_importer.compare_channel_soap(definitions, db_defs)
            assert len(to_update) == 1, name

# ################################################################################################################################
# ################################################################################################################################
