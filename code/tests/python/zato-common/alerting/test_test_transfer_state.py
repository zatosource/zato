# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path
from typing import Generator

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.alerting.config_store import apply_type_config, get_type_definition
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.api import Alerting
from zato.common.odb.model import Base, Cluster, IntervalBasedJob, Job, Service
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.util.scheduler import ensure_test_transfer_job_exists, set_job_active

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

engine_generator:TypeAlias = Generator[Engine, None, None]

# ################################################################################################################################
# ################################################################################################################################

# Who the test says made the changes
_actor = 'test-test-transfer-state'

# The cluster the test jobs belong to
_cluster_id = 1

# The rule the test transfers checkbox flips
_test_transfer_full_name = 'alerts_file_transfer_Test_Transfer_Failing'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def odb_session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding
    the scheduler tables and one cluster.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        Service.__table__,
        Job.__table__,
        IntervalBasedJob.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def backend(tmp_path:'Path') -> 'RuleSQLBackend':
    """ Returns the complete rule backend over an isolated test database, with
    the default alerting definitions already seeded and live.
    """
    database_path = tmp_path / 'rule-engine.sqlite'
    database_url = f'sqlite:///{database_path}'
    connection_options = {'check_same_thread': False}
    engine = create_database_engine(database_url, connect_args=connection_options)

    create_schema(engine)

    out = RuleSQLBackend.from_engine(engine)
    ensure_alerting_definitions(out)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_test_transfer_job(session:'any_') -> 'Job':
    out = session.query(Job).\
        filter(Job.name==Alerting.Test_Transfer_Job_Name).\
        filter(Job.cluster_id==_cluster_id).\
        one()
    return out

# ################################################################################################################################

def _get_test_transfer_rule_state(backend:'RuleSQLBackend') -> 'bool':
    definition = get_type_definition(backend, 'file_transfer')
    document = deserialize_document(definition.document)
    rule_document = document[Documents_Key][_test_transfer_full_name]

    out = rule_document.get('is_active') is not False
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTransferJobState:

    def test_the_test_transfer_job_ships_inactive(self, odb_session:'any_') -> 'None':

        created = ensure_test_transfer_job_exists(odb_session, _cluster_id)
        odb_session.commit()
        assert created is True

        job = _get_test_transfer_job(odb_session)
        assert job.is_active is False

# ################################################################################################################################

    def test_the_job_row_follows_the_checkbox_in_either_direction(self, odb_session:'any_') -> 'None':

        _ = ensure_test_transfer_job_exists(odb_session, _cluster_id)
        odb_session.commit()

        # On - the way the service flips it when the checkbox is checked
        changed = set_job_active(odb_session, _cluster_id, Alerting.Test_Transfer_Job_Name, True)
        odb_session.commit()
        assert changed is True
        assert _get_test_transfer_job(odb_session).is_active is True

        # Off again
        changed = set_job_active(odb_session, _cluster_id, Alerting.Test_Transfer_Job_Name, False)
        odb_session.commit()
        assert changed is True
        assert _get_test_transfer_job(odb_session).is_active is False

# ################################################################################################################################

    def test_a_flip_to_the_same_state_changes_nothing(self, odb_session:'any_') -> 'None':

        _ = ensure_test_transfer_job_exists(odb_session, _cluster_id)
        odb_session.commit()

        # The job already ships inactive, so another off is a no-op
        changed = set_job_active(odb_session, _cluster_id, Alerting.Test_Transfer_Job_Name, False)
        odb_session.commit()
        assert changed is False

# ################################################################################################################################
# ################################################################################################################################

class TestTransferRuleAndJobTogether:

    def test_the_rule_and_the_job_both_follow_the_checkbox(
        self,
        odb_session:'any_',
        backend:'RuleSQLBackend',
    ) -> 'None':

        _ = ensure_test_transfer_job_exists(odb_session, _cluster_id)
        odb_session.commit()

        # Both ship off - the test transfer writes to remote systems, so both are the opt-in
        assert _get_test_transfer_rule_state(backend) is False
        assert _get_test_transfer_job(odb_session).is_active is False

        # The checkbox goes on - the save path flips the rule, the service flips the job
        changed = apply_type_config(backend, 'file_transfer', actor=_actor, values={'test_transfers': True})
        assert changed is True

        _ = set_job_active(odb_session, _cluster_id, Alerting.Test_Transfer_Job_Name, True)
        odb_session.commit()

        assert _get_test_transfer_rule_state(backend) is True
        assert _get_test_transfer_job(odb_session).is_active is True

        # And off again, through the same pair of flips
        changed = apply_type_config(backend, 'file_transfer', actor=_actor, values={'test_transfers': False})
        assert changed is True

        _ = set_job_active(odb_session, _cluster_id, Alerting.Test_Transfer_Job_Name, False)
        odb_session.commit()

        assert _get_test_transfer_rule_state(backend) is False
        assert _get_test_transfer_job(odb_session).is_active is False

# ################################################################################################################################

    def test_the_health_alerts_toggle_flips_both_microsoft_health_rules(self, backend:'RuleSQLBackend') -> 'None':

        # Off - both health rules go inactive in one save
        changed = apply_type_config(backend, 'microsoft', actor=_actor, values={'health_alerts': False})
        assert changed is True

        definition = get_type_definition(backend, 'microsoft')
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        for rule_name in ('Service_Degraded', 'Service_Interrupted'):
            rule_document = documents[f'alerts_microsoft_{rule_name}']
            assert rule_document['is_active'] is False, rule_name

        # The other rules of the type stay as they were
        down_rule = documents['alerts_microsoft_Connection_Down']
        assert down_rule.get('is_active') is not False

        # And on again
        changed = apply_type_config(backend, 'microsoft', actor=_actor, values={'health_alerts': True})
        assert changed is True

        definition = get_type_definition(backend, 'microsoft')
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        for rule_name in ('Service_Degraded', 'Service_Interrupted'):
            rule_document = documents[f'alerts_microsoft_{rule_name}']
            assert rule_document['is_active'] is True, rule_name

# ################################################################################################################################
# ################################################################################################################################
