# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
from shutil import rmtree
from tempfile import mkdtemp

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# Zato
from conftest import ModuleCtx as ConftestCtx
from live_sql.certificates import generate_certificates
from live_sql.containers import start_mysql, start_postgresql, stop_container
from live_sql.env import build_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    from zato.common.typing_ import stranydict, strlist

    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

# The root of the 4.1 tree, five levels above this file
_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

# The Python interpreter of the Zato virtualenv
_python = os.path.join(_base_dir, 'code', 'bin', 'python')

# The Playwright test files that exercise the audit log through the dashboard
_ui_test_files = (
    'test_pubsub_audit_log.py',
    'test_rest_channel_audit_log.py',
    'test_soap_channel_audit_log.py',
    'test_rest_outconn_audit_log.py',
    'test_soap_outconn_audit_log.py',
    'test_email_imap_audit_log.py',
    'test_rest_channel_internal.py',
)

# Where the Playwright test files live
_ui_test_dir = os.path.join(_base_dir, 'code', 'tests', 'python', 'zato-dashboard', 'playwright_')

# The unit test files that write to the audit log directly, run against every backend as well
_unit_test_files = (
    os.path.join(_base_dir, 'code', 'zato-server', 'test', 'zato', 'connection', 'test_email_imap.py'),
    os.path.join(_base_dir, 'code', 'tests', 'python', 'zato-common', 'pubsub', 'test_redis_backend.py'),
    os.path.join(_base_dir, 'code', 'tests', 'python', 'zato-common', 'pubsub', 'test_facade_amqp.py'),
)

# The pytest cache directory for the matrix runs
_cache_dir = os.path.join(_base_dir, 'code', 'tests', '.pytest_cache_audit_log_ui')

# The database users inside the containers must be able to traverse into the certificate directory
_certificate_dir_mode = 0o755

# The backends every UI test runs against, in this order
_backend_names = ('sqlite', 'mysql', 'postgresql', 'mysql-ssl', 'postgresql-ssl')

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

def _run_ui_tests(env:'stranydict') -> 'int':
    """ Runs all the audit log Playwright test files, returning the pytest exit code.
    """
    command:'strlist' = [_python, '-m', 'pytest']

    for name in _ui_test_files:
        command.append(os.path.join(_ui_test_dir, name))

    command.extend(['-v', '-s', '-o', f'cache_dir={_cache_dir}'])

    result = subprocess.run(command, cwd=_base_dir, env=env, check=False)

    out = result.returncode
    return out

# ################################################################################################################################

def _run_unit_tests(env:'stranydict') -> 'int':
    """ Runs the unit tests that write to the audit log directly, returning the pytest exit code.
    """
    command:'strlist' = [_python, '-m', 'pytest']
    command.extend(_unit_test_files)
    command.extend(['-v', '-s', '-o', f'cache_dir={_cache_dir}'])

    result = subprocess.run(command, cwd=_base_dir, env=env, check=False)

    out = result.returncode
    return out

# ################################################################################################################################

def main() -> 'None':
    """ Runs every audit log test - the dashboard UI ones and the unit ones that write
    to the audit log directly - against every backend: sqlite, MySQL, PostgreSQL,
    both plain and TLS-required for the two servers. The UI tests create their own
    server and dashboard which inherit the Zato_Audit_Log_DB_* variables set here.
    """

    # Certificates for the TLS-required containers
    certificate_dir = mkdtemp(prefix='zato-audit-log-certificates-')
    os.chmod(certificate_dir, _certificate_dir_mode)
    certificates = generate_certificates(certificate_dir)

    # Containers are started once and reused by both their plain and TLS matrix passes
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

        # The per-backend environments the components are restarted with
        backend_env:'stranydict' = {
            'sqlite': {},
            'mysql': build_env(_env_prefix, servers['mysql'].details),
            'postgresql': build_env(_env_prefix, servers['postgresql'].details),
            'mysql-ssl': build_env(_env_prefix, servers['mysql-ssl'].details),
            'postgresql-ssl': build_env(_env_prefix, servers['postgresql-ssl'].details),
        }

        for backend_name in _backend_names:

            print(f'Audit log matrix: running against {backend_name}', flush=True)

            env = dict(os.environ)
            env['ZATO_TEST_BASE_DIR'] = _base_dir
            env.update(backend_env[backend_name])

            # The unit tests write to the backend from the pytest process itself ..
            unit_return_code = _run_unit_tests(env)

            if unit_return_code:
                failed.append(f'{backend_name} (unit)')
                print(f'Audit log matrix: {backend_name} unit tests failed with code {unit_return_code}', flush=True)

            # .. while the UI tests spawn their own server and dashboard which inherit the variables.
            ui_return_code = _run_ui_tests(env)

            if ui_return_code:
                failed.append(f'{backend_name} (ui)')
                print(f'Audit log matrix: {backend_name} UI tests failed with code {ui_return_code}', flush=True)

    finally:

        # Stop all the containers no matter what happened above ..
        for server in servers.values():
            stop_container(server.container_name)

        # .. and delete the throwaway certificates.
        rmtree(certificate_dir, ignore_errors=True)

    if failed:
        failed_names = ', '.join(failed)
        print(f'Audit log matrix: failed backends: {failed_names}', flush=True)
        sys.exit(1)

    print('Audit log matrix: all backends passed', flush=True)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
