# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.model import new_finding, new_rule, rule_matches, AlertSeverity, FindingKind

# ################################################################################################################################
# ################################################################################################################################

# The source and object the tests raise findings about
_source = 'hl7'
_channel_name = 'hl7.test.channel'

# ################################################################################################################################
# ################################################################################################################################

class TestRuleMatching:

    def test_the_kind_is_the_one_required_match(self) -> 'None':
        rule = new_rule('silent-feeds', FindingKind.Feed_Silent)

        matching = new_finding(FindingKind.Feed_Silent, _source, _channel_name, 'The feed went quiet')
        other = new_finding(FindingKind.Error_Rate, _source, _channel_name, 'The channel errors')

        assert rule_matches(rule, matching) is True
        assert rule_matches(rule, other) is False

# ################################################################################################################################

    def test_source_and_object_narrow_the_match_only_when_set(self) -> 'None':
        broad = new_rule('all-silent-feeds', FindingKind.Feed_Silent)
        narrowed = new_rule('one-silent-feed', FindingKind.Feed_Silent, source=_source, object_name=_channel_name)

        ours = new_finding(FindingKind.Feed_Silent, _source, _channel_name, 'The feed went quiet')
        other_object = new_finding(FindingKind.Feed_Silent, _source, 'hl7.other.channel', 'The feed went quiet')
        other_source = new_finding(FindingKind.Feed_Silent, 'as2', _channel_name, 'The feed went quiet')

        assert rule_matches(broad, ours) is True
        assert rule_matches(broad, other_object) is True
        assert rule_matches(broad, other_source) is True

        assert rule_matches(narrowed, ours) is True
        assert rule_matches(narrowed, other_object) is False
        assert rule_matches(narrowed, other_source) is False

# ################################################################################################################################

    def test_an_inactive_rule_matches_nothing(self) -> 'None':
        rule = new_rule('paused', FindingKind.Feed_Silent, is_active=False)
        finding = new_finding(FindingKind.Feed_Silent, _source, _channel_name, 'The feed went quiet')

        assert rule_matches(rule, finding) is False

# ################################################################################################################################

    def test_a_finding_defaults_to_a_warning(self) -> 'None':
        finding = new_finding(FindingKind.Feed_Silent, _source, _channel_name, 'The feed went quiet')

        assert finding.severity == AlertSeverity.Warning

# ################################################################################################################################
# ################################################################################################################################
