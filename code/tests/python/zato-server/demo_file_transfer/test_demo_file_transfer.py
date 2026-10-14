# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file transfer demo set, turned on and off the way the Demo config screen does it. Once on, files dropped
# into each directory are picked up over SFTP, FTP, FTPS and SMB, a malformed invoice ends up in quarantine and
# the audit log has the transfers of each connection. Once off, nothing of the demo is left - no objects,
# no processes, no listening ports and no files.

# stdlib
import os
import shutil
import time

# SQLAlchemy
from sqlalchemy import create_engine, select

# pytest
import pytest

# Zato
from zato.common.audit_log.api import event_table
from zato.common.audit_log.common import AuditSource
from zato.common.sftp_local import has_sshd, LocalSFTPServer
from zato.common.util.local_server import is_expected_process, is_port_free, read_pid_file, stop_pid
from zato.server.demo_file_transfer import demo_server
from zato.server.demo_file_transfer.common import get_paths
from zato.server.demo_file_transfer.layout import All_Connections, FTP_Connections, get_connection_names, \
    SFTP_Connections, Shape_Invoices, Shape_Orders, SMB_Connections

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, callable_, intlist, stranydict, strlist
    from zato.server.demo_file_transfer.layout import ConnectionSpec, connection_spec_list

# ################################################################################################################################
# ################################################################################################################################

_set_name = 'file_transfer'

# How long the schedules may take to get through what they were given, in seconds - the slowest schedule
# runs every minute and its first run is up to half a minute after the import.
_processing_timeout = 180

# How long to sleep between two looks at the directories, in seconds
_poll_interval = 2

# What each schedule shape moves its files into once they are done with
_processed_directory = 'processed'
_quarantine_directory = 'quarantine'

# What the moved files of each shape end with
_shape_suffixes = {
    'invoices':  '.csv',
    'shipments': '.xml',
    'reports':   '.txt',
}

# ################################################################################################################################
# ################################################################################################################################

class _State:
    """ What one test finds out and a later one needs.
    """

    # The order files each connection's orders directory had right after the import
    seeded_orders:'anydict' = {}

    # The pids and ports of the two local servers while the demo is on
    sshd_pid = 0
    server_pid = 0
    ports:'intlist' = []

# ################################################################################################################################
# ################################################################################################################################

def _client(zato_server:'stranydict') -> 'AdminClient':
    out = zato_server['client']
    return out

# ################################################################################################################################

def _save(zato_server:'stranydict', is_on:'bool') -> 'anydict':
    """ Moves the file transfer slider the way the Demo config screen does.
    """
    client = _client(zato_server)

    request = {
        'func_name': 'save_demo_config',
        'states': {_set_name: is_on},
    }

    out = client.invoke('zato.server.invoker', request)
    return out

# ################################################################################################################################

def _get_items(zato_server:'stranydict') -> 'anydict':
    """ Whether each object of the set exists, by its name, along with whether the set is present.
    """
    client = _client(zato_server)
    response = client.invoke('zato.server.invoker', {'func_name': 'get_demo_config'})

    set_info = response['sets'][_set_name]

    out:'anydict' = {
        'is_present': set_info['is_present'],
        'items': {},
    }

    for group in set_info['groups']:
        for item in group['items']:
            out['items'][item['name']] = item['exists']

    return out

# ################################################################################################################################

def _wait_until(condition:'callable_', description:'str') -> 'None':
    """ Polls the condition until it holds, failing the test if it does not within the processing timeout.
    """
    deadline = time.monotonic() + _processing_timeout

    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(_poll_interval)

    pytest.fail(f'Timed out waiting for {description}')

# ################################################################################################################################

def _list_files(directory:'str', suffix:'str') -> 'strlist':
    """ The names of the files in the directory that end with the suffix, an empty list if there is no such directory.
    """
    out:'strlist' = []

    if not os.path.isdir(directory):
        return out

    for name in os.listdir(directory):
        if name.endswith(suffix):
            out.append(name)

    return out

# ################################################################################################################################

def _get_local_directory(spec:'ConnectionSpec', shape:'str') -> 'str':
    """ Where on disk one schedule of a demo connection polls.
    """
    paths = get_paths()

    if spec in SFTP_Connections:
        out = os.path.join(paths.sftp_files_dir, spec.account, shape)
    elif spec in FTP_Connections:
        out = os.path.join(paths.ftp_dir, spec.account, shape)
    else:
        out = os.path.join(paths.smb_dir, spec.account, shape)

    return out

