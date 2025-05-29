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
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseIncludeFromYAML(TestCase):
    """ Tests the include functionality in enmasse YAML files.
    """

    def setUp(self) -> 'None':
        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir.name

        # Extract parts from template_complex_01 for different test files
        import yaml

        # Create the complete template file for comparison
        self.complete_file_path = os.path.join(self.base_dir, 'complete.yaml')
        with open(self.complete_file_path, 'w') as f:
            _ = f.write(template_complex_01)

        # Parse the template to extract sections
        template_data = yaml.safe_load(template_complex_01)

        # Extract security and groups for common_security.yaml
        security_content = {}
        if 'security' in template_data:
            security_content['security'] = template_data['security'][:3]  # Take first 3 security definitions
        if 'groups' in template_data:
            security_content['groups'] = template_data['groups'][:1]   # Take first group

        self.security_file_path = os.path.join(self.base_dir, 'common_security.yaml')
        with open(self.security_file_path, 'w') as f:
            yaml.dump(security_content, f)

        # Extract channels for channels.yaml
        channels_content = {}
        if 'channel_rest' in template_data:
            channels_content['channel_rest'] = template_data['channel_rest']

        self.channels_file_path = os.path.join(self.base_dir, 'channels.yaml')
        with open(self.channels_file_path, 'w') as f:
            yaml.dump(channels_content, f)

        # Extract scheduler for scheduler.yaml
        scheduler_content = {}
        if 'scheduler' in template_data:
            scheduler_content['scheduler'] = template_data['scheduler'][:2]  # Take first 2 scheduler jobs

        self.scheduler_file_path = os.path.join(self.base_dir, 'scheduler.yaml')
        with open(self.scheduler_file_path, 'w') as f:
            yaml.dump(scheduler_content, f)

        # Create main file that includes the other files
        main_content = {
            'include': ['common_security.yaml', 'channels.yaml', 'scheduler.yaml']
        }

        # Add outgoing_rest section to main file
        if 'outgoing_rest' in template_data:
            main_content['outgoing_rest'] = [template_data['outgoing_rest'][0]]  # Take first outgoing_rest

        self.main_file_path = os.path.join(self.base_dir, 'main.yaml')
        with open(self.main_file_path, 'w') as f:
            yaml.dump(main_content, f)

        # Create nested include test files
        # Extract LDAP for nested_include.yaml
        nested_include_content = {
            'include': ['common_security.yaml']
        }

        if 'ldap' in template_data:
            nested_include_content['ldap'] = template_data['ldap']

        self.nested_include_path = os.path.join(self.base_dir, 'nested_include.yaml')
        with open(self.nested_include_path, 'w') as f:
            yaml.dump(nested_include_content, f)

        # Create first level include file (nested_main.yaml)
        nested_main_content = {
            'include': ['nested_include.yaml']
        }

        if 'odoo' in template_data:
            nested_main_content['odoo'] = template_data['odoo']

        self.nested_main_path = os.path.join(self.base_dir, 'nested_main.yaml')
        with open(self.nested_main_path, 'w') as f:
            yaml.dump(nested_main_content, f)

        # Create circular include test files
        circular1_content = {
            'include': ['circular2.yaml']
        }

        if 'email_smtp' in template_data:
            circular1_content['email_smtp'] = template_data['email_smtp']

        self.circular1_path = os.path.join(self.base_dir, 'circular1.yaml')
        with open(self.circular1_path, 'w') as f:
            yaml.dump(circular1_content, f)

        circular2_content = {
            'include': ['circular1.yaml']
        }

        if 'email_imap' in template_data:
            circular2_content['email_imap'] = template_data['email_imap']

        self.circular2_path = os.path.join(self.base_dir, 'circular2.yaml')
        with open(self.circular2_path, 'w') as f:
            yaml.dump(circular2_content, f)

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

    def tearDown(self) -> 'None':
        self.temp_dir.cleanup()

    def test_basic_include(self):
        """ Test basic include functionality with multiple included files.
        """
        yaml_config = self.importer.from_path(self.main_file_path)

        # Verify that all sections from all files are present
        self.assertIn('security', yaml_config)
        self.assertIn('groups', yaml_config)
        self.assertIn('channel_rest', yaml_config)
        self.assertIn('scheduler', yaml_config)
        self.assertIn('outgoing_rest', yaml_config)

        # Verify correct number of items in each section
        self.assertEqual(len(yaml_config['security']), 3)  # From common_security.yaml
        self.assertEqual(len(yaml_config['groups']), 1)    # From common_security.yaml
        self.assertEqual(len(yaml_config['channel_rest']), 3)  # From channels.yaml
        self.assertEqual(len(yaml_config['scheduler']), 2)  # From scheduler.yaml
        self.assertEqual(len(yaml_config['outgoing_rest']), 1)  # From main.yaml

        # Verify cross-references between files work
        channel_with_security = yaml_config['channel_rest'][2]  # Third channel has security
        self.assertEqual(channel_with_security['name'], 'enmasse.channel.rest.3')
        self.assertEqual(channel_with_security['security'], 'enmasse.basic_auth.1')

    def test_nested_include(self):
        """ Test nested includes (files that include other files).
        """
        yaml_config = self.importer.from_path(self.nested_main_path)

        # Verify sections from all files including nested ones
        self.assertIn('security', yaml_config)
        self.assertIn('groups', yaml_config)
        self.assertIn('ldap', yaml_config)
        self.assertIn('odoo', yaml_config)

        # Verify correct number of items in each section
        self.assertEqual(len(yaml_config['security']), 3)  # From common_security.yaml via nested_include.yaml
        self.assertEqual(len(yaml_config['groups']), 1)    # From common_security.yaml via nested_include.yaml
        self.assertEqual(len(yaml_config['ldap']), 1)      # From nested_include.yaml
        self.assertEqual(len(yaml_config['odoo']), 1)      # From nested_main.yaml

        # Verify specific values to ensure correct merging
        self.assertEqual(yaml_config['ldap'][0]['name'], 'enmasse.ldap.1')
        self.assertEqual(yaml_config['odoo'][0]['name'], 'enmasse.odoo.1')

    def test_circular_include_detection(self):
        """ Test that circular includes are detected and raise an error.
        """
        circular1_path = os.path.join(self.base_dir, 'circular1.yaml')

        with self.assertRaises(ValueError) as cm:
            _ = self.importer.from_path(circular1_path)

        error_msg = str(cm.exception)
        self.assertIn('Circular include detected', error_msg)

    def test_nonexistent_include(self):
        """ Test that including a non-existent file raises an error.
        """
        # Create a file with a non-existent include
        bad_include_path = os.path.join(self.base_dir, 'bad_include.yaml')
        with open(bad_include_path, 'w') as f:
            _ = f.write("""
include:
  - this_file_does_not_exist.yaml
""")

        with self.assertRaises(ValueError) as cm:
            _ = self.importer.from_path(bad_include_path)

        error_msg = str(cm.exception)
        self.assertIn('does not exist', error_msg)

    def test_absolute_path_include(self):
        """ Test including a file using an absolute path.
        """
        # Create a file in a different directory
        other_dir = tempfile.TemporaryDirectory()
        try:
            import yaml
            template_data = yaml.safe_load(template_complex_01)

            # Create an absolute path include file with content from template_complex_01
            abs_include_content = {}
            if 'jira' in template_data:
                abs_include_content['jira'] = template_data['jira']

            abs_include_path = os.path.join(other_dir.name, 'absolute_include.yaml')
            with open(abs_include_path, 'w') as f:
                yaml.dump(abs_include_content, f)

            # Create a file that includes the absolute path
            abs_main_content = {
                'include': [abs_include_path]
            }

            if 'confluence' in template_data:
                abs_main_content['confluence'] = template_data['confluence']

            abs_main_path = os.path.join(self.base_dir, 'abs_main.yaml')
            with open(abs_main_path, 'w') as f:
                yaml.dump(abs_main_content, f)

            # Parse the file with the absolute include
            yaml_config = self.importer.from_path(abs_main_path)

            # Verify both sections are present
            self.assertIn('jira', yaml_config)
            self.assertIn('confluence', yaml_config)
            self.assertEqual(len(yaml_config['jira']), 1)
            self.assertEqual(len(yaml_config['confluence']), 1)
            self.assertEqual(yaml_config['jira'][0]['name'], 'enmasse.jira.1')
            self.assertEqual(yaml_config['confluence'][0]['name'], 'enmasse.confluence.1')
        finally:
            other_dir.cleanup()

    def test_complete_template(self):
        """ Test that the original complete template loads correctly.
        """
        # Load the complete template file
        complete_config = self.importer.from_path(self.complete_file_path)

        # Verify all major sections from template_complex_01 are present
        self.assertIn('security', complete_config)
        self.assertIn('groups', complete_config)
        self.assertIn('channel_rest', complete_config)
        self.assertIn('outgoing_rest', complete_config)
        self.assertIn('scheduler', complete_config)
        self.assertIn('ldap', complete_config)
        self.assertIn('sql', complete_config)
        self.assertIn('outgoing_soap', complete_config)
        self.assertIn('microsoft_365', complete_config)
        self.assertIn('cache', complete_config)
        self.assertIn('confluence', complete_config)
        self.assertIn('email_imap', complete_config)
        self.assertIn('email_smtp', complete_config)
        self.assertIn('jira', complete_config)
        self.assertIn('odoo', complete_config)

        # Verify the template has the expected number of each item
        self.assertEqual(len(complete_config['security']), 7)
        self.assertEqual(len(complete_config['groups']), 2)
        self.assertEqual(len(complete_config['channel_rest']), 3)
        self.assertEqual(len(complete_config['scheduler']), 4)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
