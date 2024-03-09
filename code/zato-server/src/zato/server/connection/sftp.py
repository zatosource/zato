# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# pylint: disable=attribute-defined-outside-init

# stdlib
from datetime import date, datetime
from logging import getLogger
from tempfile import NamedTemporaryFile
from time import strptime
from traceback import format_exc

# gevent
from gevent.fileobject import FileObjectThread

# humanize
from humanize import naturalsize

# Zato
from zato.common.api import SFTP
from zato.common.broker_message import OUTGOING
from zato.common.json_internal import loads
from zato.common.sftp import SFTPOutput

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:
    from typing import List
    from zato.server.base.parallel import ParallelServer

    # For pyflakes
    List = List
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class EntryType:
    file = 'file'
    directory = 'directory'
    symlink = 'symlink'
    other = 'other'

    @staticmethod
    def get_entry_type(prefix):
        entry_map = {
            '-': EntryType.file,
            'd': EntryType.directory,
            'l': EntryType.symlink
        }

        return entry_map.get(prefix) or EntryType.other

# ################################################################################################################################

_other_types_check = EntryType.file, EntryType.directory, EntryType.symlink

# ################################################################################################################################
# ################################################################################################################################

class SFTPInfo:
    __slots__ = 'type', 'name', 'owner', 'group', 'size', 'permissions', 'permissions_oct', 'last_modified'

    def __init__(self):
        self.type = None # type: str
        self.name = None # type: str

        self.size = None       # type: int

        self.owner = None # type: str
        self.group = None # type: str

        self.permissions = None      # type: int
        self.permissions_oct = None  # type: str

        self.last_modified = None # type: date

# ################################################################################################################################

    def to_dict(self, skip_last_modified=True):
        # type: () -> dict

        out = {
            'type': self.type,
            'name': self.name,
            'size': self.size,
            'size_human': self.size_human,
            'owner': self.owner,
            'group': self.group,
            'permissions': self.permissions,
            'permissions_oct': self.permissions_oct,
            'is_file': self.is_file,
            'is_directory': self.is_directory,
            'is_symlink': self.is_symlink,
            'is_other': self.is_other,

            'last_modified_iso': self.last_modified_iso,
        }

        # We do not return it by default so as not to make JSON serializers wonder what to do with a Python object
        if not skip_last_modified:
            out['last_modified'] = self.last_modified

        return out

# ################################################################################################################################

    @property
    def is_file(self):
        # type: () -> bool
        return self.type.startswith(EntryType.file)

# ################################################################################################################################

    @property
    def is_directory(self):
        # type: () -> bool
        return self.type.startswith(EntryType.directory)

# ################################################################################################################################

    @property
    def is_symlink(self):
        # type: () -> bool
        return self.type.startswith(EntryType.symlink)

# ################################################################################################################################

    @property
    def is_other(self):
        # type: () -> bool
        return not self.type.startswith(_other_types_check)

# ################################################################################################################################

    @property
    def last_modified_iso(self):
        # type: () -> str
        return self.last_modified.isoformat()

# ################################################################################################################################

    @property
    def size_human(self):
        # type: () -> str
        return naturalsize(self.size)

# ################################################################################################################################
# ################################################################################################################################

class SFTPIPCFacade:
    """ Provides servers and services with access to SFTP resources.
    """
    def __init__(self, server, config):
        # type: (ParallelServer, dict) -> None
        self.cid = None # Not used for now
        self.server = server
        self.config = config

# ################################################################################################################################

    def ping(self):
        # type: (dict) -> None
        self.server.connector_sftp.ping_sftp(**{
            'id': self.config['id']
        })

# ################################################################################################################################

    def _execute(self, data, log_level, raise_on_error=True, _execute_value=OUTGOING.SFTP_EXECUTE.value):
        # type: (str, int, int) -> SFTPOutput

        if log_level > 0:
            logger.info('Executing cid:`%s` `%s`', self.cid, data)

        # Prepare input message
        msg = {}
        msg['action'] = _execute_value
        msg['cid'] = self.cid
        self.data = data

        # Invoke the connector
        response = self.server.connector_sftp.invoke_sftp_connector({
            'id': self.config['id'],
            'action': _execute_value,
            'cid': self.cid,
            'data': data,
            'log_level': str(log_level)
        })

        # Read in the JSON response - this will always succeed
        response = loads(response.text)

        if log_level > 0:
            logger.info('Response received, cid:`%s`, data:`%s`', self.cid, response)

        # Perhaps we are to raise an exception on an error encountered
        if not response['is_ok']:
            if raise_on_error:
                raise ValueError(response)

        # Return the business response
        out = SFTPOutput.from_dict(response)
        out.strip_stdout_prefix()

        return out

