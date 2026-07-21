# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.llm import LLMImporter
from zato.common.api import GENERIC, LLM
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseLLMFromYAML(TestCase):
    """ Tests importing LLM connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.llm_importer = LLMImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_llm_creation(self):
        self._setup_test_environment()

        llm_defs = self.yaml_config['llm']
        created, updated = self.llm_importer.sync_definitions(llm_defs, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        conn = self.session.query(GenericConn).filter_by(
            name='enmasse.llm.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_LLM,
        ).one()
        self.assertTrue(conn.is_active)
        self.assertEqual(conn.address, 'https://api.openai.com/v1')

        # The timeout is a column on the ODB model rather than an opaque attribute ..
        self.assertEqual(conn.timeout, 30)

        # .. while the remaining fields from YAML land in the opaque configuration.
        opaque = parse_instance_opaque_attr(conn)
        self.assertEqual(opaque['model'], 'gpt-4o-mini')
        self.assertEqual(opaque['max_tokens'], 2048)
        self.assertEqual(opaque['max_history_turns'], 10)
        self.assertEqual(opaque['chat_expiry'], 3600)

        # A connection without the keys in YAML gets the defaults.
        conn2 = self.session.query(GenericConn).filter_by(
            name='enmasse.llm.2',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_LLM,
        ).one()

        self.assertEqual(conn2.timeout, LLM.DEFAULT.TIMEOUT)

        opaque2 = parse_instance_opaque_attr(conn2)
        self.assertEqual(opaque2['model'], 'Sonnet 5')
        self.assertEqual(opaque2['max_tokens'], LLM.DEFAULT.MAX_TOKENS)
        self.assertEqual(opaque2['max_history_turns'], LLM.DEFAULT.MAX_HISTORY_TURNS)
        self.assertEqual(opaque2['chat_expiry'], LLM.DEFAULT.CHAT_EXPIRY)

# ################################################################################################################################

    def test_llm_update(self):
        self._setup_test_environment()

        llm_defs = self.yaml_config['llm']
        llm_def = llm_defs[0]

        instance = self.llm_importer.create_definition(llm_def, self.session)
        self.session.commit()

        update_def = {
            'name': llm_def['name'],
            'id': instance.id,
            'address': 'https://llm.example.com/v1',
            'model': 'gpt-4o',
        }

        updated_instance = self.llm_importer.update_definition(update_def, self.session)
        self.session.commit()

        self.assertEqual(updated_instance.name, llm_def['name'])
        self.assertEqual(updated_instance.address, 'https://llm.example.com/v1')

# ################################################################################################################################

    def test_complete_llm_import_flow(self):
        self._setup_test_environment()

        llm_list = self.yaml_config['llm']
        created, updated = self.llm_importer.sync_definitions(llm_list, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self.llm_importer.sync_definitions(llm_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
