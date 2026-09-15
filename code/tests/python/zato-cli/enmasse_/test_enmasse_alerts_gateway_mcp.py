# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An MCP gateway's alerts mapping - the core failure settings plus the gateway's own, imported into the alert_ opaque keys
# of the mcp type next to the gateway's own fields, the settings left out taking the defaults, the two latencies in seconds
# taking fractions, the volume budget travelling as a plain count of bytes with its own window, the tool count with no
# window at all, a negative number refused before anything is written, a re-import of the same file storing the same
# settings, an update making the file the source of truth, and the export writing only what moved away from the defaults,
# last among the fields.

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
from zato.cli.enmasse.exporters.mcp import GatewayMCPExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import CONNECTION, EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, HTTPSOAP, SecurityBase, Service, \
    SMTP

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

_mcp_type = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
_llm_type = GENERIC.CONNECTION.TYPE.OUTCONN_LLM

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name
_smtp_name = 'enmasse.alerts.mcp.smtp'
_explainer_name = 'enmasse.alerts.mcp.explainer'

# The gateways of the file - one moving a few settings away from their defaults, one carrying no mapping
_gateway_name_1 = 'enmasse.alerts.mcp.gateway.1'
_gateway_name_2 = 'enmasse.alerts.mcp.gateway.2'

_url_path_1 = '/mcp/enmasse-alerts-1'
_url_path_2 = '/mcp/enmasse-alerts-2'

_services_1 = ['orders.get', 'orders.list']

# The latencies of the first gateway, in seconds, one of them a fraction
_own_warning_latency = 7.5
_own_error_latency = 12

# The budget of the first gateway, a plain count of bytes over an hour
_own_volume_budget = 2000000000
_own_volume_budget_window = 3600

# The tool count of the first gateway
_own_max_tools = 30

# The one setting of its own the second gateway moves, in seconds
_own_session_ttl = 1800

_yaml_text = f"""
mcp_gateway:
  - name: {_gateway_name_1}
    url_path: {_url_path_1}
    services:
      - {_services_1[0]}
      - {_services_1[1]}
    alerts:
      invalid_calls: 2
      invalid_calls_window: 600
      rejections: 4
      repeat_calls: 30
      warning_latency: {_own_warning_latency}
      error_latency: {_own_error_latency}
      volume_budget: {_own_volume_budget}
      volume_budget_window: {_own_volume_budget_window}
      traffic_expected: true
      max_tools: {_own_max_tools}
      email_connection: smtp:{_smtp_name}
      llm_connection: {_explainer_name}

  - name: {_gateway_name_2}
    url_path: {_url_path_2}
    session_ttl: {_own_session_ttl}
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
    """ A real ODB session over an in-memory SQLite database holding one cluster, the SMTP and LLM connections
    the alerts mappings name, and the tables the REST channel every gateway rides on is created in.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        GenericObject.__table__,
        SMTP.__table__,
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

    explainer = GenericConn()
    explainer.name = _explainer_name
    explainer.type_ = _llm_type
    explainer.is_active = True
    explainer.is_internal = False
    explainer.is_channel = False
    explainer.is_outconn = True
    explainer.address = 'http://ollama.internal:11434/v1'
    explainer.opaque1 = '{"model": "llama3.1"}'
    explainer.cluster = cluster
    session.add(explainer)

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def mcp_importer() -> 'GatewayMCPImporter':
    out = GatewayMCPImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def mcp_exporter() -> 'GatewayMCPExporter':
    out = GatewayMCPExporter(EnmasseYAMLExporter())
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
    out = session.query(GenericConn).filter_by(type_=_mcp_type, name=name).first()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayMCPAlertsImport:

    def test_a_gateway_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
    ) -> 'None':
        created, _ = mcp_importer.sync_definitions(yaml_config['mcp_gateway'], session)
        gateway = _by_name(created)[_gateway_name_1]

        opaque = _opaque(gateway)

        # The counts are stored as they were typed, the latencies in seconds, the budget as a plain count of bytes
        assert opaque[storage_name('invalid_calls')] == 2
        assert opaque[storage_name('invalid_calls_window')] == 600
        assert opaque[storage_name('rejections')] == 4
        assert opaque[storage_name('repeat_calls')] == 30
        assert opaque[storage_name('warning_latency')] == _own_warning_latency
        assert opaque[storage_name('error_latency')] == _own_error_latency
        assert opaque[storage_name('volume_budget')] == _own_volume_budget
        assert opaque[storage_name('volume_budget_window')] == _own_volume_budget_window
        assert opaque[storage_name('traffic_expected')] is True
        assert opaque[storage_name('max_tools')] == _own_max_tools
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _explainer_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('rejections_window')] == 300
        assert opaque[storage_name('auth_failures')] == 10
        assert opaque[storage_name('throttled_calls')] == 10
        assert opaque[storage_name('repeat_calls_window')] == 300
        assert opaque[storage_name('latency_window')] == 300
        assert opaque[storage_name('truncations')] == 5
        assert opaque[storage_name('silence_window')] == 3600
        assert opaque[storage_name('use_llm')] is True

        # Neither an outgoing connection's settings nor another channel's ever land on a gateway
        assert storage_name('status_codes') not in opaque
        assert storage_name('connection_failures') not in opaque
        assert storage_name('token_budget') not in opaque
        assert storage_name('refusals') not in opaque
        assert storage_name('max_latency') not in opaque
        assert storage_name('ack_codes') not in opaque

        # The gateway's own attributes are untouched and the mapping itself is not stored
        assert opaque['url_path'] == _url_path_1
        assert opaque['services'] == _services_1
        assert gateway.type_ == _mcp_type
        assert Alerts_Key not in opaque
        assert not hasattr(gateway, Alerts_Key)

        # The REST channel the gateway rides on is there as before
        channel = session.query(HTTPSOAP).filter_by(name=_gateway_name_1, connection=CONNECTION.CHANNEL).one()
        assert channel.url_path == _url_path_1

