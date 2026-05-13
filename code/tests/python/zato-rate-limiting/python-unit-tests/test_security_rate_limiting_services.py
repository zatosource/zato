# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.broker_message import SECURITY
from zato.common.json_internal import dumps, loads
from zato.common.rate_limiting.common import RateLimitError, Window_Unit_Second
from zato.server.service.internal.security.rate_limiting import \
    BasicAuthRateLimitingGet, BasicAuthRateLimitingSave, BasicAuthRateLimitingClearCounters, \
    APIKeyRateLimitingGet, APIKeyRateLimitingSave, APIKeyRateLimitingClearCounters

# ################################################################################################################################
# ################################################################################################################################

def _all_day_range(**overrides):
    out = {
        'is_all_day':  True,
        'disabled':    False,
        'disallowed':  False,
        'rate':        100,
        'burst':       200,
        'limit':       1000,
        'limit_unit':  Window_Unit_Second,
    }
    out.update(overrides)
    return out

# ################################################################################################################################

def _make_rule(cidr_list, time_range):
    return {
        'cidr_list': cidr_list,
        'time_range': time_range,
    }

# ################################################################################################################################

def _make_get_service(class_, sec_def_id, existing_opaque=None):
    """ Builds a bare object with just enough state for handle() to work.
    """
    service = object.__new__(class_)

    service.request = MagicMock()
    service.request.input = {'id': str(sec_def_id)}

    service.response = MagicMock()

    mock_item = type('MockItem', (), {
        'opaque1': dumps(existing_opaque) if existing_opaque is not None else None,
    })()

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.one.return_value = mock_item

    service.odb = MagicMock()
    service.odb.session.return_value = mock_session

    return service

# ################################################################################################################################

def _make_save_service(class_, sec_def_id, rules, existing_opaque=None):
    """ Builds a bare object with just enough state for handle() to work.
    """
    service = object.__new__(class_)

    service.request = MagicMock()
    service.request.input = {
        'id': str(sec_def_id),
        'rules_json': dumps(rules),
    }

    mock_item = type('MockItem', (), {
        'opaque1': dumps(existing_opaque) if existing_opaque is not None else None,
    })()

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.one.return_value = mock_item

    service.odb = MagicMock()
    service.odb.session.return_value = mock_session

    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test')

    return service, mock_item, mock_session

# ################################################################################################################################

