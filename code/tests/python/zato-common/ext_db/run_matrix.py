# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from shutil import rmtree
from tempfile import mkdtemp

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# Zato
from common import assert_mysql_connection_encrypted, assert_postgresql_connection_encrypted, ext_db_env, run_ext_db_scenario
from conftest import ModuleCtx as ConftestCtx
from certificates import generate_certificates
from live_sql.containers import start_mysql, start_postgresql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    from zato.common.typing_ import stranydict, strlist

    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

# The database users inside the containers must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

# The backends the scenario runs against, in this order
_backend_names = ('mysql', 'postgresql', 'mysql-ssl', 'postgresql-ssl')

# Encryption checks per TLS-required backend
_encryption_asserts = {
    'mysql-ssl':      assert_mysql_connection_encrypted,
    'postgresql-ssl': assert_postgresql_connection_encrypted,
}

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Runs the complete external AS2/AS4 database scenario against every backend:
    MySQL and PostgreSQL, both plain and TLS-required. TLS sessions additionally confirm
    that the connection really is encrypted.
    """

    # Certificates for the TLS-required containers
    certificate_dir = mkdtemp(prefix='zato-ext-db-certificates-')
    os.chmod(certificate_dir, _certificate_dir_mode)
    certificates = generate_certificates(certificate_dir)

    servers:'stranydict' = {}
    failed:'strlist' = []

    try:
        servers['mysql'] = start_mysql(
            container_name=ConftestCtx.MySQL_Container,
            port=ConftestCtx.MySQL_Port,
            username=ConftestCtx.Username,
            password=ConftestCtx.Password,
            db_name=ConftestCtx.DB_Name,
            needs_ssl=False,
        )
        servers['postgresql'] = start_postgresql(
            container_name=ConftestCtx.PostgreSQL_Container,
            port=ConftestCtx.PostgreSQL_Port,
            username=ConftestCtx.Username,
            password=ConftestCtx.Password,
            db_name=ConftestCtx.DB_Name,
            needs_ssl=False,
        )
        servers['mysql-ssl'] = start_mysql(
            container_name=ConftestCtx.MySQL_SSL_Container,
            port=ConftestCtx.MySQL_SSL_Port,
            username=ConftestCtx.Username,
            password=ConftestCtx.Password,
            db_name=ConftestCtx.DB_Name,
            needs_ssl=True,
            certificates=certificates,
        )
        servers['postgresql-ssl'] = start_postgresql(
            container_name=ConftestCtx.PostgreSQL_SSL_Container,
            port=ConftestCtx.PostgreSQL_SSL_Port,
            username=ConftestCtx.Username,
            password=ConftestCtx.Password,
            db_name=ConftestCtx.DB_Name,
            needs_ssl=True,
            certificates=certificates,
        )

        for backend_name in _backend_names:

            print(f'External database matrix: running against {backend_name}')

            server = servers[backend_name]

            try:
                with ext_db_env(server.details):
                    run_ext_db_scenario()

                    # TLS-required backends additionally confirm the connection is encrypted
                    if encryption_assert := _encryption_asserts.get(backend_name):
                        encryption_assert()

            except Exception as e:
                failed.append(backend_name)
                print(f'External database matrix: {backend_name} failed: {e}')

    finally:

        # Stop all the containers no matter what happened above ..
        for server in servers.values():
            stop_container(server.container_name)

        # .. and delete the throwaway certificates.
        rmtree(certificate_dir, ignore_errors=True)

    if failed:
        failed_names = ', '.join(failed)
        print(f'External database matrix: failed backends: {failed_names}')
        sys.exit(1)

    print('External database matrix: all backends passed')

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
