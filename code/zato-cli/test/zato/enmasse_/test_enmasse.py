# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import basicConfig, getLogger, WARN
from unittest import TestCase, main

# PyYAML
import yaml

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseTestCase(TestCase):

    def setUp(self) -> 'None':
        self.cs = ConfigStore()

# ################################################################################################################################

    def test_enmasse_complex_ok_01(self) -> 'None':
        """ Load the complex template into ConfigStore and verify the round-trip.
        """
        self.cs.load_yaml_string(template_complex_01)
        exported = self.cs.export_to_dict()

        self.assertIn('security', exported)
        self.assertIn('channel_rest', exported)
        self.assertIn('outgoing_rest', exported)
        self.assertIn('scheduler', exported)
        self.assertIn('cache', exported)

        self.assertEqual(len(exported['security']), 8)
        self.assertEqual(len(exported['channel_rest']), 4)
        self.assertEqual(len(exported['outgoing_rest']), 5)
        self.assertEqual(len(exported['scheduler']), 4)
        self.assertEqual(len(exported['cache']), 1)

# ################################################################################################################################

    def test_enmasse_idempotent(self) -> 'None':
        """ Load the same YAML twice - second load should be idempotent.
        """
        self.cs.load_yaml_string(template_complex_01)
        self.cs.load_yaml_string(template_complex_01)

        exported = self.cs.export_to_dict()

        self.assertEqual(len(exported['security']), 8)
        self.assertEqual(len(exported['channel_rest']), 4)
        self.assertEqual(len(exported['outgoing_rest']), 5)

# ################################################################################################################################

    def test_enmasse_import_export_flow(self) -> 'None':
        """ Load YAML, export to dict, re-export to YAML, re-import - verify consistency.
        """
        self.cs.load_yaml_string(template_complex_01)
        exported = self.cs.export_to_dict()

        yaml_output = yaml.dump(exported, default_flow_style=False)

        cs2 = ConfigStore()
        cs2.load_yaml_string(yaml_output)
        exported2 = cs2.export_to_dict()

        for key in exported:
            self.assertIn(key, exported2)
            self.assertEqual(
                len(exported[key]),
                len(exported2[key]),
                f'Mismatch in item count for key={key}'
            )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
