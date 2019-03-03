# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import date, datetime
from json import loads
from logging import getLogger
from time import strptime

# humaniz
from humanize import naturalsize

# Zato
from zato.common import SFTP
from zato.common.broker_message import OUTGOING
from zato.common.sftp import SFTPOutput
from zato.server.service import Service

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:
    from typing import List
    from zato.server.base.parallel import ParallelServer

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

class SFTPInfo(object):
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

class SFTPIPCFacade(object):
    """ Provides servers and services with access to SFTP resources.
    """
    def __init__(self, cid, server, config):
        # type: (str, ParallelServer, dict) -> None
        self.cid = cid
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

            # If modification month is bigger than current one, it means that it must have been already
            # in the previous year. Otherwise, it was in the same year we have today.
            mod_year = today.year - 1 if mod_date.tm_mon > today.month else today.year

            return date(mod_year, mod_date.tm_mon, mod_date.tm_mday)

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

        # Next two tokens are modification date, but only its month and day will be known here
        line = line[1].strip()
        line = line.split(' ', 3)
        line = [elem for elem in line if elem.strip()]

        month = line[0]
        day = line[1]

        line = line[2:]
        line = line[0]

        # Next token is either year or hour:minute
        line = line.split(' ', 1)
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

    def get_info(self, remote_path, log_level=SFTP.LOG_LEVEL.LEVEL0.id):
        # type: (str) -> SFTPInfo

        out = self.execute('ls -la {}'.format(remote_path), log_level=log_level)

        if out.stdout:
            out = self._parse_ls_output(out.stdout)
            return out[0]

# ################################################################################################################################

    def exists(self, remote_path):
        # type: (str) -> bool

        # The is_ok flag will be True only if the remote path points to an existing file or directory
        return self.execute('ls {}'.format(remote_path), raise_on_error=False).is_ok

# ################################################################################################################################

    def is_file(self, remote_path):
        pass

# ################################################################################################################################

    def is_symlink(self, remote_path):
        pass

# ################################################################################################################################

    def is_directory(self, path):
        pass

# ################################################################################################################################

    def delete(self, remote_path):
        pass

# ################################################################################################################################

    def delete_file(self, remote_path):
        pass

# ################################################################################################################################

    def delete_directory(self, remote_path):
        pass

# ################################################################################################################################

    def read(self, remote_path):
        pass

# ################################################################################################################################

    def list(self, remote_path):
        pass

# ################################################################################################################################

    def chmod(self, remote_path):
        pass

# ################################################################################################################################

    def chown(self, remote_path):
        pass

# ################################################################################################################################

    def chgrp(self, remote_path):
        pass

# ################################################################################################################################

    def create_file(self):
        pass

# ################################################################################################################################

    def create_directory(self):
        pass

# ################################################################################################################################

    def create_symlink(self):
        pass

# ################################################################################################################################

    def move(self, source_path, target_path):
        pass

# ################################################################################################################################

    def read(self, remote_path):
        pass

# ################################################################################################################################

    def write(self, data, remote_path, overwrite=False):
        pass

# ################################################################################################################################

    def download(self, remote_path, local_path):
        pass

# ################################################################################################################################

    def upload(self, local_path, remote_path, overwrite=False):
        pass

# ################################################################################################################################
# ################################################################################################################################
