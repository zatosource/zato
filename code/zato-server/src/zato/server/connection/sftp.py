# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.sftp import SFTPOutput
    from zato.common.typing_ import any_, stranydict
    from zato.server.generic.api.outconn_sftp import OutconnSFTPWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EntryType:
    file = 'file'
    directory = 'directory'
    symlink = 'symlink'
    other = 'other'

# ################################################################################################################################

# Maps prefixes of ls output lines to entry types
_entry_type_map = {
    '-': EntryType.file,
    'd': EntryType.directory,
    'l': EntryType.symlink,
}

# ################################################################################################################################

def get_entry_type(prefix:'str') -> 'str':

    out = _entry_type_map.get(prefix)
    if not out:
        out = EntryType.other

    return out

# ################################################################################################################################

_other_types_check = EntryType.file, EntryType.directory, EntryType.symlink

# ################################################################################################################################

sftp_info_list = list['SFTPInfo']

# ################################################################################################################################
# ################################################################################################################################

class SFTPInfo:
    __slots__ = 'type', 'name', 'owner', 'group', 'size', 'permissions', 'permissions_oct', 'last_modified'

    def __init__(self) -> 'None':
        self.type = '' # type: str
        self.name = '' # type: str

        self.size = 0 # type: int

        self.owner = '' # type: str
        self.group = '' # type: str

        self.permissions = 0      # type: int
        self.permissions_oct = '' # type: str

        self.last_modified = None # type: any_

# ################################################################################################################################

    def to_dict(self, skip_last_modified:'bool'=True) -> 'stranydict':

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
    def is_file(self) -> 'bool':
        return self.type.startswith(EntryType.file)

# ################################################################################################################################

    @property
    def is_directory(self) -> 'bool':
        return self.type.startswith(EntryType.directory)

# ################################################################################################################################

    @property
    def is_symlink(self) -> 'bool':
        return self.type.startswith(EntryType.symlink)

# ################################################################################################################################

    @property
    def is_other(self) -> 'bool':
        return not self.type.startswith(_other_types_check)

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

class SFTPConnection:
    """ The public API of a single outgoing SFTP connection, obtained via self.sftp['My Connection'] in services.
    """
    def __init__(self, cid:'str', wrapper:'OutconnSFTPWrapper') -> 'None':
        self.cid = cid
        self.wrapper = wrapper

# ################################################################################################################################

    def ping(self) -> 'None':
        self.wrapper.ping()

# ################################################################################################################################

    def _execute(self, data:'str', log_level:'int', raise_on_error:'bool'=True) -> 'SFTPOutput':

        if log_level > 0:
            logger.info('Executing cid:`%s` `%s`', self.cid, data)

        # Run the command(s) using a client from the wrapper's queue ..
        with self.wrapper.client() as client:
            out = client.execute(self.cid, data, log_level) # type: SFTPOutput

        if log_level > 0:
            logger.info('Response received, cid:`%s`, data:`%s`', self.cid, out.to_dict())

        # .. perhaps we are to raise an exception on an error encountered ..
        if not out.is_ok:
            if raise_on_error:
                raise Exception(out.to_dict())

        # .. remove the echoed sftp> prompt lines from the output ..
        out.strip_stdout_prefix()

        # .. and return the business response.
        return out

# ################################################################################################################################

    def execute(self, data:'str', log_level:'int'=0, raise_on_error:'bool'=True) -> 'SFTPOutput':

        out = self._execute(data, log_level, raise_on_error)

        return out

# ################################################################################################################################

    def _parse_permissions(self, permissions:'str') -> 'int':

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

    def _build_last_modified(self, month:'str', day:'str', year_hour_info:'str') -> 'any_':

        # If there is a colon, it means that it is an hour in the format of HH:mm,
        # otherwise it will be actually a year.
        has_year = ':' not in year_hour_info

        # We have a year already so we can immediately build the full date to be parsed
        if has_year:

            mod_date = '{}-{}-{}'.format(year_hour_info, month, day)
            mod_date = strptime(mod_date, '%Y-%b-%d')

            out = date(mod_date.tm_year, mod_date.tm_mon, mod_date.tm_mday)
            return out

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
            if mod_date.tm_mon > today.month:
                mod_year = today.year - 1
            else:
                mod_year = today.year

            out = datetime(mod_year, mod_date.tm_mon, mod_date.tm_mday, hour, minute)
            return out