# ################################################################################################################################

    def execute(self, data, log_level=SFTP.LOG_LEVEL.LEVEL0.id, raise_on_error=True):
        # type: (str, int) -> SFTPOutput
        return self._execute(data, log_level, raise_on_error)

# ################################################################################################################################

    def _parse_permissions(self, permissions):
        # type: (str) -> int
        out = 0

        # Read
        if permissions[0] == 'r':
            out += 4

        # Write
        if permissions[1] == 'w':
            out += 2

        # Execute
        if permissions[2] == 'x':
            out += 1

        return out

# ################################################################################################################################

    def _build_last_modified(self, month, day, year_hour_info):
        # type: (str, str, str) -> datetime

        # If there is a colon, it means that it is an hour in the format of HH:mm,
        # otherwise it will be actually a year.
        has_year = ':' not in year_hour_info

        # We have a year already so we can immediately build the full date to be parsed
        if has_year:

            mod_date = '{}-{}-{}'.format(year_hour_info, month, day)
            mod_date = strptime(mod_date, '%Y-%b-%d')

            return date(mod_date.tm_year, mod_date.tm_mon, mod_date.tm_mday)

        # .. otherwise, we must find that year ourselves
        else:
            #
            # Given a particular month and day, we need to find in which year it was
            # in relation to current month.
            #
            # For instance (simplified, without taking days into account):
            #
            # If now is November 2183 and month is March    -> year was 2183
            # If now is February 2183 and month is December -> year was 2182
            #
            today = datetime.today()
            mod_date = strptime('{}-{}'.format(month, day), '%b-%d')

            hour, minute = year_hour_info.split(':')
            hour = int(hour)
            minute = int(minute)

            # If modification month is bigger than current one, it means that it must have been already
            # in the previous year. Otherwise, it was in the same year we have today.
            mod_year = today.year - 1 if mod_date.tm_mon > today.month else today.year

            return datetime(mod_year, mod_date.tm_mon, mod_date.tm_mday, hour, minute)

# ################################################################################################################################

    def _parse_ls_line(self, line):
        # type: (str) -> SFTPInfo

        # Output to return
        out = SFTPInfo()

        # Map prefix found to entry type
        prefix = line[0]         # type: str
        entry_type = EntryType.get_entry_type(prefix)

        permissions = line[1:10] # type: str

        user_permissions = self._parse_permissions(permissions[:3])   # type: int
        group_permissions = self._parse_permissions(permissions[3:6]) # type: int
        other_permissions = self._parse_permissions(permissions[6:])  # type: int

        permissions_oct = '{}{}{}'.format(user_permissions, group_permissions, other_permissions)
        permissions = int(permissions_oct, 8)

        # Move to other entries now
        line = line[10:].strip()

        # Ignore hardlinks / directory entries
        line = line.split(' ', 1)

        # line[0] are the very ignored hardlinks and directory entries
        line = line[1]

        # The next entry is owner
        line = line.split(' ', 1)
        owner = line[0]

        # The next entry is group name
        line = line[1].strip()
        line = line.split(' ', 1)
        group = line[0]

        # Next is the entry size
        line = line[1].strip()
        line = line.split(' ', 1)
        size = line[0]

        # Split by whitespace into individual elements
        line = line[1].strip()
        line = line.split(' ', 4)
        line = [elem for elem in line if elem.strip()]

        # Next two tokens are modification date, but only its month and day will be known here
        month = line[0]
        day = line[1]

        line = line[2:]

        # Next token is either year or hour:minute
        year_time_info = line[0]

        # We can now combine all date elements to build a full modification time
        last_modified = self._build_last_modified(month, day, year_time_info)

        # Anything left must be our entry name
        name = line[1].strip()

        # Populate everything before returning ..
        out.type = entry_type
        out.name = name
        out.permissions = permissions
        out.permissions_oct = permissions_oct
        out.owner = owner
        out.group = group
        out.size = size
        out.last_modified = last_modified

        # .. now we can return
        return out

