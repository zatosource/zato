# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQL importer's handling of the 'extra' options.

# stdlib
import os
from contextlib import ExitStack
from tempfile import gettempdir
from unittest import TestCase, main

# SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.cli.enmasse.util.secrets import Session_Key_Crypto_Manager
from zato.common.crypto.api import CryptoManager, ServerCryptoManager
from zato.common.odb.model import SQLConnectionPool
from zato.common.test.config_database import config_database_engine
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# A template with the sql section alone - the 'extra' options are a YAML list.
template_sql_extra = """
sql:

  - name: enmasse.sql.extra.1
    type: mysql
    host: 127.0.0.1
    port: 3306
    db_name: mydb
    username: enmasse.1
    extra:
      - connect_timeout=10
      - charset=utf8mb4

  - name: enmasse.sql.extra.2
    type: postgresql
    host: 127.0.0.1
    port: 5432
    db_name: mydb
    username: enmasse.2
"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSQLImporterExtraList(TestCase):
    """ The 'extra' options of an SQL connection - a YAML list on input, one newline-separated string in the column.
    """

    def setUp(self:'any_') -> 'None':

        # Each test gets a new PostgreSQL database of its own, dropped when the test ends ..
        self.exit_stack = ExitStack()
        engine = self.exit_stack.enter_context(config_database_engine([SQLConnectionPool.__table__]))

        # .. with a session carrying the crypto manager the importer encrypts passwords with ..
        session_factory = sessionmaker(bind=engine)
        self.session = session_factory()
        self.session.info[Session_Key_Crypto_Manager] = ServerCryptoManager.from_secret_key(ServerCryptoManager.generate_key())

        # .. the YAML template goes to a file of its own ..
        file_name = 'enmasse.sql.extra.' + CryptoManager.generate_hex_string() + '.yaml'
        self.temp_file_path = os.path.join(gettempdir(), file_name)

        with open(self.temp_file_path, 'w') as temp_file:
            _ = temp_file.write(template_sql_extra)

        # .. and the importers that will read it back.
        self.importer = EnmasseYAMLImporter()
        self.sql_importer = SQLImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)

# ################################################################################################################################

    def tearDown(self:'any_') -> 'None':
        self.session.close()
        os.remove(self.temp_file_path)
        self.exit_stack.close()

# ################################################################################################################################

    def _setup_test_environment(self:'any_') -> 'None':

        # Parse the YAML file.
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file_path)

# ################################################################################################################################

    def test_the_extra_list_is_joined_into_the_column_on_create(self:'any_') -> 'None':

        self._setup_test_environment()

        # Import the definitions ..
        sql_definitions = self.yaml_config['sql']
        _ = self.sql_importer.sync_sql_definitions(sql_definitions, self.session)

        # .. and read the row back.
        row = self.session.query(SQLConnectionPool).filter_by(name='enmasse.sql.extra.1').one()
        self.assertEqual(row.extra, 'connect_timeout=10\ncharset=utf8mb4')

# ################################################################################################################################

    def test_a_definition_without_extra_stores_an_empty_column(self:'any_') -> 'None':

        self._setup_test_environment()

        # Import the definitions ..
        sql_definitions = self.yaml_config['sql']
        _ = self.sql_importer.sync_sql_definitions(sql_definitions, self.session)

        # .. and read the row back.
        row = self.session.query(SQLConnectionPool).filter_by(name='enmasse.sql.extra.2').one()
        self.assertEqual(row.extra, '')

# ################################################################################################################################

    def test_the_extra_list_is_joined_on_update_too(self:'any_') -> 'None':

        self._setup_test_environment()

        # The first sync creates the connections ..
        sql_definitions = self.yaml_config['sql']
        _ = self.sql_importer.sync_sql_definitions(sql_definitions, self.session)

        # .. the second one goes down the update path with new options ..
        for sql_definition in sql_definitions:
            if sql_definition['name'] == 'enmasse.sql.extra.1':
                sql_definition['extra'] = ['connect_timeout=30', 'charset=utf8mb4']

        _ = self.sql_importer.sync_sql_definitions(sql_definitions, self.session)

        # .. and the row carries what the update said.
        row = self.session.query(SQLConnectionPool).filter_by(name='enmasse.sql.extra.1').one()
        self.assertEqual(row.extra, 'connect_timeout=30\ncharset=utf8mb4')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
