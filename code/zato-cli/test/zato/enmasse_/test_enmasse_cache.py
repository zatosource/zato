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
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.common.odb.model import CacheBuiltin
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCacheFromYAML(TestCase):
    """ Tests importing cache configurations from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Parse the YAML file - but don't initialize importers here
        # Each test will create its own fresh importers
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            # Explicitly delete any cache entries we've created before closing
            self.session.execute('DELETE FROM cache_builtin')
            self.session.execute('DELETE FROM cache')
            self.session.commit()
            self.session.close()
            
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)
            # Ensure we have a test cluster in the database
            from zato.common.odb.model import Cluster
            cluster = self.session.query(Cluster).filter_by(id=1).first()
            if not cluster:
                cluster = Cluster()
                cluster.id = 1
                cluster.name = 'test'
                self.session.add(cluster)
                self.session.commit()

        if not self.yaml_config:
            # Create a temporary importer just for parsing the YAML
            temp_importer = EnmasseYAMLImporter()
            self.yaml_config = temp_importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_yaml_parsing(self):
        """ Test that the YAML file is parsed correctly.
        """
        self._setup_test_environment()

        # Verify the YAML was parsed correctly
        self.assertIn('cache', self.yaml_config)
        self.assertIsInstance(self.yaml_config['cache'], list)

# ################################################################################################################################

    def test_cache_creation(self):
        """ Test the creation of cache definitions.
        """
        self._setup_test_environment()

        # Create fresh importer instances for this test
        importer = EnmasseYAMLImporter()
        cache_importer = CacheImporter(importer)

        # Create a modified copy of cache definitions with a unique prefix for this test
        cache_list = self.yaml_config['cache']
        test_cache_list = []
        
        for idx, cache_def in enumerate(cache_list):
            # Create a deep copy to avoid modifying the original
            import copy
            test_cache = copy.deepcopy(cache_def)
            # Use a unique name for this test
            test_cache['name'] = f'test_creation_{idx}'
            test_cache_list.append(test_cache)
            
        # Process cache definitions with unique names
        try:
            cache_created, _ = cache_importer.sync_cache_definitions(test_cache_list, self.session)
            
            # Assert the correct number of items were created
            self.assertEqual(len(cache_created), len(test_cache_list), 'Not all cache definitions were created')

            # Verify each definition was created correctly
            for instance in cache_created:
                self.assertIn(instance.name, cache_importer.cache_defs)
                self.assertTrue(instance.name.startswith('enmasse.cache.builtin.'))
                
                # Check if attributes were properly set
                self.assertTrue(hasattr(instance, 'extend_expiry_on_get'))
        except Exception as e:
            self.session.rollback()
            raise

# ################################################################################################################################

    def test_complete_import_flow(self):
        """ Test the complete flow of importing all definitions from a YAML file.
        """
        self._setup_test_environment()

        # Create a modified copy of the YAML config with unique cache names
        import copy
        test_yaml_config = copy.deepcopy(self.yaml_config)
        
        # Modify cache definitions to have unique names
        if 'cache' in test_yaml_config:
            for idx, cache_def in enumerate(test_yaml_config['cache']):
                cache_def['name'] = f'test_flow_{idx}'
                
        # Create fresh importer instances for this test
        importer = EnmasseYAMLImporter()
        
        try:
            # Process the complete YAML configuration
            importer.sync_from_yaml(test_yaml_config, self.session)

            # Verify cache definitions were created
            self.assertTrue(len(importer.cache_defs) > 0, 'No cache definitions were created')

            # Check that we have the expected number of cache definitions
            self.assertEqual(len(importer.cache_defs), len(test_yaml_config['cache']))
        except Exception as e:
            self.session.rollback()
            raise

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()


