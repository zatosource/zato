# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - must run before threading is imported by the module under test
from gevent import monkey

if not monkey.is_module_patched('threading'):
    _ = monkey.patch_all()

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.api import URL_TYPE
from zato.server.connection.http_soap.response_cache import parse_config

# ################################################################################################################################
# ################################################################################################################################

class ConfigParsingTestCase(TestCase):

    def test_defaults_applied(self) -> 'None':
        config = parse_config({}, URL_TYPE.PLAIN_HTTP)

        self.assertFalse(config.is_enabled)
        self.assertEqual(config.ttl_seconds, 5 * 60)
        self.assertFalse(config.is_shared_across_callers)
        self.assertEqual(config.vary_by_headers, [])
        self.assertEqual(config.ignored_query_parameters, [])
        self.assertFalse(config.include_body_in_key)
        self.assertEqual(config.max_body_size, 1_000_000)
        self.assertTrue(config.cache_on_second_request)
        self.assertFalse(config.needs_etag)
        self.assertEqual(config.coalesce_timeout, 15)

# ################################################################################################################################

    def test_ttl_unit_conversion(self) -> 'None':
        config = parse_config({'ttl': 2, 'ttl_unit': 'minutes'}, URL_TYPE.PLAIN_HTTP)
        self.assertEqual(config.ttl_seconds, 120)

        config = parse_config({'ttl': 3, 'ttl_unit': 'hours'}, URL_TYPE.PLAIN_HTTP)
        self.assertEqual(config.ttl_seconds, 3 * 3600)

        config = parse_config({'ttl': 45, 'ttl_unit': 'seconds'}, URL_TYPE.PLAIN_HTTP)
        self.assertEqual(config.ttl_seconds, 45)

# ################################################################################################################################

    def test_unknown_ttl_unit_raises(self) -> 'None':
        with self.assertRaises(Exception) as ctx:
            _ = parse_config({'ttl_unit': 'fortnights'}, URL_TYPE.PLAIN_HTTP)

        self.assertIn('fortnights', str(ctx.exception))

# ################################################################################################################################

    def test_soap_always_includes_body_in_key(self) -> 'None':
        config = parse_config({'include_body_in_key': False}, URL_TYPE.SOAP)
        self.assertTrue(config.include_body_in_key)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
