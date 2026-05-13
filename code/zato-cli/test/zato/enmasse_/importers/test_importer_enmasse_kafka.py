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
from zato.cli.enmasse.importers.kafka import ChannelKafkaImporter, OutgoingKafkaImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelKafkaFromYAML(TestCase):
    """ Tests importing Kafka channel definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.kafka_importer = ChannelKafkaImporter(self.importer)

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

    def test_channel_kafka_creation(self):
        self._setup_test_environment()

        kafka_defs = self.yaml_config['channel_kafka']
        created, updated = self.kafka_importer.sync_definitions(kafka_defs, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        conn = self.session.query(GenericConn).filter_by(
            name='enmasse.kafka.channel.1',
            type_=GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA,
        ).one()
        self.assertEqual(conn.address, 'localhost:9092')
        self.assertTrue(conn.is_active)

# ################################################################################################################################

    def test_channel_kafka_update(self):
        self._setup_test_environment()

        kafka_defs = self.yaml_config['channel_kafka']
        kafka_def = kafka_defs[0]

        instance = self.kafka_importer.create_definition(kafka_def, self.session)
        self.session.commit()
        self.assertEqual(instance.address, 'localhost:9092')

        update_def = {
            'name': kafka_def['name'],
            'id': instance.id,
            'address': 'kafka-updated:9093',
        }

        updated_instance = self.kafka_importer.update_definition(update_def, self.session)
        self.session.commit()

        self.assertEqual(updated_instance.address, 'kafka-updated:9093')
        self.assertEqual(updated_instance.name, kafka_def['name'])

# ################################################################################################################################

    def test_complete_channel_kafka_import_flow(self):
        self._setup_test_environment()

        kafka_list = self.yaml_config['channel_kafka']
        created, updated = self.kafka_importer.sync_definitions(kafka_list, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self.kafka_importer.sync_definitions(kafka_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingKafkaFromYAML(TestCase):
    """ Tests importing Kafka outgoing definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.kafka_importer = OutgoingKafkaImporter(self.importer)

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

    def test_outgoing_kafka_creation(self):
        self._setup_test_environment()

        kafka_defs = self.yaml_config['outgoing_kafka']
        created, updated = self.kafka_importer.sync_definitions(kafka_defs, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        conn = self.session.query(GenericConn).filter_by(
            name='enmasse.kafka.outgoing.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA,
        ).one()
        self.assertEqual(conn.address, 'localhost:9092')
        self.assertTrue(conn.is_active)

# ################################################################################################################################

    def test_outgoing_kafka_update(self):
        self._setup_test_environment()

        kafka_defs = self.yaml_config['outgoing_kafka']
        kafka_def = kafka_defs[0]

        instance = self.kafka_importer.create_definition(kafka_def, self.session)
        self.session.commit()
        self.assertEqual(instance.address, 'localhost:9092')

        update_def = {
            'name': kafka_def['name'],
            'id': instance.id,
            'address': 'kafka-out-updated:9093',
        }

        updated_instance = self.kafka_importer.update_definition(update_def, self.session)
        self.session.commit()

        self.assertEqual(updated_instance.address, 'kafka-out-updated:9093')
        self.assertEqual(updated_instance.name, kafka_def['name'])

# ################################################################################################################################

    def test_complete_outgoing_kafka_import_flow(self):
        self._setup_test_environment()

        kafka_list = self.yaml_config['outgoing_kafka']
        created, updated = self.kafka_importer.sync_definitions(kafka_list, self.session)

        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        created2, updated2 = self.kafka_importer.sync_definitions(kafka_list, self.session)
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
