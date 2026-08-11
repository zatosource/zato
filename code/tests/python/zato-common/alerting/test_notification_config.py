# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.notification_config import notification_keys, parse_extra, read_notification_config, \
    set_notification_config
from zato.common.api import Alerting
from zato.common.odb.model import Base, Cluster, IntervalBasedJob, Job, Service
from zato.common.util.scheduler import ensure_alerting_job_exists

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The cluster the test job belongs to
_cluster_id = 1

# What the tests configure the notifications with
_values = {
    Alerting.Extra_Slack_Webhook:    'https://hooks.slack.example.com/services/T000/B000/XXX',
    Alerting.Extra_Teams_Webhook:    'https://example.webhook.office.com/webhookb2/abc',
    Alerting.Extra_Webhook_URL:      'https://example.atlassian.net/automation/webhooks/abc',
    Alerting.Extra_Email_Connection: 'My SMTP Connection',
    Alerting.Extra_Default_To:       'ops@example.com, oncall@example.com',
    Alerting.Extra_From:             'alerts@example.com',
    Alerting.Extra_Dashboard_URL:    'https://dashboard.example.com',
}

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def odb_session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding
    the scheduler tables, one cluster and the alerting sweep job.
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

    _ = ensure_alerting_job_exists(session, _cluster_id)
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################
# ################################################################################################################################

def _get_sweep_job(session:'any_') -> 'Job':
    out = session.query(Job).\
        filter(Job.name==Alerting.Job_Name).\
        filter(Job.cluster_id==_cluster_id).\
        one()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseExtra:

    def test_bytes_text_and_nothing_all_parse(self) -> 'None':

        assert parse_extra(b'{"from": "a@example.com"}') == {'from': 'a@example.com'}
        assert parse_extra('{"from": "a@example.com"}') == {'from': 'a@example.com'}
        assert parse_extra('') == {}
        assert parse_extra(None) == {}

# ################################################################################################################################

    def test_free_text_that_is_not_json_means_nothing_configured(self) -> 'None':

        # The extra column is user-editable free text, so anything goes into it
        assert parse_extra('not json at all') == {}
        assert parse_extra('["a", "list"]') == {}

# ################################################################################################################################
# ################################################################################################################################

class TestReadNotificationConfig:

    def test_a_job_without_an_extra_reads_as_all_empty(self, odb_session:'any_') -> 'None':

        job = _get_sweep_job(odb_session)
        values = read_notification_config(job.extra)

        assert sorted(values) == sorted(notification_keys)

        for key in notification_keys:
            assert values[key] == '', key

# ################################################################################################################################

    def test_what_was_set_is_what_is_read(self, odb_session:'any_') -> 'None':

        changed = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()
        assert changed is True

        job = _get_sweep_job(odb_session)
        values = read_notification_config(job.extra)

        assert values == _values

# ################################################################################################################################
# ################################################################################################################################

class TestSetNotificationConfig:

    def test_unrelated_extra_keys_survive_a_save(self, odb_session:'any_') -> 'None':

        # The extra already carries a key that is not ours to touch
        job = _get_sweep_job(odb_session)
        job.extra = json.dumps({'unrelated': 'stays'})
        odb_session.add(job)
        odb_session.commit()

        _ = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()

        parsed = parse_extra(_get_sweep_job(odb_session).extra)

        assert parsed['unrelated'] == 'stays'
        assert parsed[Alerting.Extra_From] == _values[Alerting.Extra_From]

# ################################################################################################################################

    def test_an_empty_value_removes_its_key(self, odb_session:'any_') -> 'None':

        _ = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()

        # The Slack webhook is cleared on screen and saved
        cleared = dict(_values)
        cleared[Alerting.Extra_Slack_Webhook] = ''

        changed = set_notification_config(odb_session, _cluster_id, cleared)
        odb_session.commit()
        assert changed is True

        parsed = parse_extra(_get_sweep_job(odb_session).extra)

        assert Alerting.Extra_Slack_Webhook not in parsed
        assert parsed[Alerting.Extra_Teams_Webhook] == _values[Alerting.Extra_Teams_Webhook]

# ################################################################################################################################

    def test_saving_the_same_values_changes_nothing(self, odb_session:'any_') -> 'None':

        _ = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()

        changed = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()

        assert changed is False

# ################################################################################################################################

    def test_clearing_every_value_leaves_an_empty_extra(self, odb_session:'any_') -> 'None':

        _ = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()

        cleared = {}
        for key in notification_keys:
            cleared[key] = ''

        _ = set_notification_config(odb_session, _cluster_id, cleared)
        odb_session.commit()

        # An extra with nothing left is stored as empty text, not as an empty object
        assert _get_sweep_job(odb_session).extra == ''

# ################################################################################################################################

    def test_a_key_not_sent_stays_as_it_was(self, odb_session:'any_') -> 'None':

        _ = set_notification_config(odb_session, _cluster_id, _values)
        odb_session.commit()

        # Only the dashboard URL travels in this save
        _ = set_notification_config(odb_session, _cluster_id, {
            Alerting.Extra_Dashboard_URL: 'https://other.example.com',
        })
        odb_session.commit()

        parsed = parse_extra(_get_sweep_job(odb_session).extra)

        assert parsed[Alerting.Extra_Dashboard_URL] == 'https://other.example.com'
        assert parsed[Alerting.Extra_Slack_Webhook] == _values[Alerting.Extra_Slack_Webhook]

# ################################################################################################################################
# ################################################################################################################################
