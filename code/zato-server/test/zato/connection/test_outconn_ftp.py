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
from zato.common.test.ftp_ import FTPTestServer
from zato.common.typing_ import cast_
from zato.server.connection.ftp import FTPConnection
from zato.server.generic.api.outconn_ftp import FTPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_Should_Test = 'Zato_Test_FTP'

# ################################################################################################################################
# ################################################################################################################################

# Letters from four alphabets - file names and file contents in the tests below
# use them all to prove that Unicode round trips are byte-for-byte exact.
Ascii_Letters       = 'ABCDEF'
Dutch_Letters       = 'ÁÉÍÓÚË'
Dutch_Letters_Lower = 'áéíóúë'
Greek_Letters       = 'ΑΒΓΔΕΖ'
Greek_Letters_Lower = 'αβγδεζ'
Korean_Letters      = 'ㄱㄴㄷㄹㅁㅂ'

All_Letters = Ascii_Letters + Dutch_Letters + Dutch_Letters_Lower + Greek_Letters + Greek_Letters_Lower + Korean_Letters

# ################################################################################################################################
# ################################################################################################################################

class _TestWrapperClient:
    """ A context manager that hands out the one client that the test wrapper holds.
    """
    def __init__(self, client:'FTPClient') -> 'None':
        self.client_object = client

# ################################################################################################################################

    def __enter__(self) -> 'FTPClient':
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
    def __init__(self, client:'FTPClient') -> 'None':
        self.client_object        = client
        self.should_store_content = False
        self.audit_log            = AuditLog('test-outconn-ftp')

        self.config = Bunch()
        self.config.name = 'test-outconn-ftp'

# ################################################################################################################################

    def client(self, **kwargs:'any_') -> '_TestWrapperClient':
        out = _TestWrapperClient(self.client_object)
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        self.client_object.ping()

# ################################################################################################################################
# ################################################################################################################################

class OutconnFTPTestCase(TestCase):
    """ Tests the outgoing FTP connection API against a plain FTP server.
    """

    server: 'FTPTestServer'

    # Whether the server under test speaks FTPS
    use_ssl = False

    @classmethod
    def setUpClass(class_) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        # The audit log is pointed at a throwaway SQLite database for the duration of the suite.
        audit_db_dir = mkdtemp(prefix='zato-test-ftp-audit-')
        os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
        os.environ[AuditLogCtx.Env_Name] = os.path.join(audit_db_dir, 'audit.db')

        class_.server = FTPTestServer(use_ssl=class_.use_ssl)
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

    def get_config(self, conn_name:'str') -> 'Bunch':

        config = bunchify({
            'id': 1,
            'name': conn_name,
            'is_active': True,
            'host': self.server.host,
            'port': self.server.port,
            'username': self.server.username,
            'secret': self.server.password,
            'use_ssl': self.use_ssl,
        })

        out = cast_('Bunch', config)
        return out

# ################################################################################################################################

    def get_client(self, conn_name:'str') -> 'FTPClient':

        config = self.get_config(conn_name)
        server = cast_('any_', None)
        out = FTPClient(config, server)

        return out

# ################################################################################################################################

    def get_conn(self, conn_name:'str') -> 'FTPConnection':

        client = self.get_client(conn_name)
        wrapper = _TestWrapper(client)
        wrapper_typed = cast_('any_', wrapper)

        out = FTPConnection('test-cid', wrapper_typed)

        return out

# ################################################################################################################################

    def get_file_name(self, suffix:'str') -> 'str':
        """ Builds a unique file name that contains letters from all four alphabets.
        """

        hex_string = CryptoManager.generate_hex_string()
        out = f'test-{hex_string}-{All_Letters}-{suffix}'

        return out

# ################################################################################################################################

    def get_local_path(self, file_name:'str') -> 'str':
        """ Returns the on-disk path backing the given file in the server's directory.
        """

        out = os.path.join(self.server.files_dir, file_name)

        return out

