# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################
# ################################################################################################################################

class SFTPOutput(object):
    """ Represents output resulting from execution of SFTP command(s).
    """
    __slots__ = 'is_ok', 'cid', 'command', 'command_no', 'stdout', 'stderr', 'details', 'response_time'

    def __init__(self, cid, command_no, command=None, is_ok=None, stdout=None, stderr=None, details=None, response_time=None):
        # type: (str, int, str, bool, str, str, str) -> None

        self.cid = cid
        self.command_no = command_no
        self.command = command
        self.is_ok = is_ok
        self.stdout = stdout
        self.stderr = stderr
        self.details = details
        self.response_time = response_time

# ################################################################################################################################

    def __str__(self):
        return '<{} at {}, cid:{}, command_no:{}, is_ok:{}, rt:{}>'.format(self.__class__.__name__, hex(id(self)), self.cid,
            self.command_no, self.is_ok, self.response_time)

# ################################################################################################################################

    def strip_stdout_prefix(self):
        if self.stdout:
            out = []
            for line in self.stdout.splitlines():
                if not line.startswith('sftp>'):
                    out.append(line)
            self.stdout = '\n'.join(out)

# ################################################################################################################################

    def to_dict(self):
        # type: () -> dict
        return {
            'is_ok': self.is_ok,
            'cid': self.cid,
            'command': self.command,
            'command_no': self.command_no,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'details': self.details,
            'response_time': self.response_time,
        }

# ################################################################################################################################

    @staticmethod
    def from_dict(data):
        # type: (dict) -> SFTPOutput
        return SFTPOutput(**data)

# ################################################################################################################################
# ################################################################################################################################