# ################################################################################################################################

def _assert_processed(connections:'connection_spec_list') -> 'None':
    """ Waits until each schedule of each connection got through some of its files - a moved file is in its processed
    directory and the orders seeded at import time are deleted.
    """
    for spec in connections:
        for shape in spec.shapes:

            local_directory = _get_local_directory(spec, shape)
            description = f'{spec.name} -> {shape}'

            if shape == Shape_Orders:
                seeded = _State.seeded_orders[spec.name]
                assert seeded, f'No orders seeded for {description}'

                def _orders_deleted() -> 'bool':
                    remaining = _list_files(local_directory, '.json')
                    for name in seeded:
                        if name in remaining:
                            return False
                    return True

                _wait_until(_orders_deleted, description)

            else:
                processed_directory = os.path.join(local_directory, _processed_directory)
                suffix = _shape_suffixes[shape]

                def _has_processed() -> 'bool':
                    processed = _list_files(processed_directory, suffix)
                    return bool(processed)

                _wait_until(_has_processed, description)

# ################################################################################################################################

def _read_sshd_port(config_path:'str') -> 'int':
    """ The port the SSH server's configuration says it listens on, zero if it says nothing.
    """
    out = 0

    with open(config_path) as config_file:
        for line in config_file:
            if line.startswith('Port '):
                _, _, port = line.partition(' ')
                out = int(port)

    return out

# ################################################################################################################################

