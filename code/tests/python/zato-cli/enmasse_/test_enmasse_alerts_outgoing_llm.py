# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing LLM connection's alerts mapping - the REST-like failure settings plus the LLM's own, imported into the alert_
# opaque keys of the llm type next to the connection's own fields, the settings left out taking the defaults, the codes
# travelling as the text they are typed as and a bad one refused, the two latencies in seconds taking fractions, the budget
# travelling as a plain count of tokens with its own window, a re-import of the same file storing the same settings, an update
# making the file the source of truth, and the export writing only what moved away from the defaults, last among the fields.

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
from zato.cli.enmasse.exporters.llm import LLMExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.llm import LLMImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, SecurityBase, SMTP
from zato.common.typing_ import cast_

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

_llm_type = GENERIC.CONNECTION.TYPE.OUTCONN_LLM

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email and LLM connections the alerts mappings name - the latter the one that explains, not the ones explained
_smtp_name = 'enmasse.alerts.llm.smtp'
_explainer_name = 'enmasse.alerts.llm.explainer'

# The connections of the file - one moving a few settings away from their defaults, one carrying no mapping
_conn_name_1 = 'enmasse.alerts.llm.conn.1'
_conn_name_2 = 'enmasse.alerts.llm.conn.2'

_address_1 = 'https://api.openai.com/v1'
_address_2 = 'http://ollama.internal:11434/v1'

_model_1 = 'gpt-4o'
_model_2 = 'llama3.1'

# The codes the first connection alerts on, its own rather than the default
_own_status_codes = '429, 5xx'
_default_status_codes = '429, 401, 403, 5xx'

# The latencies of the first connection, in seconds, one of them a fraction
_own_warning_latency = 7.5
_own_error_latency = 12

# The budget of the first connection, a plain count of tokens over an hour
_own_token_budget = 2000000
_own_token_budget_window = 3600

