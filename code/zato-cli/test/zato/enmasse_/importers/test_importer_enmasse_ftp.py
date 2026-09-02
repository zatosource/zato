# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sys
import tempfile
from unittest import TestCase, main

# PyYAML
import yaml

# Bunch
from zato.common.ext.bunch import bunchify

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.ftp import FTPImporter
from zato.common.api import FileTransfer, GENERIC, SchedulerLink
from zato.common.odb.model import GenericConn, Job
from zato.common.test.ftp_ import FTPTestServer
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.generic.api.outconn_ftp import FTPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Letters from three alphabets - one of the connections below uses them all in its name.
Dutch_Letters  = 'ÁÉÍÓÚË'
Greek_Letters  = 'ΑΒΓΔΕΖ'
Korean_Letters = 'ㄱㄴㄷㄹㅁㅂ'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_FTP'
    Conn_Name           = 'enmasse.ftp.1'
    Unicode_Conn_Name   = 'enmasse.ftp.' + Dutch_Letters + '.' + Greek_Letters + '.' + Korean_Letters + '.1'
    TLS_Conn_Name       = 'enmasse.ftp.tls.1'

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseFTPFromYAML(TestCase):
    """ Tests importing FTP connection definitions from YAML files using enmasse,
    against dynamically started FTP servers - a plain one and an FTPS one.
    """

    ftp_server: 'FTPTestServer'
    ftps_server: 'FTPTestServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.ftp_server = FTPTestServer()
        class_.ftp_server.start()

        class_.ftps_server = FTPTestServer(use_ssl=True)
        class_.ftps_server.start()

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.ftp_server.stop()
        class_.ftps_server.stop()