# ################################################################################################################################

    def _parse_ls_line(self, line:'str') -> 'SFTPInfo':

        # Our response to produce
        out = SFTPInfo()

        # Map the prefix found to an entry type
        prefix = line[0] # type: str
        entry_type = get_entry_type(prefix)

        permissions = line[1:10] # type: str

        user_permissions = self._parse_permissions(permissions[:3])   # type: int
        group_permissions = self._parse_permissions(permissions[3:6]) # type: int
        other_permissions = self._parse_permissions(permissions[6:])  # type: int

        permissions_oct = '{}{}{}'.format(user_permissions, group_permissions, other_permissions)
        permissions = int(permissions_oct, 8)

        # Move to other entries now
        line = line[10:].strip()

        # Ignore hardlinks / directory entries
        line_parts = line.split(' ', 1)

        # The first part are the very ignored hardlinks and directory entries
        line = line_parts[1]

        # The next entry is owner
        line_parts = line.split(' ', 1)
        owner = line_parts[0]

        # The next entry is group name
        line = line_parts[1].strip()
        line_parts = line.split(' ', 1)
        group = line_parts[0]

        # Next is the entry size
        line = line_parts[1].strip()
        line_parts = line.split(' ', 1)
        size = line_parts[0]

        # Split by whitespace into individual elements
        line = line_parts[1].strip()
        line_parts = line.split(' ', 4)

        elems = []
        for elem in line_parts:
            if elem.strip():
                elems.append(elem)

        # Next two tokens are modification date, but only its month and day will be known here
        month = elems[0]
        day = elems[1]

        elems = elems[2:]

        # Next token is either year or hour:minute
        year_time_info = elems[0]

        # We can now combine all date elements to build a full modification time
        last_modified = self._build_last_modified(month, day, year_time_info)

        # Anything left must be our entry name
        name = elems[1].strip()

        # Populate everything before returning ..
        out.type = entry_type
        out.name = name
        out.permissions = permissions
        out.permissions_oct = permissions_oct
        out.owner = owner
        out.group = group
        out.size = int(size)
        out.last_modified = last_modified

        # .. now we can return
        return out

# ################################################################################################################################

    def _parse_ls_output(self, ls_output:'str') -> 'sftp_info_list':

        # Our response to produce
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

    def _get_info(
        self,
        remote_path:'str',
        log_level:'int'=0,
        needs_dot_entries:'bool'=True,
        raise_on_error:'bool'=True
        ) -> 'sftp_info_list | None':

        if needs_dot_entries:
            options = '-la'
        else:
            options = '-l'

        result = self.execute('ls {} {}'.format(options, remote_path), log_level, raise_on_error)

        if result.stdout:
            out = self._parse_ls_output(result.stdout)
            return out

# ################################################################################################################################

    def get_info(self, remote_path:'str', log_level:'int'=0, raise_on_error:'bool'=True) -> 'SFTPInfo | None':

        result = self._get_info(remote_path, log_level, raise_on_error=raise_on_error)

        if result:

            # Replace resolved '.' directory names with what was given on input
            # because they must point to the same thing.
            out = result[0]
            if out.type == EntryType.directory:
                if out.name == '.':
                    out.name = remote_path

            return out

