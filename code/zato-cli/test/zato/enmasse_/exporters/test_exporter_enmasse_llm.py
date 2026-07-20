# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.llm import LLMImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseLLMExport(TestCase):
    """ Tests exporting LLM connection definitions to YAML format.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()
        self.llm_importer = LLMImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_llm_export(self):
        self._setup_test_environment()

        llm_list_from_yaml = self.yaml_config['llm']

        created, _ = self.llm_importer.sync_definitions(llm_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('llm', exported_data)
        exported_llm_list = exported_data['llm']

        # Filter to only the test-created connections (DB may have pre-existing ones)
        test_created = []
        for item in exported_llm_list:
            if item['name'].startswith('enmasse.llm.'):
                test_created.append(item)

        exported_llm_list = test_created
        self.assertEqual(len(exported_llm_list), 2)

        exported_by_name = {}
        for item in exported_llm_list:
            exported_by_name[item['name']] = item

        for yaml_def in llm_list_from_yaml:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name)
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def['name'], yaml_def['name'])
            self.assertEqual(exported_def['address'], yaml_def['address'])
            self.assertEqual(exported_def['model'], yaml_def['model'])

        # Non-default values round-trip - exported when set, skipped when they are the defaults.
        exported_1 = exported_by_name['enmasse.llm.1']
        self.assertEqual(exported_1['timeout'], 30)
        self.assertEqual(exported_1['max_tokens'], 2048)
        self.assertEqual(exported_1['max_history_turns'], 10)
        self.assertEqual(exported_1['chat_expiry'], 3600)

        exported_2 = exported_by_name['enmasse.llm.2']
        self.assertNotIn('timeout', exported_2)
        self.assertNotIn('max_tokens', exported_2)
        self.assertNotIn('max_history_turns', exported_2)
        self.assertNotIn('chat_expiry', exported_2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging
    from unittest import main

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