def _get_audit_counts(zato_server:'stranydict') -> 'anydict':
    """ How many outgoing file transfer events the audit log has per connection name.
    """
    engine = create_engine(f'sqlite:///{zato_server["audit_db_path"]}')

    query = select(event_table.c.object_name)
    query = query.where(event_table.c.source == AuditSource.File_Outgoing)

    out:'anydict' = {}

    try:
        with engine.connect() as connection:
            for row in connection.execute(query):
                object_name = row[0]
                out[object_name] = out.get(object_name, 0) + 1
    finally:
        engine.dispose()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDemoFileTransfer:

    def test_turning_on_imports_everything(self, zato_server:'stranydict') -> 'None':

        # The slider goes on ..
        response = _save(zato_server, True)

        assert response['success'] is True, response
        assert response['results'][_set_name] == {'action': 'imported', 'is_ok': True}

        # .. the orders already there are remembered before any schedule runs for the first time ..
        for spec in All_Connections:
            if Shape_Orders in spec.shapes:
                orders_directory = _get_local_directory(spec, Shape_Orders)
                _State.seeded_orders[spec.name] = _list_files(orders_directory, '.json')

        # .. the set is present, with each of its objects ..
        details = _get_items(zato_server)
        assert details['is_present'] is True

        for name, exists in details['items'].items():
            if name.startswith('sftp.') or name.startswith('demo.sftp.'):
                if not has_sshd():
                    continue
            assert exists, f'Expected {name} to exist'

        # .. and both local servers run.
        paths = get_paths()

        server_config = demo_server.read_config(paths)
        assert demo_server.is_running(paths, server_config)

        _State.server_pid = read_pid_file(paths.server_pid)
        _State.ports = demo_server.get_ports(server_config)

        if has_sshd():
            sftp_server = LocalSFTPServer(paths.sshd_dir, 0)
            _State.sshd_pid = sftp_server.read_pid()
            assert is_expected_process(_State.sshd_pid, sftp_server.config_path)

            sftp_port = _read_sshd_port(sftp_server.config_path)
            assert sftp_port

            _State.ports.append(sftp_port)

    def test_sftp_files_are_processed(self, zato_server:'stranydict') -> 'None':

        if not has_sshd():
            pytest.skip('No SSH server binary on this machine')

        _assert_processed(SFTP_Connections)

    def test_ftp_files_are_processed(self, zato_server:'stranydict') -> 'None':
        _assert_processed(FTP_Connections[:1])

    def test_ftps_files_are_processed(self, zato_server:'stranydict') -> 'None':
        _assert_processed(FTP_Connections[1:])

    def test_smb_files_are_processed(self, zato_server:'stranydict') -> 'None':
        _assert_processed(SMB_Connections)

    def test_malformed_invoices_are_quarantined(self, zato_server:'stranydict') -> 'None':

        for spec in All_Connections:
            if Shape_Invoices in spec.shapes:

                if spec in SFTP_Connections:
                    if not has_sshd():
                        continue

                invoices_directory = _get_local_directory(spec, Shape_Invoices)
                quarantine_directory = os.path.join(invoices_directory, _quarantine_directory)

                def _has_quarantined() -> 'bool':
                    quarantined = _list_files(quarantine_directory, '-malformed.csv')
                    return bool(quarantined)

                _wait_until(_has_quarantined, f'{spec.name} -> quarantine')

                # Only malformed invoices are ever quarantined
                for name in os.listdir(quarantine_directory):
                    assert '-malformed.csv' in name, f'Unexpected file in quarantine: {name}'

    def test_audit_log_has_transfers_of_each_connection(self, zato_server:'stranydict') -> 'None':

        for spec in All_Connections:

            if spec in SFTP_Connections:
                if not has_sshd():
                    continue

            def _has_events() -> 'bool':
                counts = _get_audit_counts(zato_server)
                return counts.get(spec.name, 0) > 0

            _wait_until(_has_events, f'audit events of {spec.name}')

    def test_resume_brings_back_a_wiped_demo(self, zato_server:'stranydict') -> 'None':

        paths = get_paths()
        server_config = demo_server.read_config(paths)
        ports_before = demo_server.get_ports(server_config)

        # Both local servers go away along with everything under the root, the way a reboot clears /tmp ..
        _ = stop_pid(_State.server_pid, paths.server_config)

        if _State.sshd_pid:
            sftp_server = LocalSFTPServer(paths.sshd_dir, 0)
            _ = stop_pid(_State.sshd_pid, sftp_server.config_path)

        shutil.rmtree(paths.root)

        # .. the server brings the demo back the way it does on startup ..
        client = _client(zato_server)
        _ = client.invoke('zato.server.invoker', {'func_name': 'resume_demo_file_transfer'})

        # .. the demo server runs again, on the same ports, with new passwords of its users ..
        server_config = demo_server.read_config(paths)
        assert demo_server.is_running(paths, server_config)
        assert demo_server.get_ports(server_config) == ports_before

        _State.server_pid = read_pid_file(paths.server_pid)

        # .. so does the SSH server, if there is one ..
        if _State.sshd_pid:
            sftp_server = LocalSFTPServer(paths.sshd_dir, 0)
            _State.sshd_pid = sftp_server.read_pid()
            assert is_expected_process(_State.sshd_pid, sftp_server.config_path)

        # .. and new files are picked up over each protocol, which needs the new passwords to have reached the connections.
        for spec in All_Connections:

            if spec in SFTP_Connections:
                if not has_sshd():
                    continue

            # The first shape of each connection moves its files once done with them
            first_shape = spec.shapes[0]

            local_directory = _get_local_directory(spec, first_shape)
            processed_directory = os.path.join(local_directory, _processed_directory)

            suffix = _shape_suffixes[first_shape]

            def _has_processed() -> 'bool':
                processed = _list_files(processed_directory, suffix)
                return bool(processed)

            _wait_until(_has_processed, f'{spec.name} -> {first_shape} after the resume')

    def test_turning_off_removes_everything(self, zato_server:'stranydict') -> 'None':

        # The slider goes off ..
        response = _save(zato_server, False)

        assert response['success'] is True, response
        assert response['results'][_set_name] == {'action': 'removed', 'is_ok': True}

        # .. none of the objects is left ..
        details = _get_items(zato_server)
        assert details['is_present'] is False

        for name, exists in details['items'].items():
            assert not exists, f'Expected {name} to be gone'

        # .. that is, each of the connections too ..
        connection_names = get_connection_names(All_Connections)

        for name in connection_names:
            assert name in details['items'], f'Expected {name} among the objects of the set'
            assert not details['items'][name], f'Expected {name} to be gone'

        # .. both processes are gone ..
        paths = get_paths()

        assert not is_expected_process(_State.server_pid, paths.server_config)

        if _State.sshd_pid:
            sftp_server = LocalSFTPServer(paths.sshd_dir, 0)
            assert not is_expected_process(_State.sshd_pid, sftp_server.config_path)

        # .. their ports are free ..
        for port in _State.ports:
            assert is_port_free(port), f'Port {port} is still taken'

        # .. and so is the root directory.
        assert not os.path.exists(paths.root), f'Expected {paths.root} to be gone'

# ################################################################################################################################
# ################################################################################################################################