# ################################################################################################################################

    def test_ping(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        client = self.get_client('test_ping')
        client.ping()

# ################################################################################################################################

    def test_write_and_read(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_write_and_read')

        data = 'Test FTP write data ' + All_Letters
        file_name = self.get_file_name('write.txt')

        # Write the data out ..
        conn.write(data, file_name)

        # .. read it back through the connection ..
        result = conn.read(file_name)
        self.assertEqual(result.decode('utf8'), data)

        # .. and confirm the bytes actually landed on disk, under the expected name.
        local_path = self.get_local_path(file_name)
        expected = data.encode('utf8')

        with open(local_path, 'rb') as local_file:
            on_disk = local_file.read()
            self.assertEqual(on_disk, expected)

# ################################################################################################################################

    def test_write_overwrites_existing_files(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_write_overwrites_existing_files')

        file_name = self.get_file_name('overwrite.txt')

        # Write the initial data ..
        initial_data = 'Initial data ' + All_Letters
        conn.write(initial_data, file_name)

        # .. overwrite it ..
        data = 'New data ' + All_Letters
        conn.write(data, file_name)

        # .. and expect to read back the new contents only.
        result = conn.read(file_name)
        self.assertEqual(result.decode('utf8'), data)

# ################################################################################################################################

    def test_upload_and_download_file(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_upload_and_download_file')

        data = 'Test FTP upload data ' + All_Letters
        file_name = self.get_file_name('upload.txt')

        # A local file to upload ..
        with NamedTemporaryFile('w+', suffix='-zato-test-ftp.txt', encoding='utf8') as local_file:
            _ = local_file.write(data)
            local_file.flush()

            # .. upload it ..
            conn.upload(local_file.name, file_name)

        # .. the uploaded bytes are on the server's disk ..
        local_path = self.get_local_path(file_name)
        expected = data.encode('utf8')

        with open(local_path, 'rb') as uploaded:
            on_disk = uploaded.read()
            self.assertEqual(on_disk, expected)

        # .. download it to another local path ..
        with NamedTemporaryFile('w+', suffix='-zato-test-ftp.txt', encoding='utf8') as download_file:
            conn.download_file(file_name, download_file.name)

            # .. and confirm the round trip did not change the contents.
            with open(download_file.name, encoding='utf8') as downloaded:
                downloaded_data = downloaded.read()
                self.assertEqual(downloaded_data, data)

# ################################################################################################################################

    def test_exists(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_exists')

        file_name = self.get_file_name('exists.txt')

        # The file does not exist yet ..
        self.assertFalse(conn.exists(file_name))

        # .. create it ..
        data = 'Test data ' + All_Letters
        conn.write(data, file_name)

        # .. and now it does exist.
        self.assertTrue(conn.exists(file_name))

# ################################################################################################################################

    def test_list(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_list')

        directory_name = self.get_file_name('list-directory')

        first_name = self.get_file_name('first.txt')
        second_name = self.get_file_name('second.txt')

        # Create a directory with two files inside ..
        conn.create_directory(directory_name)

        first_data = 'First file ' + All_Letters
        first_path = directory_name + '/' + first_name

        second_data = 'Second file ' + All_Letters
        second_path = directory_name + '/' + second_name

        conn.write(first_data, first_path)
        conn.write(second_data, second_path)

        # .. list the directory ..
        result = conn.list(directory_name)

        # .. and make sure both files were returned under their exact original names,
        # .. Unicode letters included.
        names = []
        for item in result:
            names.append(item.name)

        self.assertIn(first_name, names)
        self.assertIn(second_name, names)

# ################################################################################################################################

    def test_get_info(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_get_info')

        data = 'Test data for get_info ' + All_Letters
        file_name = self.get_file_name('info.txt')

        conn.write(data, file_name)

        info = conn.get_info(file_name)

        data_bytes = data.encode('utf8')
        expected_size = len(data_bytes)

        self.assertTrue(info.is_file)
        self.assertFalse(info.is_directory)
        self.assertEqual(info.size, expected_size)
        self.assertEqual(info.name, file_name)

# ################################################################################################################################

    def test_create_directory_and_entry_types(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_create_directory_and_entry_types')

        directory_name = self.get_file_name('directory')

        # The directory does not exist yet ..
        self.assertFalse(conn.exists(directory_name))

        # .. create it ..
        conn.create_directory(directory_name)

        # .. and confirm what the server reports about it.
        self.assertTrue(conn.exists(directory_name))
        self.assertTrue(conn.is_directory(directory_name))

        # A file created in that directory is a file, not a directory.
        file_name = self.get_file_name('file.txt')
        file_path = directory_name + '/' + file_name

        data = 'Test data ' + All_Letters
        conn.write(data, file_path)

        self.assertTrue(conn.is_file(file_path))
        self.assertFalse(conn.is_directory(file_path))

# ################################################################################################################################

    def test_create_directory_makes_nested_paths(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_create_directory_makes_nested_paths')

        top_name = self.get_file_name('nested')
        nested_path = top_name + '/level-one/level-two'

        # One call makes every component of the path ..
        conn.create_directory(nested_path)

        self.assertTrue(conn.is_directory(nested_path))

        # .. and with exist_ok, making it again is not an error.
        conn.create_directory(nested_path, exist_ok=True)

        # Without exist_ok, a path that is already there is refused.
        with self.assertRaises(Exception):
            conn.create_directory(nested_path)

# ################################################################################################################################

    def test_move_and_delete(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_move_and_delete')

        from_name = self.get_file_name('move-from.txt')
        to_name = self.get_file_name('move-to.txt')

        data = 'Data to move ' + All_Letters

        # Create the file to be moved ..
        conn.write(data, from_name)

        # .. move it ..
        conn.move(from_name, to_name)

        # .. the source is gone and the target exists, both through the API and on disk ..
        self.assertFalse(conn.exists(from_name))
        self.assertTrue(conn.exists(to_name))

        self.assertFalse(os.path.exists(self.get_local_path(from_name)))
        self.assertTrue(os.path.exists(self.get_local_path(to_name)))

        # .. the contents survived the move ..
        result = conn.read(to_name)
        self.assertEqual(result.decode('utf8'), data)

        # .. now delete the target ..
        conn.delete_file(to_name)

        # .. and confirm it is gone too.
        self.assertFalse(conn.exists(to_name))
        self.assertFalse(os.path.exists(self.get_local_path(to_name)))

# ################################################################################################################################

    def test_delete_directory(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_delete_directory')

        directory_name = self.get_file_name('delete-directory')

        conn.create_directory(directory_name)
        self.assertTrue(conn.exists(directory_name))

        conn.delete_directory(directory_name)
        self.assertFalse(conn.exists(directory_name))

# ################################################################################################################################

    def test_execute_shell_commands(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_shell_commands')

        directory_name = self.get_file_name('shell-directory')
        file_name = self.get_file_name('shell.txt')
        file_path = directory_name + '/' + file_name

        # A directory with one file in it, made through the API rather than through the shell.
        conn.create_directory(directory_name)

        data = 'Shell data ' + All_Letters
        conn.write(data, file_path)

        # One run covers a listing, a stat and an existence check.
        commands = f'ls {directory_name}\nstat {file_path}\nexists {file_path}'
        result = conn.execute(commands)

        self.assertTrue(result.is_ok)
        self.assertEqual(result.command_no, 3)
        self.assertIn(file_name, result.stdout)
        self.assertIn('True', result.stdout)
        self.assertEqual(result.stderr, '')

# ################################################################################################################################

    def test_execute_unknown_command(self) -> 'None':
        if not os.environ.get(ModuleCtx.Env_Key_Should_Test):
            return

        conn = self.get_conn('test_execute_unknown_command')

        result = conn.execute('chmod 644 file.txt', raise_on_error=False)

        self.assertFalse(result.is_ok)
        self.assertIn('Unknown command', result.stderr)

# ################################################################################################################################
# ################################################################################################################################

class OutconnFTPSTestCase(OutconnFTPTestCase):
    """ The whole suite once more, this time against a server that requires TLS on both channels.
    """
    use_ssl = True

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
