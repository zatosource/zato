# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from logging import getLogger
from stat import S_ISDIR, S_ISLNK

# gevent
from gevent.fileobject import FileObjectThread

# humanize
from humanize import naturalsize

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.server.generic.api.outconn_smb import OutconnSMBWrapper, SMBClient
    SMBClient = SMBClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EntryType:
    file = 'file'
    directory = 'directory'
    symlink = 'symlink'

# ################################################################################################################################

smb_info_list = list['SMBInfo']

# ################################################################################################################################
# ################################################################################################################################

class SMBInfo:
    __slots__ = 'type', 'name', 'size', 'last_modified'

    def __init__(self) -> 'None':
        self.type = '' # type: str
        self.name = '' # type: str

        self.size = 0 # type: int

        self.last_modified = None # type: any_

# ################################################################################################################################

    def to_dict(self, skip_last_modified:'bool'=True) -> 'stranydict':

        out = {
            'type': self.type,
            'name': self.name,
            'size': self.size,
            'size_human': self.size_human,
            'is_file': self.is_file,
            'is_directory': self.is_directory,
            'is_symlink': self.is_symlink,

            'last_modified_iso': self.last_modified_iso,
        }

        # We do not return it by default so as not to make JSON serializers wonder what to do with a Python object
        if not skip_last_modified:
            out['last_modified'] = self.last_modified

        return out

# ################################################################################################################################

    @property
    def is_file(self) -> 'bool':
        return self.type == EntryType.file

# ################################################################################################################################

    @property
    def is_directory(self) -> 'bool':
        return self.type == EntryType.directory

# ################################################################################################################################

    @property
    def is_symlink(self) -> 'bool':
        return self.type == EntryType.symlink

# ################################################################################################################################

    @property
    def last_modified_iso(self) -> 'str':
        return self.last_modified.isoformat()

# ################################################################################################################################

    @property
    def size_human(self) -> 'str':
        return naturalsize(self.size)

# ################################################################################################################################
# ################################################################################################################################

class SMBConnection:
    """ The public API of a single outgoing SMB connection, obtained via self.smb['My Connection'] in services.

    Remote paths always include the share name and use forward slashes, e.g. MyShare/documents/invoice.pdf.
    """
    def __init__(self, cid:'str', wrapper:'OutconnSMBWrapper') -> 'None':
        self.cid = cid
        self.wrapper = wrapper

# ################################################################################################################################

    def ping(self) -> 'None':
        self.wrapper.ping()

# ################################################################################################################################

    def _build_info_from_stat(self, name:'str', stat_result:'any_') -> 'SMBInfo':

        # Our response to produce
        out = SMBInfo()

        # Map the mode bits to one of our entry types ..
        if S_ISLNK(stat_result.st_mode):
            entry_type = EntryType.symlink
        elif S_ISDIR(stat_result.st_mode):
            entry_type = EntryType.directory
        else:
            entry_type = EntryType.file

        # .. and populate everything before returning.
        out.type = entry_type
        out.name = name
        out.size = stat_result.st_size

        # The timestamp is made UTC-aware so it compares equal to what directory listings return -
        # their modification times come from the SMB protocol layer as UTC-aware datetime objects.
        out.last_modified = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc)

        return out

# ################################################################################################################################

    def get_info(self, remote_path:'str') -> 'SMBInfo':

        # Ask the remote server about the path ..
        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            stat_result = client.stat(remote_path)

        # .. the entry's name is the last part of the input path ..
        name = remote_path.rstrip('/').split('/')[-1]

        # .. and now we can build the full response.
        out = self._build_info_from_stat(name, stat_result)

        return out

# ################################################################################################################################

    def exists(self, remote_path:'str') -> 'bool':

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            out = client.exists(remote_path)

        return out

# ################################################################################################################################

    def is_file(self, remote_path:'str') -> 'bool':

        info = self.get_info(remote_path)

        out = info.is_file
        return out

# ################################################################################################################################

    def is_directory(self, remote_path:'str') -> 'bool':

        info = self.get_info(remote_path)

        out = info.is_directory
        return out

# ################################################################################################################################

    def _build_info_from_dir_entry(self, entry:'any_') -> 'SMBInfo':

        # Our response to produce
        out = SMBInfo()

        # Map the entry's attributes to one of our entry types ..
        if entry.is_symlink():
            entry_type = EntryType.symlink
        elif entry.is_dir():
            entry_type = EntryType.directory
        else:
            entry_type = EntryType.file

        # .. the size and modification time are already in the listing itself,
        # .. which means that no further network calls are needed ..
        smb_info = entry.smb_info

        # .. and populate everything before returning.
        out.type = entry_type
        out.name = entry.name
        out.size = smb_info.end_of_file
        out.last_modified = smb_info.last_write_time

        return out

# ################################################################################################################################

    def list(self, remote_path:'str') -> 'smb_info_list':

        # Our response to produce
        out:'smb_info_list' = []

        # List the remote directory ..
        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            entries = client.scandir(remote_path)

        # .. and turn each entry into our common info object.
        for entry in entries:
            info = self._build_info_from_dir_entry(entry)
            out.append(info)

        return out

# ################################################################################################################################

    def delete_file(self, remote_path:'str') -> 'None':

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            client.remove(remote_path)

# ################################################################################################################################

    def delete_directory(self, remote_path:'str') -> 'None':

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            client.rmdir(remote_path)

# ################################################################################################################################

    def create_directory(self, remote_path:'str', exist_ok:'bool'=False) -> 'None':

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            client.makedirs(remote_path, exist_ok)

# ################################################################################################################################

    def move(self, from_path:'str', to_path:'str') -> 'None':

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            client.rename(from_path, to_path)

    rename = move

# ################################################################################################################################

    def read(self, remote_path:'str') -> 'bytes':

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            out = client.read(remote_path)

        return out

# ################################################################################################################################

    def write(self, data:'any_', remote_path:'str', encoding:'str'='utf8') -> 'None':

        # Data to be written out must be always bytes
        if not isinstance(data, bytes):
            data = data.encode(encoding)

        with self.wrapper.client() as client:
            client = cast_('SMBClient', client)
            client.write(remote_path, data)

# ################################################################################################################################

    def upload(self, local_path:'str', remote_path:'str') -> 'None':

        # Read the local file in using a separate thread so as not to block the event loop ..
        thread_file = FileObjectThread(local_path, 'rb')
        data = thread_file.read()
        thread_file.close()

        # .. and write it out to the remote location.
        self.write(data, remote_path)

# ################################################################################################################################

    def download_file(self, remote_path:'str', local_path:'str') -> 'None':

        # Read the remote file in first ..
        data = self.read(remote_path)

        # .. and write it out locally using a separate thread so as not to block the event loop.
        thread_file = FileObjectThread(local_path, 'wb')
        _ = thread_file.write(data)
        thread_file.close()

    download = download_file

# ################################################################################################################################
# ################################################################################################################################