# ################################################################################################################################

    def test_a_gateway_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
    ) -> 'None':
        created, _ = mcp_importer.sync_definitions(yaml_config['mcp_gateway'], session)
        gateway = _by_name(created)[_gateway_name_2]

        opaque = _opaque(gateway)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('invalid_calls')] == 5
        assert opaque[storage_name('invalid_calls_window')] == 300
        assert opaque[storage_name('rejections')] == 3
        assert opaque[storage_name('auth_failures')] == 10
        assert opaque[storage_name('throttled_calls')] == 10
        assert opaque[storage_name('repeat_calls')] == 20
        assert opaque[storage_name('warning_latency')] == 5
        assert opaque[storage_name('error_latency')] == 15
        assert opaque[storage_name('truncations')] == 5
        assert opaque[storage_name('volume_budget')] == 100000000
        assert opaque[storage_name('volume_budget_window')] == 86400
        assert opaque[storage_name('traffic_expected')] is False
        assert opaque[storage_name('max_tools')] == 25
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['url_path'] == _url_path_2
        assert opaque['session_ttl'] == _own_session_ttl

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
    ) -> 'None':
        created, _ = mcp_importer.sync_definitions(yaml_config['mcp_gateway'], session)
        assert len(created) == 2

        # The same file again writes the same settings - a generic connection is rewritten from its file on every import ..
        definitions = yaml.safe_load(_yaml_text)['mcp_gateway']
        created_again, updated = mcp_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 2

        opaque = _opaque(_by_name(updated)[_gateway_name_1])
        assert opaque[storage_name('volume_budget')] == _own_volume_budget
        assert opaque[storage_name('max_tools')] == _own_max_tools

        # .. and one with a smaller mapping updates the gateway it belongs to.
        definitions = yaml.safe_load(_yaml_text)['mcp_gateway']
        definitions[0]['alerts'] = {'repeat_calls': 50}

        created_again, updated = mcp_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        gateway = _by_name(updated)[_gateway_name_1]
        opaque = _opaque(gateway)

        assert opaque[storage_name('repeat_calls')] == 50
        assert opaque[storage_name('invalid_calls')] == 5
        assert opaque[storage_name('rejections')] == 3
        assert opaque[storage_name('warning_latency')] == 5
        assert opaque[storage_name('error_latency')] == 15
        assert opaque[storage_name('volume_budget')] == 100000000
        assert opaque[storage_name('volume_budget_window')] == 86400
        assert opaque[storage_name('traffic_expected')] is False
        assert opaque[storage_name('max_tools')] == 25
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_negative_number_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
    ) -> 'None':
        definitions = yaml_config['mcp_gateway']
        definitions[0]['alerts']['max_tools'] = -1

        with pytest.raises(Exception) as context:
            _ = mcp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'max_tools' in message
        assert _gateway_name_1 in message

        # Nothing was written
        assert _stored(session, _gateway_name_1) is None

