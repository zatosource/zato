# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re

# oracledb
import oracledb

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where the SQL files live.
    Schema_Directory = os.path.join(os.path.dirname(__file__), 'schema')

    # A statement in an SQL file ends with this on a line of its own.
    Statement_Terminator = re.compile(r'^/[ \t]*$', re.MULTILINE)

    # What the SQL files carry where the password of every user goes.
    Password_Placeholder = '{{password}}'

    # The administrator of the pluggable database.
    System_Username = 'system'

    # The users every SQL file creates or fills, in the order of their creation.
    Users = ('FACILITY', 'FACILITY_READER', 'RECORDS', 'RECORDS_API', 'SYNC_WRITER', 'SYNC_FAULTS')

    # The files that build the schema, in the order they are loaded.
    Files_Before_Package = ('users.sql', 'facility.sql', 'records.sql', 'sync_faults.sql', 'grants.sql')
    Files_After_Package  = ('sync_writer.sql',)

    # The two package variants and the file each one comes from.
    Variant_No_Commit = 'no_commit'
    Variant_Commit    = 'commit'

    Package_Files = {
        Variant_No_Commit: 'records_api_no_commit.sql',
        Variant_Commit:    'records_api_commit.sql',
    }

    # The tables a test fills and what every test starts without.
    Data_Tables = (
        'FACILITY.PATIENTS',
        'FACILITY.STAFF',
        'FACILITY.CONDITION_CODES',
        'FACILITY.TREATMENTS',
        'FACILITY.LOG_TREATMENTS',
        'FACILITY.LOG_CONSULT_NOTES',
        'RECORDS.PATIENT_FIELD',
        'RECORDS.PATIENT_SECTION',
        'SYNC_WRITER.SYNC_ID_MAP',
        'SYNC_WRITER.SYNC_CHECKPOINT',
    )

# ################################################################################################################################
# ################################################################################################################################

def _quote_users() -> 'str':
    """ The users as an SQL list of string literals.
    """
    quoted:'strlist' = []

    for user in ModuleCtx.Users:
        quoted.append(f'\'{user}\'')

    out = ', '.join(quoted)
    return out

# What did not compile, if anything, among the objects the SQL files created.
_compilation_errors_template = '''
select owner, name, type, line, text
from dba_errors
where owner in ({users})
order by owner, name, type, sequence
'''

_quoted_users = _quote_users()
_compilation_errors = _compilation_errors_template.format(users=_quoted_users)

_reset_fault_plan = 'update SYNC_FAULTS.FAULT_PLAN set NEEDS_RAISE = 0, SLEEP_SECONDS = 0'

# ################################################################################################################################
# ################################################################################################################################

def _is_only_comments(statement:'str') -> 'bool':
    """ True if nothing in the statement is an actual statement.
    """
    for line in statement.splitlines():
        line = line.strip()

        if not line:
            continue

        if not line.startswith('--'):
            out = False
            break
    else:
        out = True

    return out

# ################################################################################################################################

def read_statements(file_name:'str', password:'str') -> 'strlist':
    """ The statements of one SQL file, each ready to be executed, with the password of every user filled in.
    """
    path = os.path.join(ModuleCtx.Schema_Directory, file_name)

    with open(path) as sql_file:
        text = sql_file.read()

    text = text.replace(ModuleCtx.Password_Placeholder, password)

    out:'strlist' = []

    for statement in ModuleCtx.Statement_Terminator.split(text):
        statement = statement.strip()

        if not statement:
            continue

        if _is_only_comments(statement):
            continue

        out.append(statement)

    return out

# ################################################################################################################################
# ################################################################################################################################

class Schema:
    """ The database side of the suite - every user, table, package and grant, created through the
    administrator's connection and reset between tests.
    """

    def __init__(self, *, host:'str', port:'int', service_name:'str', system_password:'str') -> 'None':
        self.host = host
        self.port = port
        self.service_name = service_name
        self.system_password = system_password

        # One password for every user the SQL files create.
        self.password = 'test.facility.' + CryptoManager.generate_hex_string()

# ################################################################################################################################

    def connect(self, username:'str') -> 'oracledb.Connection':
        """ A connection as one of the users.
        """
        if username == ModuleCtx.System_Username:
            password = self.system_password
        else:
            password = self.password

        out = oracledb.connect(
            user=username,
            password=password,
            host=self.host,
            port=self.port,
            service_name=self.service_name,
        )

        return out

# ################################################################################################################################

    def _run_file(self, connection:'oracledb.Connection', file_name:'str') -> 'None':
        """ Runs every statement of one SQL file.
        """
        statements = read_statements(file_name, self.password)

        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)

# ################################################################################################################################

    def install(self, variant:'str') -> 'None':
        """ Builds everything from scratch, with the package variant asked for.
        """
        connection = self.connect(ModuleCtx.System_Username)

        try:

            # The users, the tables and everything the package depends on ..
            for file_name in ModuleCtx.Files_Before_Package:
                self._run_file(connection, file_name)

            # .. the package itself ..
            package_file = ModuleCtx.Package_Files[variant]
            self._run_file(connection, package_file)

            # .. and what calls the package.
            for file_name in ModuleCtx.Files_After_Package:
                self._run_file(connection, file_name)

            connection.commit()

        finally:
            connection.close()

        self.verify_compiled()

# ################################################################################################################################

    def install_package(self, variant:'str') -> 'None':
        """ Replaces the package with the variant asked for, leaving everything else as it is.
        """
        connection = self.connect(ModuleCtx.System_Username)

        try:
            package_file = ModuleCtx.Package_Files[variant]
            self._run_file(connection, package_file)
            connection.commit()

        finally:
            connection.close()

        self.verify_compiled()

# ################################################################################################################################

    def verify_compiled(self) -> 'None':
        """ Raises if any package, body or trigger the SQL files created did not compile.
        """
        connection = self.connect(ModuleCtx.System_Username)

        try:
            with connection.cursor() as cursor:
                cursor.execute(_compilation_errors)
                errors = cursor.fetchall()

        finally:
            connection.close()

        if errors:
            lines:'strlist' = []

            for owner, name, object_type, line, text in errors:
                lines.append(f'{owner}.{name} ({object_type}) line {line}: {text}')

            details = '\n'.join(lines)
            raise Exception(f'Schema objects did not compile:\n{details}')

# ################################################################################################################################

    def reset_data(self) -> 'None':
        """ Empties every table a test fills and clears the fault plan.
        """
        connection = self.connect(ModuleCtx.System_Username)

        try:
            with connection.cursor() as cursor:

                for table in ModuleCtx.Data_Tables:
                    cursor.execute(f'delete from {table}')

                cursor.execute(_reset_fault_plan)

            connection.commit()

        finally:
            connection.close()

# ################################################################################################################################
# ################################################################################################################################