# ################################################################################################################################

    def _parse_ls_output(self, ls_output):
        # type: (str) -> List[SFTPInfo]

        # Output to produce
        out = []

        #
        # Sample lines to parse - the output is standardized by The Open Group
        #
        # https://pubs.opengroup.org/onlinepubs/9699919799/utilities/ls.html
        #
        # -rw-------    1 user1    group1         336 Mar  3 11:50 filename.txt
        # drwx------    2 user1    group1        4096 Mar  3 10:02 directony_name
        # lrwxrwxrwx    1 user1    group1           5 Mar  3 13:36 symlink.txt
        # srwxrwxr-x    1 user1    group1           0 Mar  3 11:50 ipc_queue_name
        #
        #
        # Or, if timestamps include the year:
        #
        # -rw-rw-r--    1 user1    group1        1822 Oct 24  2017 publish1.py
        # drwxr-x---+
        #
        #
        # The format that we expect and parse is thus:
        #
        # 1) Item type              - one character
        # 2) Permissions            - nine characters (SFTP does not return getfacl flags)
        # 3) Hardlinks/dir entries  - we do not parse it
        # 4) User name              - N characters
        # 5) Group name             - N characters
        # 6) Size                   - N characters
        # 7) Modification date      - Assuming a file system maintains it
        # 8) Either time or year    - Ditto
        # 9) File name
        #

        for line in ls_output.splitlines():
            parsed = self._parse_ls_line(line)
            out.append(parsed)

        return out

# ################################################################################################################################

    def _get_info(self, remote_path, log_level=0, needs_dot_entries=True, raise_on_error=True):
        # type: (str, int, bool) -> SFTPInfo

        options = '-la' if needs_dot_entries else '-l'
        out = self.execute('ls {} {}'.format(options, remote_path), log_level, raise_on_error)

        if out.stdout:
            out = self._parse_ls_output(out.stdout) # type: List[SFTPInfo]
            return out

# ################################################################################################################################

    def get_info(self, remote_path, log_level=0, raise_on_error=True):
        out = self._get_info(remote_path, log_level, raise_on_error=raise_on_error)
        if out:
            # Replace resolved '.' directory names with what was given on input
            # because they must point to the same thing.
            out = out[0]
            if out.type == EntryType.directory and out.name == '.':
                out.name = remote_path

            return out

# ################################################################################################################################

    def exists(self, remote_path, log_level=0):
        # type: (str) -> bool

        # The is_ok flag will be True only if the remote path points to an existing file or directory
        return self.execute('ls {}'.format(remote_path), log_level, raise_on_error=False).is_ok

# ################################################################################################################################

    def is_file(self, remote_path, log_level=0):
        return self.get_info(remote_path, log_level).is_file

# ################################################################################################################################

    def is_directory(self, remote_path, log_level=0):
        return self.get_info(remote_path, log_level).is_directory

# ################################################################################################################################

    def is_symlink(self, remote_path, log_level=0):
        return self.get_info(remote_path, log_level).is_symlink

# ################################################################################################################################

    def delete(self, remote_path, log_level=0, _info=None):
        info = _info or self.get_info(remote_path, log_level)

        if info.is_directory:
            return self.delete_directory(remote_path, log_level, False)

        elif info.is_file:
            return self.delete_file(remote_path, log_level, False)

        elif info.is_symlink:
            return self.delete_symlink(remote_path, log_level, False)

        else:
            raise ValueError('Unexpected entry type (delete) `{}`'.format(info.to_dict()))

# ################################################################################################################################

    def delete_by_type(self, remote_path, type, log_level):
        delete_func_map = {
            EntryType.file: self.delete_file,
            EntryType.directory: self.delete_directory,
            EntryType.symlink: self.delete_symlink,
        }

        func = delete_func_map[type]
        return func(remote_path, log_level, False)

# ################################################################################################################################

    def _remove(self, is_dir, remote_path, log_level):
        command = 'rmdir' if is_dir else 'rm'
        return self.execute('{} {}'.format(command, remote_path), log_level)

# ################################################################################################################################

    def _ensure_entry_type(self, remote_path, expected, log_level):
        info = self.get_info(remote_path, log_level)
        if not info.type == expected:
            raise ValueError('Expected for `{}` to be `{}` instead of `{}` ({})'.format(
                remote_path, expected, info.type, info.to_dict()))

# ################################################################################################################################

    def delete_file(self, remote_path, log_level=0, needs_check=True):
        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.file, log_level)

        return self._remove(False, remote_path, log_level)

# ################################################################################################################################

    def delete_directory(self, remote_path, log_level=0, needs_check=True):
        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.directory, log_level)

        return self._remove(True, remote_path, log_level)

