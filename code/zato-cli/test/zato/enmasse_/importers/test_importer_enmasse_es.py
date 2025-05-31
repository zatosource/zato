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
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.common.odb.model import ElasticSearch
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseElasticSearchFromYAML(TestCase):
    """ Tests importing ElasticSearch connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains connection definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize ElasticSearch importer
        self.es_importer = ElasticSearchImporter(self.importer)

        # Parse the YAML file
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
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_es_definition_creation(self):
        """ Test creating ElasticSearch connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        es_defs = self.yaml_config['elastic_search']

        # Process all ElasticSearch definitions
        created, updated = self.es_importer.sync_es_definitions(es_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify ElasticSearch connection was created correctly
        es = self.session.query(ElasticSearch).filter_by(name='enmasse.elastic.1').one()  # type: ignore
        self.assertEqual(es.hosts, 'http://elasticsearch:9200')
        self.assertEqual(es.timeout, 60)
        self.assertEqual(es.body_as, 'json')
        self.assertTrue(es.is_active)

# ################################################################################################################################

    def test_es_update(self):
        """ Test updating existing ElasticSearch connection definitions.
        """
        self._setup_test_environment()

        # First, get the ElasticSearch definition from YAML and create it
        es_defs = self.yaml_config['elastic_search']
        es_def = es_defs[0]

        # Create the ElasticSearch definition
        instance = self.es_importer.create_es_definition(es_def, self.session)
        self.session.commit()
        original_hosts = es_def['hosts']
        self.assertEqual(instance.hosts, original_hosts)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': es_def['name'],
            'id': instance.id,
            'hosts': 'http://elasticsearch-updated:9200',  # Changed hosts
            'timeout': 30,  # Changed timeout
            'body_as': 'raw'  # Changed body_as
        }

        # Update the ElasticSearch definition
        updated_instance = self.es_importer.update_es_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.hosts, 'http://elasticsearch-updated:9200')
        self.assertEqual(updated_instance.timeout, 30)
        self.assertEqual(updated_instance.body_as, 'raw')

        # Make sure name was preserved
        self.assertEqual(updated_instance.name, es_def['name'])

# ################################################################################################################################

    def test_complete_es_import_flow(self):
        """ Test the complete flow of importing ElasticSearch connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all ElasticSearch definitions from the YAML
        es_list = self.yaml_config['elastic_search']
        es_created, es_updated = self.es_importer.sync_es_definitions(es_list, self.session)

        # Update importer's ElasticSearch definitions
        self.importer.es_defs = self.es_importer.es_defs

        # Verify ElasticSearch definitions were created
        self.assertEqual(len(es_created), 1)
        self.assertEqual(len(es_updated), 0)

        # Verify the ElasticSearch definitions dictionary was populated
        self.assertEqual(len(self.es_importer.es_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.es_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        es_created2, es_updated2 = self.es_importer.sync_es_definitions(es_list, self.session)
        self.assertEqual(len(es_created2), 0)
        self.assertEqual(len(es_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
