# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from json import loads
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.common.api import EMAIL
from zato.common.odb.model import IMAP, IntervalBasedJob, Job
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseEmailIMAPFromYAML(TestCase):
    """ Tests importing IMAP connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file using the existing template which already contains connection definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize IMAP importer
        self.imap_importer = IMAPImporter(self.importer)

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

    def test_imap_definition_creation(self):
        """ Test creating IMAP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        imap_defs = self.yaml_config['email_imap']

        # Process all IMAP definitions
        created, updated = self.imap_importer.sync_imap_definitions(imap_defs, self.session)

        # Should have created 2 definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify IMAP connection was created correctly
        imap = self.session.query(IMAP).filter_by(name='enmasse.email.imap.1').one()  # type: ignore
        self.assertEqual(imap.host, 'imap.example.com')
        self.assertEqual(imap.port, 993)
        self.assertEqual(imap.username, 'enmasse@example.com')
        self.assertEqual(imap.mode, 'plain')
        self.assertTrue(hasattr(imap, 'password'))

# ################################################################################################################################

    def test_imap_scheduler_job_creation(self):
        """ Test that an IMAP connection with scheduler fields auto-creates a linked scheduler job.
        """
        self._setup_test_environment()

        # Process all IMAP definitions, one of which carries scheduler fields
        imap_defs = self.yaml_config['email_imap']
        _ = self.imap_importer.sync_imap_definitions(imap_defs, self.session)

        # The connection with scheduler fields must point to its auto-created job
        imap = self.session.query(IMAP).filter_by(name='enmasse.email.imap.2').one() # type: ignore
        imap_opaque = parse_instance_opaque_attr(imap)

        self.assertEqual(imap_opaque['scheduler_run_every'], 5)
        self.assertEqual(imap_opaque['scheduler_run_unit'], 'minutes')
        self.assertEqual(imap_opaque['scheduler_service'], 'demo.ping')
        self.assertEqual(imap_opaque['scheduler_invoke_with'], 'each_attachment')

        # The job itself must exist under the conventional name and invoke the dispatch service ..
        scheduler_common = EMAIL.IMAP.Scheduler
        job = self.session.query(Job).filter_by(name='imap.enmasse.email.imap.2').one() # type: ignore
        self.assertEqual(imap_opaque['scheduler_job_id'], job.id)
        self.assertEqual(job.job_type, 'interval_based')
        self.assertEqual(job.service.name, scheduler_common.Dispatch_Service)

        # .. its extra data must carry the connection's identity, the per-message service
        # .. and the invoke-with mode ..
        extra = loads(job.extra)
        self.assertEqual(extra[scheduler_common.Extra_Conn_ID], imap.id)
        self.assertEqual(extra[scheduler_common.Extra_Conn_Name], 'enmasse.email.imap.2')
        self.assertEqual(extra[scheduler_common.Extra_Service], 'demo.ping')
        self.assertEqual(extra[scheduler_common.Extra_Invoke_With], 'each_attachment')

        # .. it must point back to its connection ..
        job_opaque = parse_instance_opaque_attr(job)
        self.assertEqual(job_opaque['imap_conn_id'], imap.id)

        # .. and its interval must match the run-every configuration.
        interval = self.session.query(IntervalBasedJob).filter_by(job_id=job.id).one() # type: ignore
        self.assertEqual(interval.minutes, 5)
        self.assertEqual(interval.seconds, 0)
        self.assertEqual(interval.hours, 0)
        self.assertEqual(interval.days, 0)

        # Importing again must update the same job rather than create a new one
        _ = self.imap_importer.sync_imap_definitions(imap_defs, self.session)

        job_count = self.session.query(Job).filter_by(name='imap.enmasse.email.imap.2').count() # type: ignore
        self.assertEqual(job_count, 1)

# ################################################################################################################################

    def test_imap_update(self):
        """ Test updating existing IMAP connection definitions.
        """
        self._setup_test_environment()

        # First, get the IMAP definition from YAML and create it
        imap_defs = self.yaml_config['email_imap']
        imap_def = imap_defs[0]

        # Create the IMAP definition
        instance = self.imap_importer.create_imap_definition(imap_def, self.session)
        self.session.commit()
        original_host = imap_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': imap_def['name'],
            'id': instance.id,
            'host': 'imap-updated.example.com',  # Changed host
            'port': 143,  # Changed port
            'mode': 'plain'  # Changed mode
        }

        # Update the IMAP definition
        updated_instance = self.imap_importer.update_imap_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'imap-updated.example.com')
        self.assertEqual(updated_instance.port, 143)
        self.assertEqual(updated_instance.mode, 'plain')

        # Make sure other fields were preserved from the original YAML definition
        self.assertEqual(updated_instance.username, imap_def['username'])

        # Only check get_criteria if it exists in the definition
        if 'get_criteria' in imap_def:
            self.assertEqual(updated_instance.get_criteria, imap_def['get_criteria'])

# ################################################################################################################################

    def test_complete_imap_import_flow(self):
        """ Test the complete flow of importing IMAP connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all IMAP definitions from the YAML
        imap_list = self.yaml_config['email_imap']
        imap_created, imap_updated = self.imap_importer.sync_imap_definitions(imap_list, self.session)

        # Update importer's IMAP definitions
        self.importer.imap_defs = self.imap_importer.imap_defs

        # Verify IMAP definitions were created
        self.assertEqual(len(imap_created), 2)
        self.assertEqual(len(imap_updated), 0)

        # Verify the IMAP definitions dictionary was populated
        self.assertEqual(len(self.imap_importer.imap_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.imap_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        imap_created2, imap_updated2 = self.imap_importer.sync_imap_definitions(imap_list, self.session)
        self.assertEqual(len(imap_created2), 0)
        self.assertEqual(len(imap_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