# ################################################################################################################################

    def setUp(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            self.skipTest('Env. key Zato_Test_FTP is not set')

        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # The YAML configuration with three connections - an ASCII-named one, a Unicode-named one
        # and one that speaks FTPS.
        yaml_dict = self.get_yaml_dict()
        yaml_data = yaml.safe_dump(yaml_dict, allow_unicode=True)

        # Create a temporary file with the configuration.
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        yaml_bytes = yaml_data.encode('utf-8')
        _ = self.temp_file.write(yaml_bytes)
        self.temp_file.close()

        # Initialize the importer.
        self.importer = EnmasseYAMLImporter()

        # Initialize FTP importer.
        self.ftp_importer = FTPImporter(self.importer)

        # Placeholders that _setup_test_environment fills in later.
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def get_yaml_dict(self) -> 'stranydict':

        # A connection with a plain ASCII name - it also keeps the bytes of the files it moves ..
        ascii_named = {
            'name': ModuleCtx.Conn_Name,
            'host': self.ftp_server.host,
            'port': self.ftp_server.port,
            'username': self.ftp_server.username,
            'password': self.ftp_server.password,
            'should_store_content': True,
        }

        # .. one whose name contains Dutch, Greek and Korean letters ..
        unicode_named = {
            'name': ModuleCtx.Unicode_Conn_Name,
            'host': self.ftp_server.host,
            'port': self.ftp_server.port,
            'username': self.ftp_server.username,
            'password': self.ftp_server.password,
        }

        # .. and one that speaks FTPS to a server requiring TLS.
        tls_named = {
            'name': ModuleCtx.TLS_Conn_Name,
            'host': self.ftps_server.host,
            'port': self.ftps_server.port,
            'username': self.ftps_server.username,
            'password': self.ftps_server.password,
            'use_ssl': True,
        }

        out = {'ftp': [ascii_named, unicode_named, tls_named]}

        return out

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def _build_client_from_instance(self, instance:'any_') -> 'FTPClient':
        """ Builds an FTPClient out of what was actually stored in the database for the input connection.
        """

        # The host and the SSL flag live in the instance's opaque attributes.
        opaque = parse_instance_opaque_attr(instance)

        config = bunchify({
            'id': instance.id,
            'name': instance.name,
            'is_active': True,
            'host': opaque.host,
            'port': instance.port,
            'username': instance.username,
            'secret': instance.secret,
            'use_ssl': opaque.use_ssl,
        })

        server = cast_('any_', None)
        out = FTPClient(config, server)

        return out

# ################################################################################################################################

    def test_ftp_definition_creation(self) -> 'None':
        """ Test creating FTP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML.
        ftp_defs = self.yaml_config['ftp']

        # Process all FTP definitions.
        created, updated = self.ftp_importer.sync_definitions(ftp_defs, self.session)

        # All three definitions were created.
        self.assertEqual(len(created), 3)
        self.assertEqual(len(updated), 0)

        # Verify each plain connection was created correctly, the Unicode name included.
        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_FTP
            ).one()

            opaque = parse_instance_opaque_attr(instance)

            self.assertEqual(opaque.host, self.ftp_server.host)
            self.assertEqual(instance.port, self.ftp_server.port)
            self.assertEqual(instance.username, self.ftp_server.username)
            self.assertEqual(instance.secret, self.ftp_server.password)

            # Nothing turned SSL on for these two.
            self.assertIs(opaque.use_ssl, False)

        # The first connection turned content storage on, the second one left it off by default.
        ascii_instance = self.session.query(GenericConn).filter_by(
            name=ModuleCtx.Conn_Name,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_FTP
        ).one()
        ascii_opaque = parse_instance_opaque_attr(ascii_instance)
        ascii_should_store_content = ascii_opaque['should_store_content']
        self.assertIs(ascii_should_store_content, True)

        unicode_instance = self.session.query(GenericConn).filter_by(
            name=ModuleCtx.Unicode_Conn_Name,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_FTP
        ).one()
        unicode_opaque = parse_instance_opaque_attr(unicode_instance)
        unicode_should_store_content = unicode_opaque['should_store_content']
        self.assertIs(unicode_should_store_content, False)

        # The third connection turned SSL on.
        tls_instance = self.session.query(GenericConn).filter_by(
            name=ModuleCtx.TLS_Conn_Name,
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_FTP
        ).one()
        tls_opaque = parse_instance_opaque_attr(tls_instance)
        tls_use_ssl = tls_opaque['use_ssl']
        self.assertIs(tls_use_ssl, True)

# ################################################################################################################################

    def test_ftp_live_ping_after_import(self) -> 'None':
        """ Test that all imported connections actually work against the live servers -
        the plain ones and the FTPS one alike.
        """
        self._setup_test_environment()

        # Import all the definitions first.
        ftp_defs = self.yaml_config['ftp']
        created, _ = self.ftp_importer.sync_definitions(ftp_defs, self.session)
        self.assertEqual(len(created), 3)

        for name in [ModuleCtx.Conn_Name, ModuleCtx.Unicode_Conn_Name, ModuleCtx.TLS_Conn_Name]:

            instance = self.session.query(GenericConn).filter_by(
                name=name,
                type_=GENERIC.CONNECTION.TYPE.OUTCONN_FTP
            ).one()

            # Build a client out of the imported connection ..
            client = self._build_client_from_instance(instance)

            # .. and a live ping must succeed.
            client.ping()

# ################################################################################################################################

    def test_ftp_update(self) -> 'None':
        """ Test updating existing FTP connection definitions.
        """
        self._setup_test_environment()

        # First, get the FTP definition from YAML and create it.
        ftp_defs = self.yaml_config['ftp']
        ftp_def = ftp_defs[0]

        # Create the FTP definition.
        instance = self.ftp_importer.create_definition(ftp_def, self.session)
        self.session.commit()

        opaque = parse_instance_opaque_attr(instance)
        self.assertEqual(opaque.host, self.ftp_server.host)

        # Prepare an update definition based on the existing one.
        update_def = {
            'name': ftp_def['name'],
            'id': instance.id,
            'host': 'ftp.updated.example.com',
            'username': 'updated-username',
        }

        # Update the FTP definition.
        updated_instance = self.ftp_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied.
        opaque = parse_instance_opaque_attr(updated_instance)

        self.assertEqual(opaque.host, 'ftp.updated.example.com')
        self.assertEqual(updated_instance.username, 'updated-username')

        # Make sure other fields were preserved.
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_FTP)

# ################################################################################################################################

    def test_ftp_schedules_import(self) -> 'None':
        """ Test that a connection's schedules from YAML create their scheduler jobs, that a re-import
        updates the same jobs in place and that removing a schedule from YAML deletes its job.
        """
        self._setup_test_environment()

        _scheduler = FileTransfer.Scheduler

        # A connection with two schedules - the first one relies on the defaults wherever possible
        # and the second one overrides them all.
        conn_def = {
            'name': ModuleCtx.Conn_Name,
            'host': self.ftp_server.host,
            'port': self.ftp_server.port,
            'username': self.ftp_server.username,
            'password': self.ftp_server.password,
            'schedules': [
                {
                    'name': 'invoices.hourly',
                    'directory': 'incoming/invoices',
                    'service': 'demo.ping',
                    'run_every': 30,
                    'run_unit': 'minutes',
                },
                {
                    'name': 'reports.daily',
                    'directory': 'incoming/reports',
                    'service': 'demo.ping',
                    'run_every': 1,
                    'run_unit': 'days',
                    'is_active': False,
                    'pattern': '*.csv',
                    'ready_how': 'marker',
                    'marker_suffix': '.ok',
                    'should_claim': True,
                    'on_success': 'delete',
                },
            ],
        }

        # Import the connection along with its schedules.
        created, _ = self.ftp_importer.sync_definitions([conn_def], self.session)
        self.assertEqual(len(created), 1)

        instance = created[0]
        opaque = parse_instance_opaque_attr(instance)

        # The stored list carries the full entries with the defaults filled in.
        schedules = opaque[_scheduler.Schedules_Field]
        self.assertEqual(len(schedules), 2)

        first = schedules[0]

        # The id is generated rather than derived from the name.
        self.assertTrue(first['id'])
        self.assertNotEqual(first['id'], 'invoices.hourly')

        self.assertEqual(first['name'], 'invoices.hourly')
        self.assertEqual(first['directory'], 'incoming/invoices')
        self.assertEqual(first['pattern'], _scheduler.Default_Pattern)
        self.assertEqual(first['ready_how'], _scheduler.ReadyHow.Stability)
        self.assertEqual(first['on_success'], _scheduler.OnSuccess.Move)
        self.assertEqual(first['move_directory'], _scheduler.Default_Move_Directory)
        self.assertTrue(first['is_active'])

        second = schedules[1]

        self.assertEqual(second['pattern'], '*.csv')
        self.assertEqual(second['ready_how'], _scheduler.ReadyHow.Marker)
        self.assertEqual(second['marker_suffix'], '.ok')
        self.assertTrue(second['should_claim'])
        self.assertEqual(second['on_success'], _scheduler.OnSuccess.Delete)
        self.assertFalse(second['is_active'])

        # Each schedule has a linked job with the conventional name, the right interval,
        # the FTP dispatch service and the link attributes.
        first_job_name = f'ftp.{ModuleCtx.Conn_Name}.invoices.hourly'
        second_job_name = f'ftp.{ModuleCtx.Conn_Name}.reports.daily'

        first_job = self.session.query(Job).filter_by(name=first_job_name).one()
        second_job = self.session.query(Job).filter_by(name=second_job_name).one()

        self.assertEqual(first['job_id'], first_job.id)
        self.assertEqual(second['job_id'], second_job.id)

        self.assertEqual(first_job.interval_based.minutes, 30)
        self.assertEqual(second_job.interval_based.days, 1)

        self.assertEqual(first_job.service.name, _scheduler.Dispatch_Service[GENERIC.CONNECTION.TYPE.OUTCONN_FTP])

        first_job_opaque = parse_instance_opaque_attr(first_job)

        self.assertEqual(first_job_opaque[SchedulerLink.Conn_ID], instance.id)
        self.assertEqual(first_job_opaque[SchedulerLink.Conn_Type], GENERIC.CONNECTION.TYPE.OUTCONN_FTP)
        self.assertEqual(first_job_opaque[SchedulerLink.Kind], first['id'])

        # A re-import with the first schedule changed and the second one removed
        # must update the first job in place and delete the second one.
        conn_def['schedules'] = [
            {
                'name': 'invoices.hourly',
                'directory': 'incoming/invoices-v2',
                'service': 'demo.ping',
                'run_every': 3,
                'run_unit': 'hours',
            },
        ]

        _, updated = self.ftp_importer.sync_definitions([conn_def], self.session)
        self.assertEqual(len(updated), 1)

        updated_opaque = parse_instance_opaque_attr(updated[0])
        updated_schedules = updated_opaque[_scheduler.Schedules_Field]

        self.assertEqual(len(updated_schedules), 1)
        self.assertEqual(updated_schedules[0]['directory'], 'incoming/invoices-v2')

        # A re-import keeps the id the schedule was created with.
        self.assertEqual(updated_schedules[0]['id'], first['id'])

        # It is still the same job, just with a new interval ..
        updated_job = self.session.query(Job).filter_by(name=first_job_name).one()

        self.assertEqual(updated_job.id, first_job.id)
        self.assertEqual(updated_job.interval_based.hours, 3)
        self.assertEqual(updated_job.interval_based.minutes, 0)

        # .. while the removed schedule's job is gone.
        second_job = self.session.query(Job).filter_by(name=second_job_name).first()
        self.assertIsNone(second_job)

# ################################################################################################################################

    def test_complete_ftp_import_flow(self) -> 'None':
        """ Test the complete flow of importing FTP connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all FTP definitions from the YAML.
        ftp_list = self.yaml_config['ftp']
        ftp_created, ftp_updated = self.ftp_importer.sync_definitions(ftp_list, self.session)

        # Update importer's FTP definitions.
        self.importer.ftp_defs = self.ftp_importer.connection_defs

        # Verify FTP definitions were created.
        self.assertEqual(len(ftp_created), 3)
        self.assertEqual(len(ftp_updated), 0)

        # Verify the FTP definitions dictionary was populated.
        self.assertEqual(len(self.ftp_importer.connection_defs), 3)

        # Verify that these definitions are accessible from the main importer.
        self.assertEqual(len(self.importer.ftp_defs), 3)

        # Importing the same definitions again results in updates, not creations.
        ftp_created2, ftp_updated2 = self.ftp_importer.sync_definitions(ftp_list, self.session)
        self.assertEqual(len(ftp_created2), 0)
        self.assertEqual(len(ftp_updated2), 3)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
