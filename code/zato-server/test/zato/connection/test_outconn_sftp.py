# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import mkdtemp, NamedTemporaryFile
from unittest import main, TestCase

# Bunch
from zato.common.ext.bunch import Bunch, bunchify

# Zato
from zato.common.audit_log.api import AuditLog, ModuleCtx as AuditLogCtx
from zato.common.crypto.api import CryptoManager
from zato.common.test.sftp_ import SFTPTestServer
from zato.common.typing_ import cast_
from zato.common.util.tcp import get_free_port
from zato.server.connection.sftp import SFTPConnection
from zato.server.generic.api.outconn_sftp import SFTPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_SFTP'

    # A key file that is never created.
    Missing_Key_Name = 'missing_key'

# ################################################################################################################################
# ################################################################################################################################

class _TestWrapperClient:
    """ A context manager that hands out the one client that the test wrapper holds.
    """
    def __init__(self, client:'SFTPClient') -> 'None':
        self.client_object = client

# ################################################################################################################################

    def __enter__(self) -> 'SFTPClient':
        return self.client_object

# ################################################################################################################################

    def __exit__(self, _type:'object', _value:'object', _traceback:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class _TestWrapper:
    """ Exposes a .client and .ping API over a single client object,
    along with an audit writer and a content storage flag.
    """
    def __init__(self, client:'SFTPClient') -> 'None':
        self.client_object        = client
        self.should_store_content = False
        self.audit_log            = AuditLog('test-outconn-sftp')

        self.config = Bunch()
        self.config.name = 'test-outconn-sftp'

# ################################################################################################################################

    def client(self, **kwargs:'any_') -> '_TestWrapperClient':
        out = _TestWrapperClient(self.client_object)
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        out = self.client_object.ping()
        if not out.is_ok:
            raise Exception(out.stderr)

# ################################################################################################################################
# ################################################################################################################################

class OutconnSFTPTestCase(TestCase):
    """ Tests the outgoing SFTP connection API against a real SFTP server.
    """

    server: 'SFTPTestServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # The audit log is pointed at a throwaway SQLite database for the duration of the suite.
        audit_db_dir = mkdtemp(prefix='zato-test-sftp-audit-')
        os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
        os.environ[AuditLogCtx.Env_Name] = os.path.join(audit_db_dir, 'audit.db')

        class_.server = SFTPTestServer()
        class_.server.start()

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.server.stop()

        # The audit log is no longer pointed at this suite's database.
        del os.environ[AuditLogCtx.Env_Type]
        del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

    def get_config(self, conn_name:'str', *, use_password:'bool' = False) -> 'Bunch':

        # With a password in use, we authenticate with the encrypted key whose passphrase
        # is the connection's password, going through the askpass helper.
        if use_password:
            private_key = self.server.client_key_encrypted_path
            secret = self.server.password
        else:
            private_key = self.server.client_key_path
            secret = ''

        host = self.server.host
        port = self.server.port
        address = f'{host}:{port}'

        config = bunchify({
            'id': 1,
            'name': conn_name,
            'is_active': True,
            'address': address,
            'username': self.server.username,
            'secret': secret,
            'private_key': private_key,

            'strict_host_key_checking': False,

            # The test server's host key is freshly generated on each run.
            'ignore_host_key_changes': True,
        })

        out = cast_('Bunch', config)
        return out

# ################################################################################################################################

    def make_client(self, config:'Bunch') -> 'SFTPClient':

        server = cast_('any_', None)
        out = SFTPClient(config, server)

        return out

# ################################################################################################################################

    def get_client(self, conn_name:'str', *, use_password:'bool' = False) -> 'SFTPClient':

        config = self.get_config(conn_name, use_password=use_password)
        out = self.make_client(config)

        return out

# ################################################################################################################################

    def get_conn(self, conn_name:'str', *, use_password:'bool' = False) -> 'SFTPConnection':

        client = self.get_client(conn_name, use_password=use_password)
        wrapper = _TestWrapper(client)
        wrapper_typed = cast_('any_', wrapper)

        out = SFTPConnection('test-cid', wrapper_typed)

        return out

# ################################################################################################################################

    def get_remote_path(self, suffix:'str') -> 'str':

        hex_string = CryptoManager.generate_hex_string()
        file_name = f'test-{hex_string}-{suffix}'

        out = os.path.join(self.server.files_dir, file_name)

        return out

# ################################################################################################################################

    def test_ping_with_key(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        client = self.get_client('test_ping_with_key')
        out = client.ping()

        self.assertTrue(out.is_ok, out.stderr)

# ################################################################################################################################

    def test_ping_with_password(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        client = self.get_client('test_ping_with_password', use_password=True)
        out = client.ping()

        self.assertTrue(out.is_ok, out.stderr)

# ################################################################################################################################

    def test_execute_with_key(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_with_key')

        files_dir = self.server.files_dir
        command = f'ls {files_dir}'
        out = conn.execute(command)

        self.assertTrue(out.is_ok, out.stderr)

# ################################################################################################################################

    def test_execute_with_password(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_with_password', use_password=True)

        files_dir = self.server.files_dir
        command = f'ls {files_dir}'
        out = conn.execute(command)

        self.assertTrue(out.is_ok, out.stderr)

# ################################################################################################################################

    def test_execute_error_is_reported(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_error_is_reported')
        missing_path = self.get_remote_path('missing-dir')

        command = f'ls {missing_path}'
        out = conn.execute(command, raise_on_error=False)

        self.assertFalse(out.is_ok)

# ################################################################################################################################

    def test_wrong_key_is_rejected(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # Generate a key that the server does not know about.
        rejected_key_path = os.path.join(self.server.base_dir, 'rejected_key')
        self.server.generate_key(rejected_key_path)

        config = self.get_config('test_wrong_key_is_rejected')
        config.private_key = rejected_key_path

        client = self.make_client(config)
        out = client.ping()

        self.assertFalse(out.is_ok)

# ################################################################################################################################

    def test_missing_key_file_is_reported(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # Nothing ever creates this file.
        missing_key_path = os.path.join(self.server.base_dir, ModuleCtx.Missing_Key_Name)

        config = self.get_config('test_missing_key_file_is_reported')
        config.private_key = missing_key_path

        client = self.make_client(config)
        out = client.ping()

        # The ping must fail with a clear error naming the key file.
        self.assertFalse(out.is_ok)

        details = out.details
        details = cast_('str', details)
        self.assertIn(missing_key_path, details)

# ################################################################################################################################

    def test_upload_and_download_file(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_upload_and_download_file')

        data = 'Test SFTP upload data'
        remote_path = self.get_remote_path('upload.txt')

        # A local file to upload ..
        with NamedTemporaryFile('w+', suffix='-zato-test-sftp.txt') as local_file:
            _ = local_file.write(data)
            local_file.flush()

            # .. upload it ..
            out = conn.upload(local_file.name, remote_path)
            self.assertTrue(out.is_ok, out.stderr)

        # .. download it to another local path ..
        with NamedTemporaryFile('w+', suffix='-zato-test-sftp.txt') as download_file:
            out = conn.download_file(remote_path, download_file.name)
            self.assertTrue(out.is_ok, out.stderr)

            # .. and confirm the round trip did not change the contents.
            with open(download_file.name, encoding='utf8') as downloaded:
                downloaded_data = downloaded.read()
                self.assertEqual(downloaded_data, data)

# ################################################################################################################################

    def test_upload_with_overwrite_false_onto_existing_path(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_upload_with_overwrite_false_onto_existing_path')
        remote_path = self.get_remote_path('overwrite.txt')

        # Create the remote file first ..
        conn.write('Initial data', remote_path)

        # .. prepare a local file to upload ..
        with NamedTemporaryFile('w+', suffix='-zato-test-sftp.txt') as local_file:
            _ = local_file.write('New data')
            local_file.flush()

            # .. and now expect an exception because the remote location already exists.
            with self.assertRaises(Exception) as ctx:
                _ = conn.upload(local_file.name, remote_path, overwrite=False)

        error_message = str(ctx.exception)
        self.assertIn('already exists', error_message)

# ################################################################################################################################

    def test_write_and_read(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_write_and_read')

        data = 'Test SFTP write data'
        remote_path = self.get_remote_path('write.txt')

        # Write the data out ..
        conn.write(data, remote_path)

        # .. and read it back.
        result = conn.read(remote_path)
        self.assertEqual(result.decode('utf8'), data)

# ################################################################################################################################

    def test_write_and_read_with_password(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_write_and_read_with_password', use_password=True)

        data = 'Test SFTP write data with password auth'
        remote_path = self.get_remote_path('write-password.txt')

        # Write the data out ..
        conn.write(data, remote_path)

        # .. and read it back.
        result = conn.read(remote_path)
        self.assertEqual(result.decode('utf8'), data)

# ################################################################################################################################

    def test_create_directory_and_entry_types(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_create_directory_and_entry_types')
        remote_path = self.get_remote_path('directory')

        # The directory does not exist yet ..
        self.assertFalse(conn.exists(remote_path))

        # .. create it ..
        out = conn.create_directory(remote_path)
        self.assertTrue(out.is_ok, out.stderr)

        # .. and confirm what the server reports about it.
        self.assertTrue(conn.exists(remote_path))
        self.assertTrue(conn.is_directory(remote_path))

        # A file created in that directory is a file, not a directory.
        file_path = os.path.join(remote_path, 'file.txt')
        conn.write('Test data', file_path)

        self.assertTrue(conn.is_file(file_path))
        self.assertFalse(conn.is_directory(file_path))

# ################################################################################################################################

    def test_get_info(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_get_info')
        remote_path = self.get_remote_path('info.txt')

        data = 'Test data for get_info'
        conn.write(data, remote_path)

        info = conn.get_info(remote_path)
        info = cast_('any_', info)

        expected_size = len(data)

        self.assertTrue(info.is_file)
        self.assertEqual(info.size, expected_size)
        self.assertEqual(info.name, remote_path)

# ################################################################################################################################

    def test_list(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_list')
        remote_path = self.get_remote_path('list-directory')

        # Create a directory with two files inside ..
        _ = conn.create_directory(remote_path)

        first_path = os.path.join(remote_path, 'first.txt')
        second_path = os.path.join(remote_path, 'second.txt')

        conn.write('First file', first_path)
        conn.write('Second file', second_path)

        # .. list the directory ..
        result = conn.list(remote_path)
        result = cast_('any_', result)

        # .. and make sure both files were returned - only base names are compared,
        # .. the server reports full paths.
        names = []
        for item in result:
            base_name = os.path.basename(item.name)
            names.append(base_name)

        self.assertIn('first.txt', names)
        self.assertIn('second.txt', names)

# ################################################################################################################################

    def test_move_and_delete(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_move_and_delete')

        from_path = self.get_remote_path('move-from.txt')
        to_path = self.get_remote_path('move-to.txt')

        # Create the file to be moved ..
        conn.write('Data to move', from_path)

        # .. move it ..
        out = conn.move(from_path, to_path)
        self.assertTrue(out.is_ok, out.stderr)

        # .. the source is gone and the target exists ..
        self.assertFalse(conn.exists(from_path))
        self.assertTrue(conn.exists(to_path))

        # .. now delete the target ..
        _ = conn.delete(to_path)

        # .. and confirm it is gone too.
        self.assertFalse(conn.exists(to_path))

# ################################################################################################################################

    def test_delete_directory(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_delete_directory')
        remote_path = self.get_remote_path('delete-directory')

        _ = conn.create_directory(remote_path)
        self.assertTrue(conn.exists(remote_path))

        _ = conn.delete_directory(remote_path)
        self.assertFalse(conn.exists(remote_path))

# ################################################################################################################################

    def test_bad_host_is_reported(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        config = self.get_config('test_bad_host_is_reported')

        # Nothing listens on this port.
        host = self.server.host
        free_port = get_free_port()
        config.address = f'{host}:{free_port}'

        client = self.make_client(config)
        out = client.ping()

        self.assertFalse(out.is_ok)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
