# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A SOAP channel's alerts mapping - it imports into the same alert_ opaque keys a REST channel's does,
# the settings left out take the defaults, a re-import changes nothing, an update makes the file the source
# of truth, and the export writes only what moved away from the defaults, last among the channel's fields.

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
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.channel_soap import ChannelSOAPExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_soap import ChannelSOAPImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    Path = Path
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name
_smtp_name = 'enmasse.alerts.soap.smtp'
_llm_name = 'enmasse.alerts.soap.llm'

# The service the SOAP channels invoke
_service_name = 'enmasse.alerts.soap.service'

# The SOAP channels of the file - one moving a few settings away from their defaults, one carrying no mapping
_channel_name_1 = 'enmasse.alerts.soap.channel.1'
_channel_name_2 = 'enmasse.alerts.soap.channel.2'

_yaml_text = f"""
channel_soap:
  - name: {_channel_name_1}
    service: {_service_name}
    url_path: /enmasse/alerts/soap/channel/1
    soap_action: urn:orders
    soap_version: '1.1'
    alerts:
      max_latency: 2500
      auth_failures: 3
      traffic_expected: true
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: {_channel_name_2}
    service: {_service_name}
    url_path: /enmasse/alerts/soap/channel/2
    soap_action: urn:status
    soap_version: '1.2'
    is_audit_log_active: false
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
    """ A real ODB session over an in-memory SQLite database holding one cluster, the service
    the channels invoke and the SMTP and LLM connections the alerts mappings name.
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

    service = Service(None, _service_name, True, 'enmasse.alerts.soap.Service', False, cluster)
    session.add(service)

    smtp = SMTP()
    smtp.name = _smtp_name
    smtp.is_active = True
    smtp.host = 'smtp.example.com'
    smtp.port = 587
    smtp.timeout = 30
    smtp.is_debug = False
    smtp.mode = EMAIL.SMTP.MODE.STARTTLS
    smtp.ping_address = 'ping@example.com'
    smtp.cluster = cluster
    session.add(smtp)

    llm = GenericConn()
    llm.name = _llm_name
    llm.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
    llm.is_active = True
    llm.is_internal = False
    llm.is_channel = False
    llm.is_outconn = True
    llm.cluster = cluster
    session.add(llm)

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def soap_importer() -> 'ChannelSOAPImporter':
    out = ChannelSOAPImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def soap_exporter() -> 'ChannelSOAPExporter':
    out = ChannelSOAPExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################

def _opaque(channel:'any_') -> 'anydict':
    out = loads(channel.opaque1)
    return out

# ################################################################################################################################

def _by_name(items:'any_') -> 'anydict':
    out = {}

    for item in items:
        if isinstance(item, dict):
            out[item['name']] = item
        else:
            out[item.name] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelAlertsImport:

    def test_a_soap_channel_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)
        channel = _by_name(created)[_channel_name_1]

        opaque = _opaque(channel)

        assert opaque[storage_name('max_latency')] == 2500
        assert opaque[storage_name('auth_failures')] == 3
        assert opaque[storage_name('traffic_expected')] is True
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _llm_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('silence_window')] == 3600
        assert opaque[storage_name('silence_slots')] == '[]'
        assert opaque[storage_name('use_llm')] is True

        # The channel's own attributes are untouched and the mapping itself is not stored
        assert opaque['is_audit_log_active'] is True
        assert channel.soap_action == 'urn:orders'
        assert channel.soap_version == '1.1'
        assert Alerts_Key not in opaque
        assert not hasattr(channel, Alerts_Key)

# ################################################################################################################################

    def test_a_soap_channel_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)
        channel = _by_name(created)[_channel_name_2]

        opaque = _opaque(channel)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('auth_failures')] == 10
        assert opaque[storage_name('traffic_expected')] is False
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['is_audit_log_active'] is False

# ################################################################################################################################

    def test_a_soap_channel_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        created, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)
        assert len(created) == 2

        # The same file again changes nothing ..
        definitions = yaml.safe_load(_yaml_text)['channel_soap']
        created_again, updated = soap_importer.sync_channel_soap(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 0

        # .. and one with a smaller mapping updates the channel it belongs to.
        definitions = yaml.safe_load(_yaml_text)['channel_soap']
        definitions[0]['alerts'] = {'auth_failures': 3}

        created_again, updated = soap_importer.sync_channel_soap(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 1

        channel = _by_name(updated)[_channel_name_1]
        opaque = _opaque(channel)

        assert opaque[storage_name('auth_failures')] == 3
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('traffic_expected')] is False
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_missing_email_connection_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
    ) -> 'None':
        definitions = yaml_config['channel_soap']
        definitions[0]['alerts']['email_connection'] = 'smtp:enmasse.no.such.connection'

        with pytest.raises(Exception) as context:
            _ = soap_importer.sync_channel_soap(definitions, session)

        message = str(context.value)
        assert 'enmasse.no.such.connection' in message
        assert 'channel_soap' in message
        assert _channel_name_1 in message

        # Nothing was written
        stored = session.query(HTTPSOAP).filter_by(name=_channel_name_1).first()
        assert stored is None

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
        soap_exporter:'ChannelSOAPExporter',
    ) -> 'None':
        _, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)

        exported = soap_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_channel_name_1]

        expected = {
            'max_latency': 2500,
            'auth_failures': 3,
            'traffic_expected': True,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        assert item['soap_action'] == 'urn:orders'
        assert item['soap_version'] == '1.1'

        for key in item:
            assert not key.startswith('alert_')

        # A channel that moved nothing carries no alerts key
        item = _by_name(exported)[_channel_name_2]
        assert Alerts_Key not in item
        assert item['is_audit_log_active'] is False

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        soap_importer:'ChannelSOAPImporter',
        soap_exporter:'ChannelSOAPExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = soap_importer.sync_channel_soap(yaml_config['channel_soap'], session)
        exported = soap_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'channel_soap': exported})

        # The alerts mapping is the last field of a written channel
        written = path.read_text()
        assert "    soap_version: '1.1'\n    alerts:\n      max_latency: 2500\n" in written

        read_back = yaml.safe_load(written)
        assert read_back['channel_soap'] == exported

        # The same settings again change nothing
        _, updated = soap_importer.sync_channel_soap(read_back['channel_soap'], session)
        assert len(updated) == 0

# ################################################################################################################################
# ################################################################################################################################