def _make_clear_service(class_, sec_def_id, rule_index):
    """ Builds a bare object with just enough state for handle() to work.
    """
    service = object.__new__(class_)

    service.request = MagicMock()
    service.request.input = {
        'id': str(sec_def_id),
        'rule_index': str(rule_index),
    }

    service.server = MagicMock()

    return service

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthGetTestCase(unittest.TestCase):

    def test_returns_empty_list_when_no_opaque(self):
        """ When opaque1 is None, an empty list is returned.
        """
        service = _make_get_service(BasicAuthRateLimitingGet, 10)

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], [])

    def test_returns_empty_list_when_no_rate_limiting_key(self):
        """ When opaque1 exists but has no rate_limiting key, an empty list is returned.
        """
        service = _make_get_service(BasicAuthRateLimitingGet, 10, existing_opaque={'http_accept': 'text/html'})

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], [])

    def test_returns_stored_rules(self):
        """ When rate_limiting rules exist, they are returned as-is.
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service = _make_get_service(BasicAuthRateLimitingGet, 10, existing_opaque={'rate_limiting': rules})

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], rules)

    def test_returns_multiple_rules(self):
        """ Multiple rules are all returned.
        """
        rules = [
            _make_rule(['10.0.0.0/8'], [_all_day_range()]),
            _make_rule(['192.168.0.0/16'], [_all_day_range(rate=50)]),
        ]
        service = _make_get_service(BasicAuthRateLimitingGet, 10, existing_opaque={'rate_limiting': rules})

        service.handle()

        result = service.response.payload['rate_limiting']
        self.assertEqual(len(result), 2)

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthSaveTestCase(unittest.TestCase):

    def test_save_valid_rules(self):
        """ Valid rules are saved into opaque1['rate_limiting'].
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, mock_item, mock_session = _make_save_service(BasicAuthRateLimitingSave, 10, rules)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertIn('rate_limiting', saved_opaque)
        self.assertEqual(len(saved_opaque['rate_limiting']), 1)
        self.assertEqual(saved_opaque['rate_limiting'][0]['cidr_list'], ['10.0.0.0/8'])

        mock_session.add.assert_called_once_with(mock_item)
        mock_session.commit.assert_called_once()

    def test_save_preserves_existing_opaque_keys(self):
        """ Existing keys in opaque1 are not lost when saving rate_limiting.
        """
        existing = {'http_accept': 'application/json', 'some_flag': True}
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, mock_item, _ = _make_save_service(BasicAuthRateLimitingSave, 10, rules, existing_opaque=existing)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(saved_opaque['http_accept'], 'application/json')
        self.assertTrue(saved_opaque['some_flag'])
        self.assertIn('rate_limiting', saved_opaque)

    def test_save_empty_opaque_creates_dict(self):
        """ When opaque1 is None, a new dict is created.
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, mock_item, _ = _make_save_service(BasicAuthRateLimitingSave, 10, rules, existing_opaque=None)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertIn('rate_limiting', saved_opaque)

    def test_save_invalid_cidr_rejected(self):
        """ Invalid CIDR in rules raises RateLimitError before ODB write.
        """
        rules = [_make_rule(['not-a-cidr'], [_all_day_range()])]
        service, _, mock_session = _make_save_service(BasicAuthRateLimitingSave, 10, rules)

        with self.assertRaises(RateLimitError):
            service.handle()

        mock_session.commit.assert_not_called()

    def test_save_publishes_config_event(self):
        """ After ODB commit, config_dispatcher.publish is called with the correct action.
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, _, _ = _make_save_service(BasicAuthRateLimitingSave, 10, rules)

        service.handle()

        service.config_dispatcher.publish.assert_called_once()

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], SECURITY.BASIC_AUTH_RATE_LIMITING_EDIT.value)
        self.assertEqual(call_args['id'], 10)
        self.assertEqual(len(call_args['rule_dicts']), 1)

    def test_save_does_not_publish_on_validation_error(self):
        """ If validation fails, config_dispatcher.publish must not be called.
        """
        rules = [_make_rule(['not-a-cidr'], [_all_day_range()])]
        service, _, _ = _make_save_service(BasicAuthRateLimitingSave, 10, rules)

        with self.assertRaises(RateLimitError):
            service.handle()

        service.config_dispatcher.publish.assert_not_called()

    def test_save_multiple_rules(self):
        """ Multiple rules are all saved.
        """
        rules = [
            _make_rule(['10.0.0.0/8'], [_all_day_range()]),
            _make_rule(['192.168.0.0/16'], [_all_day_range(rate=50)]),
        ]
        service, mock_item, _ = _make_save_service(BasicAuthRateLimitingSave, 10, rules)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(len(saved_opaque['rate_limiting']), 2)

# ################################################################################################################################
# ################################################################################################################################

class BasicAuthClearCountersTestCase(unittest.TestCase):

    def test_clear_counters_calls_manager(self):
        """ clear_sec_def_rule_counters is called with correct arguments.
        """
        service = _make_clear_service(BasicAuthRateLimitingClearCounters, 10, 2)

        service.handle()

        service.server.rate_limiting_manager.clear_sec_def_rule_counters.assert_called_once_with(10, 2, 'basic10:')

    def test_clear_counters_key_prefix_format(self):
        """ The key prefix follows the basic{id}: pattern.
        """
        service = _make_clear_service(BasicAuthRateLimitingClearCounters, 99, 0)

        service.handle()

        call_args = service.server.rate_limiting_manager.clear_sec_def_rule_counters.call_args[0]
        self.assertEqual(call_args[2], 'basic99:')

# ################################################################################################################################
# ################################################################################################################################

class APIKeyGetTestCase(unittest.TestCase):

    def test_returns_empty_list_when_no_opaque(self):
        """ When opaque1 is None, an empty list is returned.
        """
        service = _make_get_service(APIKeyRateLimitingGet, 20)

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], [])

    def test_returns_empty_list_when_no_rate_limiting_key(self):
        """ When opaque1 exists but has no rate_limiting key, an empty list is returned.
        """
        service = _make_get_service(APIKeyRateLimitingGet, 20, existing_opaque={'header': 'X-API-Key'})

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], [])

    def test_returns_stored_rules(self):
        """ When rate_limiting rules exist, they are returned as-is.
        """
        rules = [_make_rule(['172.16.0.0/12'], [_all_day_range()])]
        service = _make_get_service(APIKeyRateLimitingGet, 20, existing_opaque={'rate_limiting': rules})

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], rules)

    def test_returns_multiple_rules(self):
        """ Multiple rules are all returned.
        """
        rules = [
            _make_rule(['10.0.0.0/8'], [_all_day_range()]),
            _make_rule(['192.168.0.0/16'], [_all_day_range(rate=50)]),
        ]
        service = _make_get_service(APIKeyRateLimitingGet, 20, existing_opaque={'rate_limiting': rules})

        service.handle()

        result = service.response.payload['rate_limiting']
        self.assertEqual(len(result), 2)