_yaml_text = f"""
llm:
  - name: {_conn_name_1}
    address: {_address_1}
    model: {_model_1}
    alerts:
      status_codes: '{_own_status_codes}'
      status_code_threshold: 5
      truncations: 5
      truncations_window: 600
      refusals: 2
      warning_latency: {_own_warning_latency}
      error_latency: {_own_error_latency}
      token_budget: {_own_token_budget}
      token_budget_window: {_own_token_budget_window}
      email_connection: smtp:{_smtp_name}
      llm_connection: {_explainer_name}

  - name: {_conn_name_2}
    address: {_address_2}
    model: {_model_2}
    max_tokens: 2048
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
        SecurityBase.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    smtp = cast_('any_', SMTP())
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

    explainer = cast_('any_', GenericConn())
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
def llm_importer() -> 'LLMImporter':
    out = LLMImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

@pytest.fixture
def llm_exporter() -> 'LLMExporter':
    out = LLMExporter(EnmasseYAMLExporter())
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
    out = session.query(GenericConn).filter_by(type_=_llm_type, name=name).first()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingLLMAlertsImport:

    def test_a_connection_stores_every_alert_setting_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
    ) -> 'None':
        created, _ = llm_importer.sync_definitions(yaml_config['llm'], session)
        connection = _by_name(created)[_conn_name_1]

        opaque = _opaque(connection)

        # The codes are stored as the text they were typed as, the latencies in seconds, the budget as a plain count
        assert opaque[storage_name('status_codes')] == _own_status_codes
        assert opaque[storage_name('status_code_threshold')] == 5
        assert opaque[storage_name('truncations')] == 5
        assert opaque[storage_name('truncations_window')] == 600
        assert opaque[storage_name('refusals')] == 2
        assert opaque[storage_name('warning_latency')] == _own_warning_latency
        assert opaque[storage_name('error_latency')] == _own_error_latency
        assert opaque[storage_name('token_budget')] == _own_token_budget
        assert opaque[storage_name('token_budget_window')] == _own_token_budget_window
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _explainer_name

        # What the mapping left out is at its default
        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('status_codes_window')] == 300
        assert opaque[storage_name('connection_failures')] == 3
        assert opaque[storage_name('connection_failures_window')] == 300
        assert opaque[storage_name('refusals_window')] == 300
        assert opaque[storage_name('latency_window')] == 300
        assert opaque[storage_name('use_llm')] is True

        # Neither a channel's settings, nor the REST latency, nor another connection's codes ever land on an LLM one
        assert storage_name('max_latency') not in opaque
        assert storage_name('auth_failures') not in opaque
        assert storage_name('silence_slots') not in opaque
        assert storage_name('fault_codes') not in opaque
        assert storage_name('outcome_codes') not in opaque

        # The connection's own attributes are untouched and the mapping itself is not stored
        assert opaque['model'] == _model_1
        assert connection.address == _address_1
        assert connection.type_ == _llm_type
        assert Alerts_Key not in opaque
        assert not hasattr(connection, Alerts_Key)

# ################################################################################################################################

    def test_a_connection_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
    ) -> 'None':
        created, _ = llm_importer.sync_definitions(yaml_config['llm'], session)
        connection = _by_name(created)[_conn_name_2]

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('status_codes')] == _default_status_codes
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('truncations')] == 3
        assert opaque[storage_name('truncations_window')] == 300
        assert opaque[storage_name('refusals')] == 3
        assert opaque[storage_name('refusals_window')] == 300
        assert opaque[storage_name('warning_latency')] == 10
        assert opaque[storage_name('error_latency')] == 15
        assert opaque[storage_name('token_budget')] == 10000000
        assert opaque[storage_name('token_budget_window')] == 86400
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque['model'] == _model_2
        assert opaque['max_tokens'] == 2048

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
    ) -> 'None':
        created, _ = llm_importer.sync_definitions(yaml_config['llm'], session)
        assert len(created) == 2

        # The same file again writes the same settings - a generic connection is rewritten from its file on every import ..
        definitions = yaml.safe_load(_yaml_text)['llm']
        created_again, updated = llm_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 2

        opaque = _opaque(_by_name(updated)[_conn_name_1])
        assert opaque[storage_name('token_budget')] == _own_token_budget
        assert opaque[storage_name('warning_latency')] == _own_warning_latency

        # .. and one with a smaller mapping updates the connection it belongs to.
        definitions = yaml.safe_load(_yaml_text)['llm']
        definitions[0]['alerts'] = {'refusals': 2}

        created_again, updated = llm_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0

        connection = _by_name(updated)[_conn_name_1]
        opaque = _opaque(connection)

        assert opaque[storage_name('refusals')] == 2
        assert opaque[storage_name('status_codes')] == _default_status_codes
        assert opaque[storage_name('status_code_threshold')] == 3
        assert opaque[storage_name('truncations')] == 3
        assert opaque[storage_name('warning_latency')] == 10
        assert opaque[storage_name('error_latency')] == 15
        assert opaque[storage_name('token_budget')] == 10000000
        assert opaque[storage_name('token_budget_window')] == 86400
        assert opaque[storage_name('email_connection')] == ''
        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_a_bad_status_code_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
    ) -> 'None':
        definitions = yaml_config['llm']
        definitions[0]['alerts']['status_codes'] = '429, 6xx'

        with pytest.raises(Exception) as context:
            _ = llm_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert '6xx' in message
        assert _conn_name_1 in message

        # Nothing was written
        assert _stored(session, _conn_name_1) is None

# ################################################################################################################################

    def test_a_soap_fault_code_is_not_a_status_code(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
    ) -> 'None':
        definitions = yaml_config['llm']
        definitions[0]['alerts']['status_codes'] = 'Receiver'

        with pytest.raises(Exception) as context:
            _ = llm_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'Receiver' in message
        assert _conn_name_1 in message

        assert _stored(session, _conn_name_1) is None

# ################################################################################################################################

    def test_another_connections_setting_is_rejected_on_an_llm_one(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
    ) -> 'None':

        # The REST latency gave way to the two of the LLM ..
        definitions = yaml_config['llm']
        definitions[0]['alerts']['max_latency'] = 2500

        with pytest.raises(Exception) as context:
            _ = llm_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'max_latency' in message
        assert _conn_name_1 in message

        # .. and a FHIR connection's outcomes never belonged to it.
        definitions = yaml.safe_load(_yaml_text)['llm']
        definitions[0]['alerts']['outcome_codes'] = 'exception'

        with pytest.raises(Exception) as context:
            _ = llm_importer.sync_definitions(definitions, session)

        assert 'outcome_codes' in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingLLMAlertsExport:

    def test_only_the_settings_moved_away_from_their_defaults_are_written(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
        llm_exporter:'LLMExporter',
    ) -> 'None':
        _, _ = llm_importer.sync_definitions(yaml_config['llm'], session)

        exported = llm_exporter.export(session, _cluster_id)
        item = _by_name(exported)[_conn_name_1]

        expected = {
            'status_codes': _own_status_codes,
            'status_code_threshold': 5,
            'truncations': 5,
            'truncations_window': 600,
            'refusals': 2,
            'warning_latency': _own_warning_latency,
            'error_latency': _own_error_latency,
            'token_budget': _own_token_budget,
            'token_budget_window': _own_token_budget_window,
            'email_connection': f'smtp:{_smtp_name}',
            'llm_connection': _explainer_name,
        }

        assert item[Alerts_Key] == expected
        assert list(item[Alerts_Key]) == list(expected)

        # The mapping is the last of the fields and no storage name leaks into the file
        assert list(item)[-1] == Alerts_Key

        for key in item:
            assert not key.startswith('alert_')

        # A connection that moved nothing carries no alerts key, only what is its own
        item = _by_name(exported)[_conn_name_2]
        assert Alerts_Key not in item
        assert item['model'] == _model_2
        assert item['max_tokens'] == 2048

        # The one that explains, created with no settings at all, carries no mapping either
        item = _by_name(exported)[_explainer_name]
        assert Alerts_Key not in item

# ################################################################################################################################

    def test_the_export_round_trips_through_the_writer(
        self,
        yaml_config:'stranydict',
        session:'any_',
        llm_importer:'LLMImporter',
        llm_exporter:'LLMExporter',
        tmp_path:'Path',
    ) -> 'None':
        _, _ = llm_importer.sync_definitions(yaml_config['llm'], session)
        exported = llm_exporter.export(session, _cluster_id)

        path = tmp_path / 'enmasse.yaml'
        FileWriter(str(path)).write({'llm': exported})

        # The alerts mapping is the last field of a written connection, the codes quoted as the text they are,
        # the fraction of a second and the plain count of tokens as the numbers they are
        written = path.read_text()
        assert f"    alerts:\n      status_codes: '{_own_status_codes}'\n      status_code_threshold: 5\n" in written
        assert f'      warning_latency: {_own_warning_latency}\n      error_latency: {_own_error_latency}\n' in written
        assert f'      token_budget: {_own_token_budget}\n      token_budget_window: {_own_token_budget_window}\n' in written

        read_back = yaml.safe_load(written)
        assert read_back['llm'] == exported

        # The same settings again store the same settings and export the same file
        _, _ = llm_importer.sync_definitions(read_back['llm'], session)
        assert llm_exporter.export(session, _cluster_id) == exported

# ################################################################################################################################
# ################################################################################################################################
