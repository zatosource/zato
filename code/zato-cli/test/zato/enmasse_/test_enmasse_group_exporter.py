# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.apikey import APIKeyImporter
from zato.cli.enmasse.importers.basic_auth import BasicAuthImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, SASession

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseGroupExporter(TestCase):
    """ Tests exporting Security Group definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.apikey_importer = APIKeyImporter(self.importer)
        self.basic_auth_importer = BasicAuthImporter(self.importer)
        self.group_importer = GroupImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import security definitions first, as groups depend on them
        security_defs_from_yaml = self.yaml_config.get('security', [])
        if security_defs_from_yaml:

            apikey_defs = [item for item in security_defs_from_yaml if item.get('type') == 'apikey']
            basic_auth_defs = [item for item in security_defs_from_yaml if item.get('type') == 'basic_auth']

            if apikey_defs:
                _, _ = self.apikey_importer.sync_apikey_definitions(apikey_defs, self.session)

            if basic_auth_defs:
                _, _ = self.basic_auth_importer.sync_basic_auth_definitions(basic_auth_defs, self.session)

        # Import group definitions
        groups_from_yaml = self.yaml_config.get('groups', [])
        if groups_from_yaml:
            _, _ = self.group_importer.sync_group_definitions(groups_from_yaml, self.session)

        self.session.commit()

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
