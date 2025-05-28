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
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel import ChannelImporter
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.common.odb.model import CacheBuiltin, Cluster
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCacheFromYAML(TestCase):
    """ Tests importing caches from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)
        self.channel_importer = ChannelImporter(self.importer)
        self.cache_importer = CacheImporter(self.importer)

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

    def test_create_cache_object(self):
        """ Test the basic creation of a cache object in the database.
        """
        self._setup_test_environment()

        cluster = self.session.query(Cluster).filter(Cluster.id==1).one()
        cluster.id = 1

        cache = CacheBuiltin()
        cache.cluster = cluster
        cache.name = 'enmasse.testing.1'
        cache.is_active = True
        cache.is_default = False

        self.session.add(cache)
        self.session.commit()

# ################################################################################################################################

    def test_yaml_cache_parsing(self):
        """ Test that cache definitions in YAML are parsed correctly.
        """
        self._setup_test_environment()

        # Verify the YAML contains cache definitions
        self.assertIn('cache', self.yaml_config)
        self.assertIsInstance(self.yaml_config['cache'], list)
        self.assertTrue(len(self.yaml_config['cache']) > 0, 'No cache definitions found in YAML')

# ################################################################################################################################

    def test_cache_definition_creation(self):
        """ Test creating cache definitions from YAML.
        """
        self._setup_test_environment()

        # Get cache definitions from YAML
        cache_defs = self.yaml_config.get('cache', [])
        self.assertTrue(len(cache_defs) > 0, 'No cache definitions found in YAML')

        # Process cache definitions
        cache_created, _ = self.cache_importer.sync_cache_definitions(cache_defs, self.session)

        # Update importer's cache definitions for other tests
        self.importer.cache_defs = self.cache_importer.cache_defs

        # Assert the correct number of items were created
        self.assertEqual(len(cache_created), len(cache_defs), 'Not all cache definitions were created')

        # Verify each definition was created correctly
        for instance in cache_created:
            self.assertTrue(instance.name.startswith('enmasse.cache.builtin.'))
            self.assertEqual(instance.cache_type, 'builtin')
            self.assertTrue(instance.is_active)
            self.assertFalse(instance.is_default)

            # Check if the instance has the expected attributes
            self.assertTrue(hasattr(instance, 'extend_expiry_on_get'))
            self.assertTrue(hasattr(instance, 'extend_expiry_on_set'))

# ################################################################################################################################

    def test_cache_comparison(self):
        """ Test comparing cache definitions between YAML and database.
        """
        self._setup_test_environment()

        # Get cache definitions from YAML
        cache_defs = self.yaml_config.get('cache', [])
        self.assertTrue(len(cache_defs) > 0, 'No cache definitions found in YAML')

        # Get cache definitions from database (initially empty)
        db_defs = self.cache_importer.get_cache_defs_from_db(self.session, self.importer.cluster_id)

        # Compare the definitions
        to_create, to_update = self.cache_importer.compare_cache_defs(cache_defs, db_defs) # type: ignore

        # All should be marked for creation since the database is empty
        self.assertEqual(len(to_create), len(cache_defs))
        self.assertEqual(len(to_update), 0)

        # Create the cache definitions
        _ = self.cache_importer.sync_cache_definitions(cache_defs, self.session)
        self.importer.cache_defs = self.cache_importer.cache_defs

        # Get cache definitions from database again (now should have the created items)
        db_defs = self.cache_importer.get_cache_defs_from_db(self.session, self.importer.cluster_id)

        # Compare the definitions again
        to_create, to_update = self.cache_importer.compare_cache_defs(cache_defs, db_defs) # type: ignore

        # Now none should be marked for creation, all should be for update
        self.assertEqual(len(to_create), 0)
        self.assertEqual(len(to_update), len(cache_defs))

# ################################################################################################################################

    def test_cache_default_values(self):
        """ Test that default values are applied correctly to cache definitions.
        """
        self._setup_test_environment()

        # Create a simple cache definition with minimal properties
        minimal_cache_def = {
            'name': 'enmasse.cache.minimal.test'
        }

        # Create the cache definition
        instance = self.cache_importer.create_cache_definition(minimal_cache_def, self.session)
        self.session.commit()

        # Verify default values were applied
        self.assertEqual(instance.name, 'enmasse.cache.minimal.test')
        self.assertEqual(instance.cache_type, 'builtin')
        self.assertTrue(instance.is_active)
        self.assertFalse(instance.is_default)
        self.assertEqual(instance.max_size, 10000)
        self.assertEqual(instance.max_item_size, 1000000)
        self.assertTrue(instance.extend_expiry_on_get)
        self.assertFalse(instance.extend_expiry_on_set)
        self.assertEqual(instance.sync_method, 'in-background')
        self.assertEqual(instance.persistent_storage, 'sqlite')

# ################################################################################################################################

    def test_cache_update(self):
        """ Test updating existing cache definitions.
        """
        self._setup_test_environment()

        # Get cache definition from YAML
        cache_defs = self.yaml_config['cache']
        cache_def = cache_defs[0]
        
        # Create the cache definition
        instance = self.cache_importer.create_cache_definition(cache_def, self.session)
        self.session.commit()
        original_name = cache_def['name']
        self.assertEqual(instance.name, original_name)

        # Update the cache definition
        update_def = {
            'name': original_name,
            'id': instance.id,
            'max_size': 8000,
            'extend_expiry_on_get': False
        }

        updated_instance = self.cache_importer.update_cache_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.max_size, 8000)
        self.assertFalse(updated_instance.extend_expiry_on_get)

# ################################################################################################################################

    def test_complete_cache_import_flow(self):
        """ Test the complete flow of importing cache definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all cache definitions from the YAML
        cache_list = self.yaml_config.get('cache', [])
        cache_created, cache_updated = self.cache_importer.sync_cache_definitions(cache_list, self.session)

        # Update importer's cache definitions
        self.importer.cache_defs = self.cache_importer.cache_defs

        # Verify cache definitions were created
        self.assertEqual(len(cache_created), len(cache_list))
        self.assertEqual(len(cache_updated), 0)

        # Verify the cached definitions dictionary was populated
        self.assertEqual(len(self.cache_importer.cache_defs), len(cache_list))

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.cache_defs), len(cache_list))

        # Try importing the same definitions again - should result in updates, not creations
        cache_created2, cache_updated2 = self.cache_importer.sync_cache_definitions(cache_list, self.session)
        self.assertEqual(len(cache_created2), 0)
        self.assertEqual(len(cache_updated2), len(cache_list))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
