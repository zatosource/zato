# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import NamedTemporaryFile
from unittest import main, TestCase
from uuid import uuid4

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from zato.common.test.sftp_ import SFTPTestServer
from zato.common.typing_ import cast_
from zato.common.util.tcp import get_free_port
from zato.server.connection.sftp import SFTPConnection
from zato.server.generic.api.outconn_sftp import SFTPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.sftp import SFTPOutput
    from zato.common.typing_ import any_
    any_ = any_
    SFTPOutput = SFTPOutput

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_SFTP'

# ################################################################################################################################
# ################################################################################################################################

class _TestWrapperClient:
    """ A context manager that hands out the one client that the test wrapper holds.
    """
    def __init__(self, client:'SFTPClient') -> 'None':
        self.client_object = client

    def __enter__(self) -> 'SFTPClient':
        return self.client_object

    def __exit__(self, _type:'object', _value:'object', _traceback:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class _TestWrapper:
    """ A minimal stand-in for OutconnSFTPWrapper - it exposes the same .client and .ping API
    but holds a single client object directly instead of a queue.
    """
    def __init__(self, client:'SFTPClient') -> 'None':
        self.client_object = client

    def client(self) -> '_TestWrapperClient':
        return _TestWrapperClient(self.client_object)

    def ping(self) -> 'None':
        out = self.client_object.ping()
        if not out.is_ok:
            raise Exception(out.stderr)

# ################################################################################################################################
# ################################################################################################################################

class OutconnSFTPTestCase(TestCase):

    server: 'SFTPTestServer'

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.server = SFTPTestServer()
        class_.server.start()

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        class_.server.stop()

# ################################################################################################################################

    def get_config(self, conn_name:'str', *, use_password:'bool'=False) -> 'Bunch':

        # With a password in use, we authenticate with the encrypted key whose passphrase
        # is the connection's password, going through the askpass helper.
        if use_password:
            private_key = self.server.client_key_encrypted_path
            secret = self.server.password
        else:
            private_key = self.server.client_key_path
            secret = ''

        config = bunchify({
            'id': 1,
            'name': conn_name,
            'is_active': True,
            'address': '{}:{}'.format(self.server.host, self.server.port),
            'username': self.server.username,
            'secret': secret,
            'private_key': private_key,

            # The test server's host key is freshly generated, which means it cannot be in known_hosts yet
            'strict_host_key_checking': False,
        })

        return config

# ################################################################################################################################

    def make_client(self, config:'Bunch') -> 'SFTPClient':

        client = SFTPClient(config, cast_('any_', None))

        # Keep the throwaway host keys of test servers out of the user's known_hosts file
        client.base_args.append('-o')
        client.base_args.append('UserKnownHostsFile=/dev/null')

        return client

# ################################################################################################################################

    def get_client(self, conn_name:'str', *, use_password:'bool'=False) -> 'SFTPClient':

        config = self.get_config(conn_name, use_password=use_password)
        client = self.make_client(config)

        return client

# ################################################################################################################################

    def get_conn(self, conn_name:'str', *, use_password:'bool'=False) -> 'SFTPConnection':

        client = self.get_client(conn_name, use_password=use_password)
        wrapper = _TestWrapper(client)

        conn = SFTPConnection('test-cid', cast_('any_', wrapper))

        return conn

# ################################################################################################################################

    def get_remote_path(self, suffix:'str') -> 'str':

        out = os.path.join(self.server.files_dir, 'test-{}-{}'.format(uuid4().hex, suffix))

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
        out = conn.execute('ls {}'.format(self.server.files_dir))

        self.assertTrue(out.is_ok, out.stderr)

# ################################################################################################################################

    def test_execute_with_password(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_with_password', use_password=True)
        out = conn.execute('ls {}'.format(self.server.files_dir))

        self.assertTrue(out.is_ok, out.stderr)

# ################################################################################################################################

    def test_execute_error_is_reported(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_error_is_reported')
        missing_path = self.get_remote_path('missing-dir')

        out = conn.execute('ls {}'.format(missing_path), raise_on_error=False)

        self.assertFalse(out.is_ok)

# ################################################################################################################################

    def test_wrong_key_is_rejected(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # Generate a key that the server does not know about
        rejected_key_path = os.path.join(self.server.base_dir, 'rejected_key')
        self.server.generate_key(rejected_key_path)

        config = self.get_config('test_wrong_key_is_rejected')
        config.private_key = rejected_key_path

        client = self.make_client(config)
        out = client.ping()

        self.assertFalse(out.is_ok)

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
                self.assertEqual(downloaded.read(), data)

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

        self.assertIn('already exists', str(ctx.exception))

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

        # A file created in that directory is a file, not a directory
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

        self.assertIsNotNone(info)
        self.assertTrue(info.is_file)
        self.assertEqual(info.size, len(data))
        self.assertEqual(info.name, remote_path)

# ################################################################################################################################

    def test_list(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_list')
        remote_path = self.get_remote_path('list-directory')

        # Create a directory with two files inside ..
        _ = conn.create_directory(remote_path)
        conn.write('First file', os.path.join(remote_path, 'first.txt'))
        conn.write('Second file', os.path.join(remote_path, 'second.txt'))

        # .. list the directory ..
        result = conn.list(remote_path)

        # .. and make sure both files were returned - the server may report them
        # .. under their full paths, which is why only the base names are compared.
        self.assertIsNotNone(result)

        names = []
        for item in result:
            names.append(os.path.basename(item.name))

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

        # Nothing listens on this port, so the connection attempt must fail
        config.address = '{}:{}'.format(self.server.host, get_free_port())

        client = self.make_client(config)
        out = client.ping()

        self.assertFalse(out.is_ok)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