# ################################################################################################################################
# ################################################################################################################################

class APIKeySaveTestCase(unittest.TestCase):

    def test_save_valid_rules(self):
        """ Valid rules are saved into opaque1['rate_limiting'].
        """
        rules = [_make_rule(['172.16.0.0/12'], [_all_day_range()])]
        service, mock_item, mock_session = _make_save_service(APIKeyRateLimitingSave, 20, rules)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertIn('rate_limiting', saved_opaque)
        self.assertEqual(len(saved_opaque['rate_limiting']), 1)
        self.assertEqual(saved_opaque['rate_limiting'][0]['cidr_list'], ['172.16.0.0/12'])

        mock_session.add.assert_called_once_with(mock_item)
        mock_session.commit.assert_called_once()

    def test_save_preserves_existing_opaque_keys(self):
        """ Existing keys in opaque1 are not lost when saving rate_limiting.
        """
        existing = {'header': 'X-API-Key', 'some_flag': True}
        rules = [_make_rule(['172.16.0.0/12'], [_all_day_range()])]
        service, mock_item, _ = _make_save_service(APIKeyRateLimitingSave, 20, rules, existing_opaque=existing)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(saved_opaque['header'], 'X-API-Key')
        self.assertTrue(saved_opaque['some_flag'])
        self.assertIn('rate_limiting', saved_opaque)

    def test_save_empty_opaque_creates_dict(self):
        """ When opaque1 is None, a new dict is created.
        """
        rules = [_make_rule(['172.16.0.0/12'], [_all_day_range()])]
        service, mock_item, _ = _make_save_service(APIKeyRateLimitingSave, 20, rules, existing_opaque=None)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertIn('rate_limiting', saved_opaque)

    def test_save_invalid_cidr_rejected(self):
        """ Invalid CIDR in rules raises RateLimitError before ODB write.
        """
        rules = [_make_rule(['not-a-cidr'], [_all_day_range()])]
        service, _, mock_session = _make_save_service(APIKeyRateLimitingSave, 20, rules)

        with self.assertRaises(RateLimitError):
            service.handle()

        mock_session.commit.assert_not_called()

    def test_save_publishes_config_event(self):
        """ After ODB commit, config_dispatcher.publish is called with the correct action.
        """
        rules = [_make_rule(['172.16.0.0/12'], [_all_day_range()])]
        service, _, _ = _make_save_service(APIKeyRateLimitingSave, 20, rules)

        service.handle()

        service.config_dispatcher.publish.assert_called_once()

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], SECURITY.APIKEY_RATE_LIMITING_EDIT.value)
        self.assertEqual(call_args['id'], 20)
        self.assertEqual(len(call_args['rule_dicts']), 1)

    def test_save_does_not_publish_on_validation_error(self):
        """ If validation fails, config_dispatcher.publish must not be called.
        """
        rules = [_make_rule(['not-a-cidr'], [_all_day_range()])]
        service, _, _ = _make_save_service(APIKeyRateLimitingSave, 20, rules)

        with self.assertRaises(RateLimitError):
            service.handle()

        service.config_dispatcher.publish.assert_not_called()

    def test_save_multiple_rules(self):
        """ Multiple rules are all saved.
        """
        rules = [
            _make_rule(['172.16.0.0/12'], [_all_day_range()]),
            _make_rule(['10.0.0.0/8'], [_all_day_range(rate=50)]),
        ]
        service, mock_item, _ = _make_save_service(APIKeyRateLimitingSave, 20, rules)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(len(saved_opaque['rate_limiting']), 2)

# ################################################################################################################################
# ################################################################################################################################

class APIKeyClearCountersTestCase(unittest.TestCase):

    def test_clear_counters_calls_manager(self):
        """ clear_sec_def_rule_counters is called with correct arguments.
        """
        service = _make_clear_service(APIKeyRateLimitingClearCounters, 20, 3)

        service.handle()

        service.server.rate_limiting_manager.clear_sec_def_rule_counters.assert_called_once_with(20, 3, 'apikey20:')

    def test_clear_counters_key_prefix_format(self):
        """ The key prefix follows the apikey{id}: pattern.
        """
        service = _make_clear_service(APIKeyRateLimitingClearCounters, 77, 1)

        service.handle()

        call_args = service.server.rate_limiting_manager.clear_sec_def_rule_counters.call_args[0]
        self.assertEqual(call_args[2], 'apikey77:')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