# ################################################################################################################################

    def test_a_budget_that_is_not_a_number_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
    ) -> 'None':
        definitions = yaml_config['mcp_gateway']
        definitions[0]['alerts']['volume_budget'] = 'lots'

        with pytest.raises(Exception) as context:
            _ = mcp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'volume_budget' in message
        assert _gateway_name_1 in message

        assert _stored(session, _gateway_name_1) is None

# ################################################################################################################################

    def test_another_connections_setting_is_rejected_on_a_gateway(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
    ) -> 'None':

        # An outgoing connection's codes never belonged to a gateway ..
        definitions = yaml_config['mcp_gateway']
        definitions[0]['alerts']['status_codes'] = '5xx'

        with pytest.raises(Exception) as context:
            _ = mcp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'status_codes' in message
        assert _gateway_name_1 in message

        # .. and neither did an LLM connection's token budget.
        definitions = yaml.safe_load(_yaml_text)['mcp_gateway']
        definitions[0]['alerts']['token_budget'] = 1000000

        with pytest.raises(Exception) as context:
            _ = mcp_importer.sync_definitions(definitions, session)

        assert 'token_budget' in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestGatewayMCPAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
        mcp_exporter:'GatewayMCPExporter',
    ) -> 'None':
        _, _ = mcp_importer.sync_definitions(yaml_config['mcp_gateway'], session)

        exported = mcp_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_gateway_name_1]

        expected = {
            'invalid_calls': 2,
            'invalid_calls_window': 600,
            'rejections': 4,
            'repeat_calls': 30,
            'warning_latency': _own_warning_latency,
            'error_latency': _own_error_latency,
            'volume_budget': _own_volume_budget,
            'volume_budget_window': _own_volume_budget_window,
            'traffic_expected': True,
            'max_tools': _own_max_tools,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _explainer_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        # The mapping is the last of the fields and no storage name leaks into the file
        assert list(item)[-1] == Alerts_Key

        for key in item:
            assert not key.startswith('alert_')

        # The gateway's own fields are there next to it
        assert item['url_path'] == _url_path_1
        assert item['services'] == _services_1

        # A gateway that moved nothing carries no alerts key, only what is its own
        item = _by_name(exported)[_gateway_name_2]
        assert Alerts_Key not in item
        assert item['url_path'] == _url_path_2
        assert item['session_ttl'] == _own_session_ttl

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mcp_importer:'GatewayMCPImporter',
        mcp_exporter:'GatewayMCPExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = mcp_importer.sync_definitions(yaml_config['mcp_gateway'], session)
        exported = mcp_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'mcp_gateway': exported})

        # The alerts mapping is the last field of a written gateway, the fraction of a second, the plain count
        # of bytes and the tool count as the numbers they are
        written = path.read_text()
        assert '    alerts:\n      invalid_calls: 2\n      invalid_calls_window: 600\n' in written
        assert f'      warning_latency: {_own_warning_latency}\n      error_latency: {_own_error_latency}\n' in written
        assert f'      volume_budget: {_own_volume_budget}\n      volume_budget_window: {_own_volume_budget_window}\n' in written
        assert f'      max_tools: {_own_max_tools}\n' in written

        read_back = yaml.safe_load(written)
        assert read_back['mcp_gateway'] == exported

        # The same settings again store the same settings and export the same file
        _, _ = mcp_importer.sync_definitions(read_back['mcp_gateway'], session)
        assert mcp_exporter.export(session, _cluster_id) == exported

# ################################################################################################################################
# ################################################################################################################################
