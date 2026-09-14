# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An MLLP channel's alerts mapping - the channel settings minus everything HTTP plus the acknowledgment codes, imported
# into the alert_ opaque keys of the mllp_channel type next to the channel's own fields, the settings left out taking the
# defaults, the codes travelling as the text they are typed as and a bad one refused, an HTTP setting refused, an update
# making the file the source of truth, and the export writing only what moved away from the defaults, last among the
# channel's fields.

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
from zato.cli.enmasse.exporters.channel_mllp import ChannelMLLPExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_mllp import ChannelMLLPImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, SecurityBase, Service, SMTP

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

_mllp_type = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name
_smtp_name = 'enmasse.alerts.mllp.smtp'
_llm_name = 'enmasse.alerts.mllp.llm'

# The channels of the file - one moving a few settings away from their defaults, one carrying no mapping
_channel_name_1 = 'enmasse.alerts.mllp.channel.1'
_channel_name_2 = 'enmasse.alerts.mllp.channel.2'

_service_name = 'demo.ping'

# The codes the first channel alerts on, its own rather than the default
_own_ack_codes = 'AR, CR'
_default_ack_codes = 'AE, AR, CE, CR'

_yaml_text = f"""
channel_mllp:
  - name: {_channel_name_1}
    service: {_service_name}
    msh9_message_type: ADT
    alerts:
      ack_codes: '{_own_ack_codes}'
      ack_threshold: 5
      acks_window: 600
      consecutive_failures: 2
      traffic_expected: true
      silence_window: 900
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: {_channel_name_2}
    service: {_service_name}
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
    """ A real ODB session over an in-memory SQLite database holding one cluster and the SMTP and LLM connections
    the alerts mappings name.
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
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

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
def mllp_importer() -> 'ChannelMLLPImporter':
    out = ChannelMLLPImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def mllp_exporter() -> 'ChannelMLLPExporter':
    out = ChannelMLLPExporter(EnmasseYAMLExporter())
    return out

# ################################################################################################################################

def _opaque(connection:'any_') -> 'anydict':
    out = loads(connection.opaque1)
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

def _stored(session:'any_', name:'str') -> 'any_':
    out = session.query(GenericConn).filter_by(type_=_mllp_type, name=name).first()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestChannelMLLPAlertsImport:

    def test_a_channel_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'ChannelMLLPImporter',
    ) -> 'None':
        created, _ = mllp_importer.sync_definitions(yaml_config['channel_mllp'], session)
        connection = _by_name(created)[_channel_name_1]

        opaque = _opaque(connection)

        # The codes are stored as the text they were typed as
        assert opaque[storage_name('ack_codes')] == _own_ack_codes
        assert opaque[storage_name('ack_threshold')] == 5
        assert opaque[storage_name('acks_window')] == 600
        assert opaque[storage_name('consecutive_failures')] == 2
        assert opaque[storage_name('traffic_expected')] is True
        assert opaque[storage_name('silence_window')] == 900
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _llm_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('error_rate')] == 10
        assert opaque[storage_name('window')] == 300
        assert opaque[storage_name('max_latency')] == 5000
        assert opaque[storage_name('latency_window')] == 300
        assert opaque[storage_name('silence_slots')] == '[]'
        assert opaque[storage_name('use_llm')] is True

        # Nothing HTTP ever lands on an MLLP channel, nor the codes of the outgoing kinds
        assert storage_name('auth_failures') not in opaque
        assert storage_name('client_errors') not in opaque
        assert storage_name('server_error_rate') not in opaque
        assert storage_name('fault_codes') not in opaque
        assert storage_name('outcome_codes') not in opaque
        assert storage_name('status_codes') not in opaque

        # The channel's own attributes are untouched and the mapping itself is not stored
        assert opaque['service'] == _service_name
        assert opaque['msh9_message_type'] == 'ADT'
        assert opaque['is_audit_log_active'] is True
        assert connection.type_ == _mllp_type
        assert Alerts_Key not in opaque
        assert not hasattr(connection, Alerts_Key)