# ################################################################################################################################

    def delete_symlink(self, remote_path, log_level=0, needs_check=True):
        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.symlink, log_level)

        return self._remove(False, remote_path, log_level)

# ################################################################################################################################

    def chmod(self, mode, remote_path, log_level=0):
        return self.execute('chmod {} {}'.format(mode, remote_path), log_level)

# ################################################################################################################################

    def chown(self, owner, remote_path, log_level=0):
        return self.execute('chown {} {}'.format(owner, remote_path), log_level)

# ################################################################################################################################

    def chgrp(self, group, remote_path, log_level=0):
        return self.execute('chgrp {} {}'.format(group, remote_path), log_level)

# ################################################################################################################################

    def create_symlink(self, from_path, to_path, log_level=0):
        return self.execute('ln -s {} {}'.format(from_path, to_path), log_level)

# ################################################################################################################################

    def create_hardlink(self, from_path, to_path, log_level=0):
        return self.execute('ln {} {}'.format(from_path, to_path), log_level)

# ################################################################################################################################

    def create_directory(self, remote_path, log_level=0):
        return self.execute('mkdir {}'.format(remote_path), log_level)

# ################################################################################################################################

    def list(self, remote_path, log_level=0):
        return self._get_info(remote_path, log_level, needs_dot_entries=False)

# ################################################################################################################################

    def move(self, from_path, to_path, log_level=0):
        return self.execute('rename {} {}'.format(from_path, to_path), log_level)

    rename = move

# ################################################################################################################################

    def download(self, remote_path, local_path, recursive=True, require_file=False, log_level=0):

        # Make sure this is indeed a file
        if require_file:
            self._ensure_entry_type(remote_path, EntryType.file, log_level)

        options = ' -r' if recursive else ''
        return self.execute('get{} {} {}'.format(options, remote_path, local_path), log_level)

# ################################################################################################################################

    def download_file(self, remote_path, local_path, log_level=0):
        return self.download(remote_path, local_path, require_file=True, log_level=log_level)

# ################################################################################################################################

    def read(self, remote_path, mode='r+b', log_level=0):

        # Download the file to a temporary location ..
        with NamedTemporaryFile(mode, suffix='zato-sftp-read.txt') as local_path:
            self.download_file(remote_path, local_path.name)

            # .. and read it in using a separate thread so as not to block the event loop.
            thread_file = FileObjectThread(local_path)
            data = thread_file.read()
            thread_file.close()

            return data

# ################################################################################################################################

    def _overwrite_if_needed(self, remote_path, overwrite, log_level):
        info = self.get_info(remote_path, log_level, raise_on_error=False)

        # The remote location exists so we either need to delete it (overwrite=True) or raise an error (overwrite=False)
        if info:
            if overwrite:
                self.delete_by_type(remote_path, info.type, log_level)
            else:
                raise ValueError('Cannot upload, location `{}` already exists ({})'.format(remote_path, info.to_dict()))

# ################################################################################################################################

    def upload(self, local_path, remote_path, recursive=True, overwrite=False, log_level=0, _needs_overwrite_check=True):

        # Will raise an exception or delete the remote location, depending on what is needed
        if _needs_overwrite_check:
            self._overwrite_if_needed(remote_path, overwrite, log_level)

        options = ' -r' if recursive else ''

        return self.execute('put{} {} {}'.format(options, local_path, remote_path), log_level)

# ################################################################################################################################

    def write(self, data, remote_path, mode='w+b', overwrite=False, log_level=0, encoding='utf8'):

        # Will raise an exception or delete the remote location, depending on what is needed
        self._overwrite_if_needed(remote_path, overwrite, log_level)

        # Data to be written must be always bytes
        data = data if isinstance(data, bytes) else data.encode(encoding)

        # A temporary file to write data to ..
        with NamedTemporaryFile(mode, suffix='zato-sftp-write.txt') as local_path:

            # .. wrap the file in separate thread so as not to block the event loop.
            thread_file = FileObjectThread(local_path, mode=mode)
            thread_file.write(data)
            thread_file.flush()

            try:
                # Data written out, we can now upload it to the remote location
                self.upload(local_path.name, remote_path, False, overwrite, log_level, False)

            except Exception:
                logger.warning('Exception in SFTP write method `%s`', format_exc())

            finally:
                # Now we can close the file too
                thread_file.close()

# ################################################################################################################################
# ################################################################################################################################
