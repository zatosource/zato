# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.broker_message import SECURITY
from zato.common.json_internal import dumps, loads
from zato.server.service.internal.security.rate_limiting import APIKeyRateLimitingSave
from zato.server.service.internal.security.tier import Create as TierCreate, Delete as TierDelete, \
    Edit as TierEdit, SetForGroup as TierSetForGroup

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

class _MockInput(dict):
    """ A dict that also supports attribute access, like a real service input object.
    """
    def __getattr__(self, name):
        return self[name]

# ################################################################################################################################

def _make_service(class_, input_data):
    """ Builds a bare service object with just enough state for handle() to work.
    """
    service = object.__new__(class_)

    service.request = MagicMock()
    service.request.input = _MockInput(input_data)

    service.response = MagicMock()
    service.server = MagicMock()
    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test')

    return service

# ################################################################################################################################
# ################################################################################################################################

class TierCreateTestCase(unittest.TestCase):

    def test_create_validates_and_saves(self):
        """ Valid rules are passed to the manager and the new id is returned.
        """
        rules = _make_rule_dicts()
        service = _make_service(TierCreate, {'name': 'Bronze', 'description': 'Entry tier', 'rules_json': dumps(rules)})
        service.server.quota_tiers_manager.get_tier_by_name.return_value = None
        service.server.quota_tiers_manager.create_tier.return_value = 100

        service.handle()

        service.server.quota_tiers_manager.create_tier.assert_called_once_with('Bronze', 'Entry tier', rules)

    def test_create_refuses_duplicate_name(self):
        """ Creating a tier under an existing name is refused.
        """
        rules = _make_rule_dicts()
        service = _make_service(TierCreate, {'name': 'Bronze', 'description': '', 'rules_json': dumps(rules)})
        service.server.quota_tiers_manager.get_tier_by_name.return_value = {'id': 100, 'name': 'Bronze'}

        with self.assertRaises(Exception) as ctx:
            service.handle()

        self.assertIn('already exists', str(ctx.exception))
        service.server.quota_tiers_manager.create_tier.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class TierEditTestCase(unittest.TestCase):

    def test_edit_publishes_config_event(self):
        """ A tier edit publishes the event that makes all workers re-resolve references.
        """
        rules = _make_rule_dicts()
        service = _make_service(TierEdit, {'id': '100', 'name': 'Bronze', 'description': '', 'rules_json': dumps(rules)})
        service.server.quota_tiers_manager.get_tier.return_value = {'id': 100, 'name': 'Bronze'}
        service.server.quota_tiers_manager.get_tier_by_name.return_value = {'id': 100, 'name': 'Bronze'}

        service.handle()

        service.config_dispatcher.publish.assert_called_once()

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], SECURITY.QUOTA_TIER_EDIT.value)
        self.assertEqual(call_args['id'], 100)

    def test_edit_refuses_rename_to_existing_name(self):
        """ Renaming a tier to another tier's name is refused.
        """
        rules = _make_rule_dicts()
        service = _make_service(TierEdit, {'id': '100', 'name': 'Gold', 'description': '', 'rules_json': dumps(rules)})
        service.server.quota_tiers_manager.get_tier.return_value = {'id': 100, 'name': 'Bronze'}
        service.server.quota_tiers_manager.get_tier_by_name.return_value = {'id': 200, 'name': 'Gold'}

        with self.assertRaises(Exception) as ctx:
            service.handle()

        self.assertIn('already exists', str(ctx.exception))
        service.server.quota_tiers_manager.edit_tier.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class TierDeleteTestCase(unittest.TestCase):

    def test_delete_refused_while_referenced(self):
        """ Deleting a referenced tier is refused and the error lists the referents by name.
        """
        service = _make_service(TierDelete, {'id': '100'})
        service.server.quota_tiers_manager.get_tier_referents.return_value = {
            'security': ['api.client.internal'],
            'groups': ['Partners'],
        }

        with self.assertRaises(Exception) as ctx:
            service.handle()

        self.assertIn('api.client.internal', str(ctx.exception))
        self.assertIn('Partners', str(ctx.exception))
        service.server.quota_tiers_manager.delete_tier.assert_not_called()

    def test_delete_proceeds_without_referents(self):
        """ A tier with no referents is deleted.
        """
        service = _make_service(TierDelete, {'id': '100'})
        service.server.quota_tiers_manager.get_tier_referents.return_value = {'security': [], 'groups': []}

        service.handle()

        service.server.quota_tiers_manager.delete_tier.assert_called_once_with(100)

