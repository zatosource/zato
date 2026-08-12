# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.alerting.model import new_finding, new_rule, FindingKind
from zato.common.alerting.store import raise_alert, render_alert_message
from zato.common.audit_log.api import get_audit_engine, AuditLog, AuditSource
from zato.common.audit_log.common import alert_table
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import dictlist
    dictlist = dictlist
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The server name the schema is created under
_server_name = 'test-alerting-server'

# The source and object the tests raise findings about
_source = 'mllp-channel'
_channel_name = 'hl7.test.channel'

# The outgoing connection whose check and whose traffic are told apart
_connection_name = 'crm.orders.api'

# The dedup window all the test rules use, in seconds
_window_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def _new_engine() -> 'Engine':
    """ Creates the schema and returns the engine over it.
    """
    _ = AuditLog(_server_name)

    out = get_audit_engine()
    return out

# ################################################################################################################################

def _new_env() -> 'tuple':
    """ Creates the schema and returns the engine along with one rule and one finding.
    """
    engine = _new_engine()

    rule = new_rule('silent-feeds', FindingKind.Feed_Silent, dedup_window_seconds=_window_seconds)
    finding = new_finding(FindingKind.Feed_Silent, _source, _channel_name, 'Feed on `hl7.test.channel` silent for 300s')

    return engine, rule, finding

# ################################################################################################################################

def _get_alert_rows(engine:'Engine') -> 'dictlist':
    """ Every alert row in the store, newest first.
    """
    statement = select(alert_table).order_by(alert_table.c.id.desc())

    out:'dictlist' = []

    with engine.connect() as connection:
        for row in connection.execute(statement):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDedup:

    def test_the_first_finding_raises_a_new_alert(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        result = raise_alert(engine, rule, finding, now)

        assert result.is_new is True
        assert result.count == 1

        alerts = _get_alert_rows(engine)

        assert len(alerts) == 1
        assert alerts[0]['id'] == result.alert_id
        assert alerts[0]['rule_name'] == 'silent-feeds'
        assert alerts[0]['object_name'] == _channel_name
        assert alerts[0]['count'] == 1

# ################################################################################################################################

    def test_a_repetition_within_the_window_grows_the_count(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        first = raise_alert(engine, rule, finding, now)
        second = raise_alert(engine, rule, finding, now + timedelta(seconds=60))
        third = raise_alert(engine, rule, finding, now + timedelta(seconds=120))

        # One alert, counted three times - not three rows
        assert second.is_new is False
        assert third.is_new is False
        assert third.alert_id == first.alert_id
        assert third.count == 3

        alerts = _get_alert_rows(engine)
        assert len(alerts) == 1
        assert alerts[0]['count'] == 3

# ################################################################################################################################

    def test_a_repetition_after_the_window_is_a_new_alert(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        first = raise_alert(engine, rule, finding, now)
        later = raise_alert(engine, rule, finding, now + timedelta(seconds=_window_seconds + 1))

        assert later.is_new is True
        assert later.alert_id != first.alert_id
        assert len(_get_alert_rows(engine)) == 2

# ################################################################################################################################

    def test_the_window_keys_on_the_last_occurrence(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        # Each repetition moves the window forward - what matters is the time
        # since the last occurrence, not since the first
        first = raise_alert(engine, rule, finding, now)
        _ = raise_alert(engine, rule, finding, now + timedelta(seconds=_window_seconds - 60))

        # Well past the first occurrence's window, still inside the second's
        third = raise_alert(engine, rule, finding, now + timedelta(seconds=_window_seconds + 120))

        assert third.is_new is False
        assert third.alert_id == first.alert_id
        assert third.count == 3

# ################################################################################################################################

    def test_different_objects_never_share_an_alert(self) -> 'None':
        engine, rule, finding = _new_env()
        other_finding = new_finding(FindingKind.Feed_Silent, _source, 'hl7.other.channel', 'The other feed went quiet')
        now = utcnow()

        first = raise_alert(engine, rule, finding, now)
        second = raise_alert(engine, rule, other_finding, now)

        assert first.is_new is True
        assert second.is_new is True
        assert first.alert_id != second.alert_id

# ################################################################################################################################

    def test_two_sources_on_one_object_raise_two_alerts(self) -> 'None':
        """ A connection's health check and the traffic it carries share a name and are
        measured apart, so what is measured apart is also reported apart.
        """
        engine = _new_engine()
        rule = new_rule('connection-errors', FindingKind.Error_Rate, dedup_window_seconds=_window_seconds)
        now = utcnow()

        traffic_finding = new_finding(
            FindingKind.Error_Rate, AuditSource.REST_Outgoing, _connection_name, 'The calls are failing')
        check_finding = new_finding(
            FindingKind.Error_Rate, AuditSource.REST_Outgoing_Health, _connection_name, 'The check is failing')

        # Both inside the dedup window, which is where a shared row would have absorbed the second
        first = raise_alert(engine, rule, traffic_finding, now)
        second = raise_alert(engine, rule, check_finding, now + timedelta(seconds=60))

        assert first.is_new is True
        assert second.is_new is True
        assert first.alert_id != second.alert_id

        alerts = _get_alert_rows(engine)
        assert len(alerts) == 2

        sources = set()

        for alert in alerts:
            assert alert['object_name'] == _connection_name
            assert alert['count'] == 1
            sources.add(alert['source'])

        assert sources == {AuditSource.REST_Outgoing, AuditSource.REST_Outgoing_Health}

# ################################################################################################################################

    def test_one_source_still_deduplicates_within_the_window(self) -> 'None':
        """ Telling the two streams apart does not stop either of them deduplicating.
        """
        engine = _new_engine()
        rule = new_rule('connection-errors', FindingKind.Error_Rate, dedup_window_seconds=_window_seconds)
        now = utcnow()

        check_finding = new_finding(
            FindingKind.Error_Rate, AuditSource.REST_Outgoing_Health, _connection_name, 'The check is failing')

        first = raise_alert(engine, rule, check_finding, now)
        second = raise_alert(engine, rule, check_finding, now + timedelta(seconds=60))

        assert second.is_new is False
        assert second.alert_id == first.alert_id
        assert second.count == 2

        assert len(_get_alert_rows(engine)) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestRendering:

    def test_a_first_occurrence_has_no_prefix(self) -> 'None':
        assert render_alert_message(1, 'channel adt.main silent') == 'channel adt.main silent'

# ################################################################################################################################

    def test_repetitions_show_up_as_a_count_prefix(self) -> 'None':
        assert render_alert_message(3, 'channel adt.main silent') == '[3x] channel adt.main silent'

# ################################################################################################################################
# ################################################################################################################################
