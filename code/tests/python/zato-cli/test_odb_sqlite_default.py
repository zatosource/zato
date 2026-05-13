# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from unittest import main, TestCase

# ################################################################################################################################
# ################################################################################################################################

_ZATO_BASE = '/home/dsuch/projects/zatosource-zato/4.1'
_ZATO_BIN = os.path.join(_ZATO_BASE, 'code', 'bin', 'zato')

_PASSWORD = 'test.odb.sqlite.' + os.urandom(8).hex()

_server_proc = None
_tmpdir = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

# ################################################################################################################################
# ################################################################################################################################

def _kill_server():
    global _server_proc
    if _server_proc and _server_proc.poll() is None:
        _server_proc.terminate()
        try:
            _server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_proc.kill()
            _server_proc.wait(timeout=5)
    _server_proc = None

# ################################################################################################################################
# ################################################################################################################################

def _cleanup():
    _kill_server()

atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host, port, password, timeout=60):
    from urllib.request import Request, urlopen
    from base64 import b64encode

    creds = b64encode(f'admin.invoke:{password}'.encode()).decode()
    url = f'http://{host}:{port}/zato/api/invoke/demo.ping'
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            req = Request(url, method='GET')
            req.add_header('Authorization', f'Basic {creds}')
            with urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise Exception(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestODBSQLiteDefault(TestCase):

    server_dir = None
    port = None

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest
        global _server_proc, _tmpdir

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest(f'zato binary not found at {_ZATO_BIN}')

        cls.port = _find_free_port()
        _tmpdir = tempfile.mkdtemp(prefix='zato_test_odb_sqlite_')

        qs_env = os.environ.copy()
        qs_env.pop('COVERAGE_PROCESS_START', None)

        qs_cmd = [
            _ZATO_BIN, 'quickstart', 'create', _tmpdir,
            '--servers', '1',
            '--server-api-client-for-scheduler-password', _PASSWORD,
            '--no-scheduler',
            '--force',
            '--password', _PASSWORD,
        ]

        result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
        if result.returncode != 0:
            shutil.rmtree(_tmpdir, ignore_errors=True)
            _tmpdir = None
            raise SkipTest(
                f'quickstart create failed:\n{result.stdout}\n{result.stderr}')

        cls.server_dir = os.path.join(_tmpdir, 'server1')
        repo_location = os.path.join(cls.server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls.port)
        update_config_file(config, repo_location, 'server.conf')

        broker_port = _find_free_port()

        env = os.environ.copy()
        env['Zato_Config_Bind_Port'] = str(cls.port)
        env['Zato_Broker_HTTP_Port'] = str(broker_port)
        env.pop('COVERAGE_PROCESS_START', None)

        _server_proc = subprocess.Popen(
            [_ZATO_BIN, 'start', cls.server_dir, '--fg'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        cls._server_output_lines = []

        def _capture():
            for line in iter(_server_proc.stdout.readline, b''):
                text = line.decode('utf-8', errors='replace').rstrip()
                cls._server_output_lines.append(text)

        cls._stdout_thread = threading.Thread(target=_capture, daemon=True)
        cls._stdout_thread.start()

        try:
            _wait_for_server('127.0.0.1', cls.port, _PASSWORD, timeout=60)
        except Exception:
            print('\n--- Server did not become ready, output: ---', file=sys.stderr)
            for line in cls._server_output_lines:
                print(line, file=sys.stderr)
            print('--- End of server output ---\n', file=sys.stderr)

            server_log = os.path.join(repo_location, '..', '..', 'logs', 'server.log')
            if os.path.isfile(server_log):
                print(f'\n--- server.log ({server_log}): ---', file=sys.stderr)
                with open(server_log) as f:
                    for line in f.readlines()[-50:]:
                        print(line.rstrip(), file=sys.stderr)
                print('--- End of server.log ---\n', file=sys.stderr)

            _kill_server()
            raise

    @classmethod
    def tearDownClass(cls):
        global _tmpdir
        _kill_server()
        if _tmpdir and os.path.isdir(_tmpdir):
            shutil.rmtree(_tmpdir, ignore_errors=True)
        _tmpdir = None

# ################################################################################################################################

    def test_sqlite_db_file_exists(self):
        db_path = os.path.join(_tmpdir, 'zato.db')
        self.assertTrue(os.path.isfile(db_path), f'SQLite DB not found at {db_path}')
        self.assertGreater(os.path.getsize(db_path), 0, 'SQLite DB file is empty')

# ################################################################################################################################

    def test_server_conf_engine_is_sqlite(self):
        from zato.common.util.config import get_config_object
        repo_location = os.path.join(self.server_dir, 'config', 'repo')
        config = get_config_object(repo_location, 'server.conf')
        engine = config['odb']['engine']
        self.assertEqual(engine, 'sqlite')

# ################################################################################################################################

    def test_sqlite_db_has_tables(self):
        db_path = os.path.join(_tmpdir, 'zato.db')
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}
        finally:
            conn.close()

        for expected in ('server', 'http_soap'):
            self.assertIn(expected, tables, f'Table "{expected}" not found in ODB, got: {sorted(tables)}')

# ################################################################################################################################

    def test_server_responds_to_ping(self):
        from urllib.request import Request, urlopen
        from base64 import b64encode

        creds = b64encode(f'admin.invoke:{_PASSWORD}'.encode()).decode()
        url = f'http://127.0.0.1:{self.port}/zato/api/invoke/demo.ping'

        req = Request(url, method='GET')
        req.add_header('Authorization', f'Basic {creds}')
        with urlopen(req, timeout=10) as resp:
            self.assertEqual(resp.status, 200)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
