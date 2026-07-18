# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.alerting.model import new_finding, new_rule, AlertState, FindingKind
from zato.common.alerting.store import get_alerts, observe_alert, raise_alert, render_alert_message, resolve_alert
from zato.common.audit_log.api import get_audit_engine, AuditLog
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

# The server name the schema is created under
_server_name = 'test-alerting-server'

# The source and object the tests raise findings about
_source = 'hl7'
_channel_name = 'hl7.test.channel'

# The dedup window all the test rules use, in seconds
_window_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def _new_env() -> 'tuple':
    """ Creates the schema and returns the engine along with one rule and one finding.
    """
    _ = AuditLog(_server_name)
    engine = get_audit_engine()

    rule = new_rule('silent-feeds', FindingKind.Feed_Silent, dedup_window_seconds=_window_seconds)
    finding = new_finding(FindingKind.Feed_Silent, _source, _channel_name, 'Feed on `hl7.test.channel` silent for 300s')

    return engine, rule, finding

# ################################################################################################################################
# ################################################################################################################################

class TestDedup:

    def test_the_first_finding_raises_a_new_alert(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        result = raise_alert(engine, rule, finding, now)

        assert result.is_new is True
        assert result.count == 1

        alerts = get_alerts(engine)

        assert len(alerts) == 1
        assert alerts[0]['id'] == result.alert_id
        assert alerts[0]['rule_name'] == 'silent-feeds'
        assert alerts[0]['object_name'] == _channel_name
        assert alerts[0]['state'] == AlertState.Unobserved
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

        alerts = get_alerts(engine)
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
        assert len(get_alerts(engine)) == 2

# ################################################################################################################################

    def test_a_resolved_alert_never_absorbs_new_findings(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        first = raise_alert(engine, rule, finding, now)
        resolve_alert(engine, first.alert_id, 'admin', now)

        # The same finding immediately afterwards raises a new alert - the previous one was resolved
        second = raise_alert(engine, rule, finding, now + timedelta(seconds=1))

        assert second.is_new is True
        assert second.alert_id != first.alert_id

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
# ################################################################################################################################

class TestLifecycle:

    def test_observed_then_resolved_with_who_and_when(self) -> 'None':
        engine, rule, finding = _new_env()
        now = utcnow()

        result = raise_alert(engine, rule, finding, now)

        observe_alert(engine, result.alert_id, 'admin', now + timedelta(seconds=10))

        alerts = get_alerts(engine)
        assert alerts[0]['state'] == AlertState.Observed
        assert alerts[0]['observed_by'] == 'admin'
        assert alerts[0]['observed_iso'] != ''

        resolve_alert(engine, result.alert_id, 'admin', now + timedelta(seconds=20))

        alerts = get_alerts(engine)
        assert alerts[0]['state'] == AlertState.Resolved
        assert alerts[0]['resolved_by'] == 'admin'
        assert alerts[0]['resolved_iso'] != ''

# ################################################################################################################################

    def test_an_observed_alert_still_absorbs_repetitions(self) -> 'None':

        # Acknowledgment does not end deduplication - repeated findings keep
        # incrementing the acknowledged alert instead of raising new ones.
        engine, rule, finding = _new_env()
        now = utcnow()

        result = raise_alert(engine, rule, finding, now)
        observe_alert(engine, result.alert_id, 'admin', now)

        repetition = raise_alert(engine, rule, finding, now + timedelta(seconds=60))

        assert repetition.is_new is False
        assert repetition.alert_id == result.alert_id

# ################################################################################################################################

    def test_alerts_are_filterable_by_state(self) -> 'None':
        engine, rule, finding = _new_env()
        other_finding = new_finding(FindingKind.Feed_Silent, _source, 'hl7.other.channel', 'The other feed went quiet')
        now = utcnow()

        first = raise_alert(engine, rule, finding, now)
        _ = raise_alert(engine, rule, other_finding, now)

        resolve_alert(engine, first.alert_id, 'admin', now)

        assert len(get_alerts(engine, state=AlertState.Resolved)) == 1
        assert len(get_alerts(engine, state=AlertState.Unobserved)) == 1

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
