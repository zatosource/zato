# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import Groups
from zato.common.json_internal import dumps
from zato.server.quota_tiers import QuotaTiersManager

# ################################################################################################################################
# ################################################################################################################################

def _make_rule_dicts(rate=10, burst=20, limit=100, limit_unit='minute', cidr='10.0.0.0/8'):
    return [{
        'cidr_list': [cidr],
        'time_range': [{
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': rate,
            'burst': burst,
            'limit': limit,
            'limit_unit': limit_unit,
        }]
    }]

# ################################################################################################################################

def _make_sec_row(sec_def_id, name, opaque=None):
    """ Builds a stand-in for a SecurityBase row.
    """
    out = type('MockSecRow', (), {
        'id': sec_def_id,
        'name': name,
        'opaque1': dumps(opaque) if opaque is not None else None,
    })()

    return out

# ################################################################################################################################

def _make_manager(tier_rows, sec_rows, group_rows, member_rows_by_group):
    """ Builds a QuotaTiersManager whose SQL access is fully mocked.

    tier_rows - rows returned for the tier listing (dicts with id, name, description, rules)
    sec_rows - SecurityBase row stand-ins
    group_rows - group parent rows (dicts with id, name and optionally quota_tier)
    member_rows_by_group - group id -> list of member row dicts (with a 'name' key)
    """
    mock_session = MagicMock()
    session_factory = MagicMock(return_value=mock_session)

    server = MagicMock()
    server.cluster_id = 1

    manager = QuotaTiersManager(server, session_factory)

    # Security definition rows come from a direct SQLAlchemy query
    mock_session.query.return_value.filter.return_value.all.return_value = sec_rows

    # Everything else comes through GenericObjectWrapper.get_list
    def get_list_side_effect(*args, **kwargs):

        # No arguments means the tier listing
        if not args:
            return tier_rows

        # Group parent rows
        if args[0] == Groups.Type.Group_Parent:
            return group_rows

        # Group member rows
        group_id = kwargs['parent_object_id']
        return member_rows_by_group[group_id]

    wrapper = MagicMock()
    wrapper.get_list.side_effect = get_list_side_effect

    wrapper_class = MagicMock(return_value=wrapper)
    patcher = patch('zato.server.quota_tiers.GenericObjectWrapper', wrapper_class)
    _ = patcher.start()

    return manager, patcher

# ################################################################################################################################
# ################################################################################################################################

class ResolveTierAssignmentsTestCase(unittest.TestCase):

    def test_direct_tier_reference_installs_tier_rules(self):
        """ A definition referencing a tier receives the tier's rules under its own id.
        """
        tier_rules = _make_rule_dicts(rate=5)
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': tier_rules}]
        sec_rows = [_make_sec_row(10, 'api.client.internal', {'quota_tier': 100})]

        manager, patcher = _make_manager(tier_rows, sec_rows, [], {})
        self.addCleanup(patcher.stop)

        resolution = manager.resolve_tier_assignments()

        self.assertEqual(resolution.rules_by_sec_def, {10: tier_rules})

    def test_own_rules_exclude_definition_from_tiers(self):
        """ A definition with its own literal rules is never governed by a tier.
        """
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': _make_rule_dicts()}]
        sec_rows = [_make_sec_row(10, 'api.client.internal', {'rate_limiting': _make_rule_dicts(rate=1)})]

        manager, patcher = _make_manager(tier_rows, sec_rows, [], {})
        self.addCleanup(patcher.stop)

        resolution = manager.resolve_tier_assignments()

        self.assertEqual(resolution.rules_by_sec_def, {})
        self.assertEqual(resolution.own_rules_sec_def_ids, {10})

    def test_group_tier_applies_to_members(self):
        """ A tier on a group covers every member without own rules or a direct tier.
        """
        tier_rules = _make_rule_dicts(rate=7)
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': tier_rules}]
        sec_rows = [
            _make_sec_row(10, 'api.client.first'),
            _make_sec_row(11, 'api.client.second'),
        ]
        group_rows = [{'id': 500, 'name': 'Partners', 'quota_tier': 100}]
        member_rows_by_group = {500: [{'name': 'apikey-10-500'}, {'name': 'basic_auth-11-500'}]}

        manager, patcher = _make_manager(tier_rows, sec_rows, group_rows, member_rows_by_group)
        self.addCleanup(patcher.stop)

        resolution = manager.resolve_tier_assignments()

        self.assertEqual(resolution.rules_by_sec_def, {10: tier_rules, 11: tier_rules})

    def test_direct_tier_overrides_group_tier(self):
        """ A tier set directly on a definition wins over the tier of a group it belongs to.
        """
        direct_rules = _make_rule_dicts(rate=50)
        group_rules = _make_rule_dicts(rate=5)
        tier_rows = [
            {'id': 100, 'name': 'Bronze', 'description': '', 'rules': group_rules},
            {'id': 200, 'name': 'Gold', 'description': '', 'rules': direct_rules},
        ]
        sec_rows = [_make_sec_row(10, 'api.client.premium', {'quota_tier': 200})]
        group_rows = [{'id': 500, 'name': 'Partners', 'quota_tier': 100}]
        member_rows_by_group = {500: [{'name': 'apikey-10-500'}]}

        manager, patcher = _make_manager(tier_rows, sec_rows, group_rows, member_rows_by_group)
        self.addCleanup(patcher.stop)

        resolution = manager.resolve_tier_assignments()

        self.assertEqual(resolution.rules_by_sec_def, {10: direct_rules})

    def test_own_rules_override_group_tier(self):
        """ A definition with its own literal rules is not covered by its group's tier.
        """
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': _make_rule_dicts()}]
        sec_rows = [_make_sec_row(10, 'api.client.custom', {'rate_limiting': _make_rule_dicts(rate=1)})]
        group_rows = [{'id': 500, 'name': 'Partners', 'quota_tier': 100}]
        member_rows_by_group = {500: [{'name': 'apikey-10-500'}]}

        manager, patcher = _make_manager(tier_rows, sec_rows, group_rows, member_rows_by_group)
        self.addCleanup(patcher.stop)

        resolution = manager.resolve_tier_assignments()

        self.assertEqual(resolution.rules_by_sec_def, {})

    def test_group_without_tier_is_skipped(self):
        """ Members of groups without a tier are not governed by anything.
        """
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': _make_rule_dicts()}]
        sec_rows = [_make_sec_row(10, 'api.client.plain')]
        group_rows = [{'id': 500, 'name': 'Partners'}]

        manager, patcher = _make_manager(tier_rows, sec_rows, group_rows, {})
        self.addCleanup(patcher.stop)

        resolution = manager.resolve_tier_assignments()

        self.assertEqual(resolution.rules_by_sec_def, {})