# ################################################################################################################################

    def exists(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        # The is_ok flag will be True only if the remote path points to an existing file or directory
        result = self.execute('ls {}'.format(remote_path), log_level, raise_on_error=False)

        out = result.is_ok
        return out

# ################################################################################################################################

    def is_file(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        info = self.get_info(remote_path, log_level)

        out = info.is_file
        return out

# ################################################################################################################################

    def is_directory(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        info = self.get_info(remote_path, log_level)

        out = info.is_directory
        return out

# ################################################################################################################################

    def is_symlink(self, remote_path:'str', log_level:'int'=0) -> 'bool':

        info = self.get_info(remote_path, log_level)

        out = info.is_symlink
        return out

# ################################################################################################################################

    def delete(self, remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        info = self.get_info(remote_path, log_level)

        if info.is_directory:
            out = self.delete_directory(remote_path, log_level, False)

        elif info.is_file:
            out = self.delete_file(remote_path, log_level, False)

        elif info.is_symlink:
            out = self.delete_symlink(remote_path, log_level, False)

        # .. anything else is not an entry type that we can delete.
        else:
            raise Exception('Unexpected entry type (delete) `{}`'.format(info.to_dict()))

        return out

# ################################################################################################################################

    def delete_by_type(self, remote_path:'str', type:'str', log_level:'int'=0) -> 'SFTPOutput':

        delete_func_map = {
            EntryType.file: self.delete_file,
            EntryType.directory: self.delete_directory,
            EntryType.symlink: self.delete_symlink,
        }

        func = delete_func_map[type]

        out = func(remote_path, log_level, False)
        return out

# ################################################################################################################################

    def _remove(self, is_dir:'bool', remote_path:'str', log_level:'int') -> 'SFTPOutput':

        if is_dir:
            command = 'rmdir'
        else:
            command = 'rm'

        out = self.execute('{} {}'.format(command, remote_path), log_level)
        return out

# ################################################################################################################################

    def _ensure_entry_type(self, remote_path:'str', expected:'str', log_level:'int') -> 'None':

        info = self.get_info(remote_path, log_level)

        if not info.type == expected:
            raise Exception('Expected for `{}` to be `{}` instead of `{}` ({})'.format(
                remote_path, expected, info.type, info.to_dict()))

# ################################################################################################################################

    def delete_file(self, remote_path:'str', log_level:'int'=0, needs_check:'bool'=True) -> 'SFTPOutput':

        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.file, log_level)

        out = self._remove(False, remote_path, log_level)
        return out

# ################################################################################################################################

    def delete_directory(self, remote_path:'str', log_level:'int'=0, needs_check:'bool'=True) -> 'SFTPOutput':

        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.directory, log_level)

        out = self._remove(True, remote_path, log_level)
        return out

# ################################################################################################################################

    def delete_symlink(self, remote_path:'str', log_level:'int'=0, needs_check:'bool'=True) -> 'SFTPOutput':

        if needs_check:
            self._ensure_entry_type(remote_path, EntryType.symlink, log_level)

        out = self._remove(False, remote_path, log_level)
        return out

# ################################################################################################################################

    def chmod(self, mode:'str', remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('chmod {} {}'.format(mode, remote_path), log_level)
        return out

# ################################################################################################################################

    def chown(self, owner:'str', remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('chown {} {}'.format(owner, remote_path), log_level)
        return out

# ################################################################################################################################

    def chgrp(self, group:'str', remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('chgrp {} {}'.format(group, remote_path), log_level)
        return out

# ################################################################################################################################

    def create_symlink(self, from_path:'str', to_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('ln -s {} {}'.format(from_path, to_path), log_level)
        return out

# ################################################################################################################################

    def create_hardlink(self, from_path:'str', to_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('ln {} {}'.format(from_path, to_path), log_level)
        return out

# ################################################################################################################################

    def create_directory(self, remote_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('mkdir {}'.format(remote_path), log_level)
        return out

# ################################################################################################################################

    def list(self, remote_path:'str', log_level:'int'=0) -> 'sftp_info_list | None':

        out = self._get_info(remote_path, log_level, needs_dot_entries=False)
        return out

# ################################################################################################################################

    def move(self, from_path:'str', to_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.execute('rename {} {}'.format(from_path, to_path), log_level)
        return out

    rename = move

# ################################################################################################################################

    def download(
        self,
        remote_path:'str',
        local_path:'str',
        recursive:'bool'=True,
        require_file:'bool'=False,
        log_level:'int'=0
        ) -> 'SFTPOutput':

        # Make sure this is indeed a file
        if require_file:
            self._ensure_entry_type(remote_path, EntryType.file, log_level)

        if recursive:
            options = ' -r'
        else:
            options = ''

        out = self.execute('get{} {} {}'.format(options, remote_path, local_path), log_level)
        return out

# ################################################################################################################################

    def download_file(self, remote_path:'str', local_path:'str', log_level:'int'=0) -> 'SFTPOutput':

        out = self.download(remote_path, local_path, require_file=True, log_level=log_level)
        return out

# ################################################################################################################################

    def read(self, remote_path:'str', mode:'str'='r+b', log_level:'int'=0) -> 'any_':

        # Download the file to a temporary location ..
        with NamedTemporaryFile(mode, suffix='zato-sftp-read.txt') as local_path:
            _ = self.download_file(remote_path, local_path.name, log_level)

            # .. and read it in using a separate thread so as not to block the event loop.
            thread_file = FileObjectThread(local_path)
            data = thread_file.read()
            thread_file.close()

            return data

# ################################################################################################################################

    def _overwrite_if_needed(self, remote_path:'str', overwrite:'bool', log_level:'int') -> 'None':

        info = self.get_info(remote_path, log_level, raise_on_error=False)

        # The remote location exists so we either need to delete it (overwrite=True) or raise an error (overwrite=False)
        if info:
            if overwrite:
                _ = self.delete_by_type(remote_path, info.type, log_level)
            else:
                raise Exception('Cannot upload, location `{}` already exists ({})'.format(remote_path, info.to_dict()))

# ################################################################################################################################

    def upload(
        self,
        local_path:'str',
        remote_path:'str',
        recursive:'bool'=True,
        overwrite:'bool'=False,
        log_level:'int'=0,
        _needs_overwrite_check:'bool'=True
        ) -> 'SFTPOutput':

        # Will raise an exception or delete the remote location, depending on what is needed
        if _needs_overwrite_check:
            self._overwrite_if_needed(remote_path, overwrite, log_level)

        if recursive:
            options = ' -r'
        else:
            options = ''

        out = self.execute('put{} {} {}'.format(options, local_path, remote_path), log_level)
        return out

# ################################################################################################################################

    def write(
        self,
        data:'any_',
        remote_path:'str',
        mode:'str'='w+b',
        overwrite:'bool'=False,
        log_level:'int'=0,
        encoding:'str'='utf8'
        ) -> 'None':

        # Will raise an exception or delete the remote location, depending on what is needed
        self._overwrite_if_needed(remote_path, overwrite, log_level)

        # Data to be written out must be always bytes
        if not isinstance(data, bytes):
            data = data.encode(encoding)

        # A temporary file to write data to ..
        with NamedTemporaryFile(mode, suffix='zato-sftp-write.txt') as local_path:

            # .. wrap the file in separate thread so as not to block the event loop.
            thread_file = FileObjectThread(local_path, mode=mode)
            thread_file.write(data)
            thread_file.flush()

            try:
                # Data written out, we can now upload it to the remote location
                _ = self.upload(local_path.name, remote_path, False, overwrite, log_level, False)

            except Exception:
                logger.warning('Exception in SFTP write method `%s`', format_exc())

            finally:
                # Now we can close the file too
                thread_file.close()

# ################################################################################################################################
# ################################################################################################################################