# ################################################################################################################################

    def test_a_channel_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'ChannelMLLPImporter',
    ) -> 'None':
        created, _ = mllp_importer.sync_definitions(yaml_config['channel_mllp'], session)
        connection = _by_name(created)[_channel_name_2]

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('ack_codes')] == _default_ack_codes
        assert opaque[storage_name('ack_threshold')] == 3
        assert opaque[storage_name('acks_window')] == 300
        assert opaque[storage_name('traffic_expected')] is False
        assert opaque[storage_name('silence_window')] == 3600
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['is_audit_log_active'] is False

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'ChannelMLLPImporter',
    ) -> 'None':
        created, _ = mllp_importer.sync_definitions(yaml_config['channel_mllp'], session)
        assert len(created) == 2

        # The same file again writes the same settings - a generic connection is rewritten from its file on every import ..
        definitions = yaml.safe_load(_yaml_text)['channel_mllp']
        created_again, updated = mllp_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 2

        opaque = _opaque(_by_name(updated)[_channel_name_1])
        assert opaque[storage_name('ack_codes')] == _own_ack_codes
        assert opaque[storage_name('ack_threshold')] == 5

        # .. and one with a smaller mapping updates the channel it belongs to.
        definitions = yaml.safe_load(_yaml_text)['channel_mllp']
        definitions[0]['alerts'] = {'consecutive_failures': 2}

        created_again, updated = mllp_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_channel_name_1]
        opaque = _opaque(connection)

        assert opaque[storage_name('consecutive_failures')] == 2
        assert opaque[storage_name('ack_codes')] == _default_ack_codes
        assert opaque[storage_name('ack_threshold')] == 3
        assert opaque[storage_name('acks_window')] == 300
        assert opaque[storage_name('traffic_expected')] is False
        assert opaque[storage_name('silence_window')] == 3600
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_bad_ack_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'ChannelMLLPImporter',
    ) -> 'None':
        definitions = yaml_config['channel_mllp']

        # A positive acknowledgment is never alerted on
        definitions[0]['alerts']['ack_codes'] = 'AR, AA'

        with pytest.raises(Exception) as context:
            _ = mllp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'AA' in message
        assert _channel_name_1 in message

        # Nothing was written
        assert _stored(session, _channel_name_1) is None

# ################################################################################################################################

    def test_an_http_setting_is_rejected_on_an_mllp_channel(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'ChannelMLLPImporter',
    ) -> 'None':
        definitions = yaml_config['channel_mllp']
        definitions[0]['alerts']['auth_failures'] = 5

        with pytest.raises(Exception) as context:
            _ = mllp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'auth_failures' in message
        assert _channel_name_1 in message

# ################################################################################################################################
# ################################################################################################################################

class TestChannelMLLPAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'ChannelMLLPImporter',
        mllp_exporter:'ChannelMLLPExporter',
    ) -> 'None':
        _, _ = mllp_importer.sync_definitions(yaml_config['channel_mllp'], session)

        exported = mllp_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_channel_name_1]

        expected = {
            'consecutive_failures': 2,
            'ack_codes': _own_ack_codes,
            'ack_threshold': 5,
            'acks_window': 600,
            'traffic_expected': True,
            'silence_window': 900,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _llm_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        # The mapping is the last of the fields and no alert_ key leaks out on its own
        assert item['service'] == _service_name
        assert item['msh9_message_type'] == 'ADT'
        assert list(item)[-1] == Alerts_Key

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
        mllp_importer:'ChannelMLLPImporter',
        mllp_exporter:'ChannelMLLPExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = mllp_importer.sync_definitions(yaml_config['channel_mllp'], session)
        exported = mllp_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'channel_mllp': exported})

        # The alerts mapping is the last field of a written channel, the codes quoted as the text they are
        written = path.read_text()
        assert f"    alerts:\n      consecutive_failures: 2\n      ack_codes: '{_own_ack_codes}'\n      ack_threshold: 5\n" in written

        read_back = yaml.safe_load(written)
        assert read_back['channel_mllp'] == exported

        # The same settings again store the same settings and export the same file
        _, _ = mllp_importer.sync_definitions(read_back['channel_mllp'], session)
        assert mllp_exporter.export(session, _cluster_id) == exported

# ################################################################################################################################
# ################################################################################################################################