# ################################################################################################################################
# ################################################################################################################################

class TierSetForGroupTestCase(unittest.TestCase):

    def test_set_tier_for_group(self):
        """ Assigning a tier to a group persists the reference and publishes the config event.
        """
        service = _make_service(TierSetForGroup, {'group_id': '500', 'quota_tier': '100'})
        service.server.quota_tiers_manager.get_tier.return_value = {'id': 100, 'name': 'Bronze'}

        service.handle()

        service.server.groups_manager.set_group_quota_tier.assert_called_once_with(500, 100)

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], SECURITY.QUOTA_TIER_EDIT.value)

    def test_remove_tier_from_group(self):
        """ An empty tier on input removes the group's reference.
        """
        service = _make_service(TierSetForGroup, {'group_id': '500', 'quota_tier': ''})

        service.handle()

        service.server.groups_manager.set_group_quota_tier.assert_called_once_with(500, None)

# ################################################################################################################################
# ################################################################################################################################

class SaveMutualExclusivityTestCase(unittest.TestCase):

    def _make_save_service(self, input_data, existing_opaque=None):
        service = _make_service(APIKeyRateLimitingSave, input_data)

        mock_item = type('MockItem', (), {
            'opaque1': dumps(existing_opaque) if existing_opaque is not None else None,
        })()

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.one.return_value = mock_item

        service.odb = MagicMock()
        service.odb.session.return_value = mock_session

        return service, mock_item

    def test_both_tier_and_rules_rejected(self):
        """ A definition cannot carry both a tier reference and its own rules.
        """
        rules = _make_rule_dicts()
        service, _ = self._make_save_service({'id': '20', 'rules_json': dumps(rules), 'quota_tier': '100'})

        with self.assertRaises(Exception) as ctx:
            service.handle()

        self.assertIn('cannot have both', str(ctx.exception))

    def test_tier_reference_replaces_own_rules(self):
        """ Saving a tier reference removes previously stored rules.
        """
        existing = {'rate_limiting': _make_rule_dicts()}
        service, mock_item = self._make_save_service({'id': '20', 'rules_json': '', 'quota_tier': '100'}, existing)
        service.server.quota_tiers_manager.get_tier.return_value = {'id': 100, 'name': 'Bronze'}

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(saved_opaque['quota_tier'], 100)
        self.assertNotIn('rate_limiting', saved_opaque)

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], SECURITY.QUOTA_TIER_EDIT.value)

    def test_own_rules_replace_tier_reference(self):
        """ Saving own rules removes a previously stored tier reference.
        """
        existing = {'quota_tier': 100}
        rules = _make_rule_dicts()
        service, mock_item = self._make_save_service({'id': '20', 'rules_json': dumps(rules), 'quota_tier': ''}, existing)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertNotIn('quota_tier', saved_opaque)
        self.assertEqual(len(saved_opaque['rate_limiting']), 1)

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], SECURITY.APIKEY_RATE_LIMITING_EDIT.value)

    def test_unknown_tier_rejected(self):
        """ Referencing a tier that does not exist is refused.
        """
        service, _ = self._make_save_service({'id': '20', 'rules_json': '', 'quota_tier': '999'})
        service.server.quota_tiers_manager.get_tier.return_value = None

        with self.assertRaises(Exception) as ctx:
            service.handle()

        self.assertIn('not found', str(ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
