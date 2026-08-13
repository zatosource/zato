# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a file transfer schedule run reaches for when it is exercised offline - a connection
# over a local directory behind the same client interface the SMB wrapper drives, the dispatch
# service around it and the query helpers the checks read the trail with.

# stdlib
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from logging import getLogger

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.server.connection.smb import SMBConnection

# Test support
from audit_env import Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# The name the connection under test goes by
Connection_Name = 'test.smb.schedule'

# The schedule and the service the files flow through
Schedule_Name = 'Daily results'
Target_Service = 'my.results.handler'

# The run's own cid, what the dispatch service would carry
Run_Cid = 'cid-schedule-run-1'

# The directory the schedule polls, relative to the local base directory
Directory = 'share/incoming'

# The file the checks move
File_Name = 'report.csv'
File_Content = b'code,label\nA1,First\nA2,Second\n'

# What the failing target service says
Service_Error = 'The target system is down'

# ################################################################################################################################
# ################################################################################################################################

class _ScanEntry:
    """ One directory listing entry of the shape the SMB client returns.
    """

    def __init__(self, dir_entry:'os.DirEntry') -> 'None':
        stat_result = dir_entry.stat()

        self.name = dir_entry.name
        self._is_dir = dir_entry.is_dir()
        self._is_symlink = dir_entry.is_symlink()

        self.smb_info = Bunch()
        self.smb_info.end_of_file = stat_result.st_size
        self.smb_info.last_write_time = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc)

    def is_dir(self) -> 'bool':
        return self._is_dir

    def is_symlink(self) -> 'bool':
        return self._is_symlink

# ################################################################################################################################

class LocalDirectoryClient:
    """ The client interface the SMB wrapper drives, backed by a local directory.
    """

    def __init__(self, base_dir:'str') -> 'None':
        self.base_dir = base_dir

    def _full_path(self, remote_path:'str') -> 'str':
        out = os.path.join(self.base_dir, remote_path)
        return out

    def exists(self, remote_path:'str') -> 'bool':
        out = os.path.exists(self._full_path(remote_path))
        return out

    def scandir(self, remote_path:'str') -> 'anylist':
        out:'anylist' = []

        for dir_entry in os.scandir(self._full_path(remote_path)):
            entry = _ScanEntry(dir_entry)
            out.append(entry)

        return out

    def stat(self, remote_path:'str') -> 'os.stat_result':
        out = os.stat(self._full_path(remote_path))
        return out

    def read(self, remote_path:'str') -> 'bytes':
        with open(self._full_path(remote_path), 'rb') as file:
            out = file.read()
        return out

    def rename(self, from_path:'str', to_path:'str') -> 'None':
        os.rename(self._full_path(from_path), self._full_path(to_path))

    def remove(self, remote_path:'str') -> 'None':
        os.remove(self._full_path(remote_path))

    def makedirs(self, remote_path:'str', exist_ok:'bool') -> 'None':
        os.makedirs(self._full_path(remote_path), exist_ok=exist_ok)

# ################################################################################################################################

class ClaimRefusingClient(LocalDirectoryClient):
    """ A directory whose files another consumer keeps claiming first - every rename fails.
    """

    def rename(self, from_path:'str', to_path:'str') -> 'None':
        raise Exception('Renamed by another consumer first')

# ################################################################################################################################

class WrapperStub:
    """ Stands in for the connection wrapper - it hands over the local-directory client
    and carries the audit writer and the content storage flag the real one carries.
    """

    def __init__(self, client:'LocalDirectoryClient', *, should_store_content:'bool') -> 'None':
        self._client = client
        self.should_store_content = should_store_content
        self.audit_log = AuditLog(Server_Name)

        self.config = Bunch()
        self.config.name = Connection_Name

    @contextmanager
    def client(self, *, should_block:'bool', block_timeout:'int') -> 'any_':
        yield self._client

# ################################################################################################################################

class ServiceStub:
    """ Stands in for the dispatch service - it remembers what the schedule handed
    to the target service where a live server would have invoked it.
    """

    def __init__(self, conn:'SMBConnection') -> 'None':
        self.cid = Run_Cid
        self.logger = getLogger('test-file-transfer-schedule')
        self.smb = {Connection_Name: conn}
        self.invoked:'anylist' = []

    def invoke(self, service_name:'str', item:'any_') -> 'None':
        self.invoked.append((service_name, item))

# ################################################################################################################################

class FailingServiceStub(ServiceStub):
    """ A dispatch service whose target service is down - every invocation fails.
    """

    def invoke(self, service_name:'str', item:'any_') -> 'None':
        raise Exception(Service_Error)

# ################################################################################################################################
# ################################################################################################################################

def new_environment(
    tmp_path:'any_',
    *,
    client_class:'type'=LocalDirectoryClient,
    service_class:'type'=ServiceStub,
    should_store_content:'bool'=False,
    file_names:'anylist | None'=None,
    ) -> 'tuple[ServiceStub, stranydict, str]':
    """ Builds one run's environment - the polled directory with its files on disk,
    the connection over it and the dispatch service around the connection.
    Returns the service, the context and the local base directory.
    """
    base_dir = os.path.join(str(tmp_path), 'files')
    os.makedirs(os.path.join(base_dir, Directory))

    if file_names is None:
        file_names = [File_Name]

    for file_name in file_names:
        with open(os.path.join(base_dir, Directory, file_name), 'wb') as file:
            _ = file.write(File_Content)

    client = client_class(base_dir)
    wrapper = WrapperStub(client, should_store_content=should_store_content)
    conn = SMBConnection(Run_Cid, cast_('any_', wrapper))

    service = service_class(conn)

    context = {
        _scheduler.Extra_Conn_Name: Connection_Name,
        _scheduler.Extra_Conn_Type: FileTransfer.ConnType.SMB,
    }

    return service, context, base_dir

# ################################################################################################################################

def new_schedule(**overrides:'any_') -> 'stranydict':
    """ A schedule of the shape the dispatch context carries, with sensible test defaults.
    """
    out:'stranydict' = {
        'name': Schedule_Name,
        'directory': Directory,
        'pattern': '*',
        'ready_how': _scheduler.ReadyHow.Stability,
        'stability_delay': 0,
        'marker_suffix': _scheduler.Default_Marker_Suffix,
        'should_claim': False,
        'service': Target_Service,
        'on_success': _scheduler.OnSuccess.Move,
        'move_directory': _scheduler.Default_Move_Directory,
    }
    out.update(overrides)
    return out

# ################################################################################################################################

def get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            event = dict(row._mapping)
            out.append(event)

    return out

# ################################################################################################################################

def get_attrs(event_id:'int') -> 'stranydict':
    """ The searchable attributes of one event, by name.
    """
    engine = get_audit_engine()

    query = select(event_attr_table.c.name, event_attr_table.c.value)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'stranydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            name = row[0]
            out[name] = row[1]

    return out

# ################################################################################################################################

def events_of_type(events:'anylist', event_type:'str') -> 'anylist':
    """ The events of one type, in the order they were written.
    """
    out:'anylist' = []

    for item in events:
        if item['event_type'] == event_type:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
