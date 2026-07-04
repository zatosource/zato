# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, boolnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

class SFTPOutput:
    """ Represents output resulting from execution of SFTP command(s).
    """
    __slots__ = 'is_ok', 'cid', 'command', 'command_no', 'stdout', 'stderr', 'details', 'response_time'

    def __init__(
        self,
        cid:'str',
        command_no:'int',
        command:'any_'=None,
        is_ok:'boolnone'=None,
        stdout:'strnone'=None,
        stderr:'strnone'=None,
        details:'strnone'=None,
        response_time:'strnone'=None
        ) -> 'None':

        self.cid = cid
        self.command_no = command_no
        self.command = command
        self.is_ok = is_ok
        self.stdout = stdout
        self.stderr = stderr
        self.details = details
        self.response_time = response_time

# ################################################################################################################################

    def __str__(self) -> 'str':
        return '<{} at {}, cid:{}, command_no:{}, is_ok:{}, rt:{}>'.format(self.__class__.__name__, hex(id(self)), self.cid,
            self.command_no, self.is_ok, self.response_time)

# ################################################################################################################################

    def strip_stdout_prefix(self) -> 'None':

        # Remove the sftp> prompt lines that the binary echoes back for each batch command
        if self.stdout:
            out = []

            for line in self.stdout.splitlines():
                if not line.startswith('sftp>'):
                    out.append(line)

            self.stdout = '\n'.join(out)

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':

        out = {
            'is_ok': self.is_ok,
            'cid': self.cid,
            'command': self.command,
            'command_no': self.command_no,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'details': self.details,
            'response_time': self.response_time,
        }

        return out

# ################################################################################################################################

    @staticmethod
    def from_dict(data:'stranydict') -> 'SFTPOutput':

        out = SFTPOutput(**data)

        return out

# ################################################################################################################################
# ################################################################################################################################
