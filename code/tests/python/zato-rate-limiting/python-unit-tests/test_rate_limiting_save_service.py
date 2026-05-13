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
from zato.common.broker_message import CHANNEL
from zato.common.json_internal import dumps, loads
from zato.common.rate_limiting.common import RateLimitError, Window_Unit_Second
from zato.server.service.internal.http_soap import RateLimitingSave

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

def _make_service(channel_id, rules, existing_opaque=None):
    """ Builds a bare object with just enough state for handle() to work.
    """
    service = object.__new__(RateLimitingSave)

    service.request = MagicMock()
    service.request.input = {
        'id': str(channel_id),
        'rules_json': dumps(rules),
    }

    # A simple namespace to hold opaque1 as a plain attribute
    mock_item = type('MockItem', (), {'opaque1': dumps(existing_opaque) if existing_opaque is not None else None})()

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.one.return_value = mock_item

    # closing() calls .close() on the returned object, so MagicMock handles that
    service.odb = MagicMock()
    service.odb.session.return_value = mock_session

    service.config_dispatcher = MagicMock()
    service.logger = logging.getLogger('test')

    return service, mock_item, mock_session

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingSaveTestCase(unittest.TestCase):

    def test_save_valid_rules(self):
        """ Valid rules are saved into opaque1['rate_limiting'].
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, mock_item, mock_session = _make_service(42, rules)

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
        service, mock_item, _ = _make_service(42, rules, existing_opaque=existing)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(saved_opaque['http_accept'], 'application/json')
        self.assertTrue(saved_opaque['some_flag'])
        self.assertIn('rate_limiting', saved_opaque)

    def test_save_empty_opaque_creates_dict(self):
        """ When opaque1 is None, a new dict is created.
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, mock_item, _ = _make_service(42, rules, existing_opaque=None)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertIn('rate_limiting', saved_opaque)

    def test_save_invalid_cidr_rejected(self):
        """ Invalid CIDR in rules raises RateLimitError before ODB write.
        """
        rules = [_make_rule(['not-a-cidr'], [_all_day_range()])]
        service, _, mock_session = _make_service(42, rules)

        with self.assertRaises(RateLimitError):
            service.handle()

        mock_session.commit.assert_not_called()

    def test_save_invalid_time_range_rejected(self):
        """ Invalid time range (missing is_all_day) raises before ODB write.
        """
        rules = [_make_rule(['10.0.0.0/8'], [{'rate': 10}])]
        service, _, mock_session = _make_service(42, rules)

        with self.assertRaises(KeyError):
            service.handle()

        mock_session.commit.assert_not_called()

    def test_save_multiple_rules(self):
        """ Multiple rules are all saved.
        """
        rules = [
            _make_rule(['10.0.0.0/8'], [_all_day_range()]),
            _make_rule(['192.168.0.0/16'], [_all_day_range(rate=50)]),
        ]
        service, mock_item, _ = _make_service(42, rules)

        service.handle()

        saved_opaque = loads(mock_item.opaque1)
        self.assertEqual(len(saved_opaque['rate_limiting']), 2)

    def test_save_publishes_config_event(self):
        """ After ODB commit, config_dispatcher.publish is called with the correct action and data.
        """
        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        service, _, _ = _make_service(42, rules)

        service.handle()

        service.config_dispatcher.publish.assert_called_once()

        call_args = service.config_dispatcher.publish.call_args[0][0]
        self.assertEqual(call_args['action'], CHANNEL.HTTP_SOAP_RATE_LIMITING_EDIT.value)
        self.assertEqual(call_args['id'], 42)
        self.assertEqual(len(call_args['rule_dicts']), 1)

    def test_save_does_not_publish_on_validation_error(self):
        """ If validation fails, config_dispatcher.publish must not be called.
        """
        rules = [_make_rule(['not-a-cidr'], [_all_day_range()])]
        service, _, _ = _make_service(42, rules)

        with self.assertRaises(RateLimitError):
            service.handle()

        service.config_dispatcher.publish.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
