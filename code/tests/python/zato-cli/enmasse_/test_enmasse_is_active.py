# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An object's is_active in YAML is what the row gets - on create and on an update that flips it - for every type
# a live proof deactivates once it is through with its objects: REST and SOAP channels and outgoing connections,
# FHIR, MLLP and LLM connections. A definition that says nothing about it is active.

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_mllp import ChannelMLLPImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.channel_soap import ChannelSOAPImporter
from zato.cli.enmasse.importers.llm import LLMImporter
from zato.cli.enmasse.importers.outgoing_fhir import OutgoingFHIRImporter
from zato.cli.enmasse.importers.outgoing_mllp import OutgoingMLLPImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.common.api import HTTP_SOAP
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, IntervalBasedJob, Job, \
    SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster every object in the test database belongs to
_cluster_id = 1

# The service the channels invoke
_service_name = 'enmasse.is_active.service'

# Each type under test - the importer class, the name of its sync method, the smallest definition it accepts
# and the model its rows are of
_types = {
    'channel_rest': (ChannelImporter, 'sync_channel_rest',
        {'name': 'enmasse.is_active.channel.rest', 'service': _service_name, 'url_path': '/enmasse/is-active/rest'}, HTTPSOAP),
    'channel_soap': (ChannelSOAPImporter, 'sync_channel_soap',
        {'name': 'enmasse.is_active.channel.soap', 'service': _service_name, 'url_path': '/enmasse/is-active/soap',
         'soap_action': 'urn:enmasse', 'soap_version': '1.1'}, HTTPSOAP),
    'outgoing_rest': (OutgoingRESTImporter, 'sync_outgoing_rest',
        {'name': 'enmasse.is_active.outgoing.rest', 'host': 'https://rest.example.com', 'url_path': '/api'}, HTTPSOAP),
    'outgoing_soap': (OutgoingSOAPImporter, 'sync_outgoing_soap',
        {'name': 'enmasse.is_active.outgoing.soap', 'host': 'https://soap.example.com', 'url_path': '/soap',
         'soap_action': 'urn:enmasse', 'soap_version': '1.1'}, HTTPSOAP),
    'outgoing_fhir': (OutgoingFHIRImporter, 'sync_definitions',
        {'name': 'enmasse.is_active.outgoing.fhir', 'address': 'https://fhir.example.com/r4'}, GenericConn),
    'channel_mllp': (ChannelMLLPImporter, 'sync_definitions',
        {'name': 'enmasse.is_active.channel.mllp', 'service': _service_name}, GenericConn),
    'outgoing_mllp': (OutgoingMLLPImporter, 'sync_definitions',
        {'name': 'enmasse.is_active.outgoing.mllp', 'address': 'lab.example.com:2575'}, GenericConn),
    'llm': (LLMImporter, 'sync_definitions',
        {'name': 'enmasse.is_active.llm', 'address': 'https://api.openai.com/v1', 'model': 'gpt-4o', 'api_key': 'key'},
        GenericConn),
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding one cluster, the service the channels invoke
    and the service a health check job dispatches to.
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
        Job.__table__,
        IntervalBasedJob.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    session.add(Service(None, _service_name, True, 'enmasse.is_active.Service', False, cluster))
    session.add(Service(None, HTTP_SOAP.HealthCheck.Dispatch_Service, True,
        'zato.server.service.internal.connection.HealthCheckRun', True, cluster))

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

def _sync(type_name:'str', session:'any_', definition:'anydict') -> 'tuple':
    """ One import of one definition through the importer of the type, on a fresh importer each time
    the way each enmasse run is.
    """
    importer_class, method_name, _, _ = _types[type_name]
    importer = importer_class(EnmasseYAMLImporter())
    sync = getattr(importer, method_name)

    out = sync([dict(definition)], session)
    session.commit()

    return out

# ################################################################################################################################

def _stored(type_name:'str', session:'any_') -> 'any_':
    _, _, definition, model = _types[type_name]
    out = session.query(model).filter_by(name=definition['name']).one()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestIsActive:

    @pytest.mark.parametrize('type_name', sorted(_types))
    def test_a_definition_saying_nothing_is_active(self, type_name:'str', session:'any_') -> 'None':
        _, _, definition, _ = _types[type_name]

        created, _ = _sync(type_name, session, definition)

        assert len(created) == 1
        assert _stored(type_name, session).is_active is True

# ################################################################################################################################

    @pytest.mark.parametrize('type_name', sorted(_types))
    def test_an_inactive_definition_creates_an_inactive_row(self, type_name:'str', session:'any_') -> 'None':
        _, _, definition, _ = _types[type_name]
        inactive = dict(definition, is_active=False)

        created, _ = _sync(type_name, session, inactive)

        assert len(created) == 1
        assert _stored(type_name, session).is_active is False

# ################################################################################################################################

    @pytest.mark.parametrize('type_name', sorted(_types))
    def test_flipping_is_active_updates_the_row(self, type_name:'str', session:'any_') -> 'None':
        _, _, definition, _ = _types[type_name]

        # An active row first ..
        _ = _sync(type_name, session, definition)
        assert _stored(type_name, session).is_active is True

        # .. the same definition, inactive, is an update and not a second row ..
        inactive = dict(definition, is_active=False)
        created, updated = _sync(type_name, session, inactive)

        assert len(created) == 0
        assert len(updated) == 1
        assert _stored(type_name, session).is_active is False

        # .. and back again.
        created, updated = _sync(type_name, session, dict(definition, is_active=True))

        assert len(created) == 0
        assert len(updated) == 1
        assert _stored(type_name, session).is_active is True

# ################################################################################################################################
# ################################################################################################################################