# ################################################################################################################################
# ################################################################################################################################

class InstallTierAssignmentsTestCase(unittest.TestCase):

    def test_install_sets_config_per_definition(self):
        """ Resolved tier rules are installed in the rate-limiting manager per definition id.
        """
        tier_rules = _make_rule_dicts(rate=5)
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': tier_rules}]
        sec_rows = [_make_sec_row(10, 'api.client.internal', {'quota_tier': 100})]

        manager, patcher = _make_manager(tier_rows, sec_rows, [], {})
        self.addCleanup(patcher.stop)

        manager.install_tier_assignments()

        manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(10, tier_rules)

    def test_install_clears_definitions_no_longer_governed(self):
        """ A definition that lost its tier reference has its rules cleared on the next pass.
        """
        tier_rules = _make_rule_dicts(rate=5)
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': tier_rules}]
        sec_rows = [_make_sec_row(10, 'api.client.internal', {'quota_tier': 100})]

        manager, patcher = _make_manager(tier_rows, sec_rows, [], {})
        self.addCleanup(patcher.stop)

        # First pass installs the rules ..
        manager.install_tier_assignments()

        # .. now the definition drops its tier reference ..
        sec_rows[0].opaque1 = None
        manager.server.rate_limiting_manager.reset_mock()

        # .. and the second pass clears the previously installed rules.
        manager.install_tier_assignments()

        manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(10, [])

    def test_install_does_not_clear_definitions_that_switched_to_own_rules(self):
        """ A definition that replaced its tier with own rules is left alone by the tier pass.
        """
        tier_rules = _make_rule_dicts(rate=5)
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': tier_rules}]
        sec_rows = [_make_sec_row(10, 'api.client.internal', {'quota_tier': 100})]

        manager, patcher = _make_manager(tier_rows, sec_rows, [], {})
        self.addCleanup(patcher.stop)

        # First pass installs the tier rules ..
        manager.install_tier_assignments()

        # .. now the definition switches to its own rules ..
        sec_rows[0].opaque1 = dumps({'rate_limiting': _make_rule_dicts(rate=1)})
        manager.server.rate_limiting_manager.reset_mock()

        # .. and the second pass must not touch it at all.
        manager.install_tier_assignments()

        manager.server.rate_limiting_manager.set_sec_def_config.assert_not_called()

    def test_tier_edit_reinstalls_rules(self):
        """ After a tier's rules change, the next pass reinstalls the new rules.
        """
        old_rules = _make_rule_dicts(rate=5)
        new_rules = _make_rule_dicts(rate=25)
        tier_rows = [{'id': 100, 'name': 'Bronze', 'description': '', 'rules': old_rules}]
        sec_rows = [_make_sec_row(10, 'api.client.internal', {'quota_tier': 100})]

        manager, patcher = _make_manager(tier_rows, sec_rows, [], {})
        self.addCleanup(patcher.stop)

        # First pass installs the original rules ..
        manager.install_tier_assignments()

        # .. the tier is edited ..
        tier_rows[0]['rules'] = new_rules
        manager.server.rate_limiting_manager.reset_mock()

        # .. and the second pass installs the new rules.
        manager.install_tier_assignments()

        manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(10, new_rules)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
