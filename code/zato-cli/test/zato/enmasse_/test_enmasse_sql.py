# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.common.odb.model import SQLConnectionPool
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSQLFromYAML(TestCase):
    """ Tests importing SQL connection pool definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize SQL importer
        self.sql_importer = SQLImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

    def test_sql_definition_creation(self):
        """ Test creating SQL connection pool definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        sql_defs = self.yaml_config['sql']

        # Process all SQL definitions
        created, updated = self.sql_importer.sync_sql_definitions(sql_defs, self.session)

        # Should have created 2 definitions (based on the number in the template)
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify SQL connection was created correctly
        sql = self.session.query(SQLConnectionPool).filter_by(name='enmasse.sql.1').one()
        self.assertEqual(sql.host, '127.0.0.1')
        self.assertEqual(sql.port, 3306)
        self.assertEqual(sql.username, 'enmasse.1')
        self.assertEqual(sql.db_name, 'MYDB_01')
        self.assertEqual(sql.engine, 'mysql')
        self.assertTrue(hasattr(sql, 'password'))

    def test_sql_update(self):
        """ Test updating existing SQL connection pool definitions.
        """
        self._setup_test_environment()

        # First, get the SQL definition from YAML and create it
        sql_defs = self.yaml_config['sql']
        sql_def = sql_defs[0]

        # Create the SQL definition
        instance = self.sql_importer.create_sql_definition(sql_def, self.session)
        self.session.commit()
        original_host = sql_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': sql_def['name'],
            'id': instance.id,
            'host': 'sql-updated.example.com',  # Changed host
            'port': 5433  # Changed port
        }

        # Update the SQL definition
        updated_instance = self.sql_importer.update_sql_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'sql-updated.example.com')
        self.assertEqual(updated_instance.port, 5433)

        # Make sure other fields were preserved from the original YAML definition
        self.assertEqual(updated_instance.username, sql_def['username'])
        self.assertEqual(updated_instance.db_name, sql_def['db_name'])
        self.assertEqual(updated_instance.engine, sql_def['type'])

    def test_complete_sql_import_flow(self):
        """ Test the complete flow of importing SQL connection pool definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all SQL definitions from the YAML
        sql_list = self.yaml_config.get('sql', [])
        sql_created, sql_updated = self.sql_importer.sync_sql_definitions(sql_list, self.session)

        # Update importer's SQL definitions
        self.importer.sql_defs = self.sql_importer.sql_defs

        # Verify SQL definitions were created
        self.assertEqual(len(sql_created), 1)
        self.assertEqual(len(sql_updated), 0)

        # Verify the SQL definitions dictionary was populated
        self.assertEqual(len(self.sql_importer.sql_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.sql_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        sql_created2, sql_updated2 = self.sql_importer.sync_sql_definitions(sql_list, self.session)
        self.assertEqual(len(sql_created2), 0)
        self.assertEqual(len(sql_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
