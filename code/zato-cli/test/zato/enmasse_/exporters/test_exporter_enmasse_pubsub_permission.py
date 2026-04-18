# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import yaml

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmassePubSubPermissionExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.config_manager.load_yaml_string(template_complex_01)

    def test_pubsub_permission_export(self):

        exporter = EnmasseExporter(self.config_manager)
        exported_data = exporter.export_to_dict()

        self.assertIn('pubsub_permission', exported_data, 'Exporter did not produce a "pubsub_permission" section.')
        exported_permissions = exported_data['pubsub_permission']

        template_dict = yaml.safe_load(template_complex_01)

        expected_permissions = {}
        for perm_def in template_dict['pubsub_permission']:
            security_name = perm_def['security']
            expected_permissions[security_name] = perm_def

        exported_by_security = {perm['security']: perm for perm in exported_permissions}

        for security_name, expected in expected_permissions.items():
            self.assertIn(security_name, exported_by_security,
                f'Expected security {security_name} not found in export')

            perm_group = exported_by_security[security_name]

            if 'pub' in expected:
                self.assertIn('pub', perm_group)
                self.assertEqual(set(perm_group['pub']), set(expected['pub']))

            if 'sub' in expected:
                self.assertIn('sub', perm_group)
                self.assertEqual(set(perm_group['sub']), set(expected['sub']))

        if 'enmasse.basic_auth.1' in exported_by_security:
            auth1_perms = exported_by_security['enmasse.basic_auth.1']
            self.assertIn('pub', auth1_perms)
            self.assertIn('sub', auth1_perms)
            self.assertEqual(set(auth1_perms['pub']), {'enmasse.topic.1', 'enmasse.topic.2'})
            self.assertEqual(set(auth1_perms['sub']), {'enmasse.topic.2', 'enmasse.topic.3'})

        if 'enmasse.basic_auth.2' in exported_by_security:
            auth2_perms = exported_by_security['enmasse.basic_auth.2']
            self.assertIn('pub', auth2_perms)
            self.assertIn('sub', auth2_perms)
            self.assertEqual(auth2_perms['pub'], ['enmasse.topic.*'])
            self.assertEqual(auth2_perms['sub'], ['enmasse.#'])

        if 'enmasse.basic_auth.3' in exported_by_security:
            auth3_perms = exported_by_security['enmasse.basic_auth.3']
            self.assertNotIn('pub', auth3_perms)
            self.assertIn('sub', auth3_perms)
            self.assertEqual(auth3_perms['sub'], ['enmasse.topic.3'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
