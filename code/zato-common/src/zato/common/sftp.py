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

# The exit code of the sftp binary when a batch command failed, and the exit code before the binary was run.
_exit_code_command_failed = 1
_exit_code_not_run = -1

# ################################################################################################################################
# ################################################################################################################################

class SFTPOutput:
    """ Represents output resulting from execution of SFTP command(s).
    """
    __slots__ = 'is_ok', 'cid', 'command', 'command_no', 'stdout', 'stderr', 'details', 'response_time', 'exit_code'

    def __init__(
        self,
        cid:'str',
        command_no:'int',
        command:'any_'=None,
        is_ok:'boolnone'=None,
        stdout:'strnone'=None,
        stderr:'strnone'=None,
        details:'strnone'=None,
        response_time:'strnone'=None,
        exit_code:'int' = _exit_code_not_run,
        ) -> 'None':

        self.cid = cid
        self.command_no = command_no
        self.command = command
        self.is_ok = is_ok
        self.stdout = stdout
        self.stderr = stderr
        self.details = details
        self.response_time = response_time
        self.exit_code = exit_code

# ################################################################################################################################

    def is_connection_failure(self) -> 'bool':
        """ Whether the session itself failed rather than one of the commands fed to it.
        """
        if self.is_ok:
            out = False
        else:
            out = self.exit_code != _exit_code_command_failed

        return out

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
            'exit_code': self.exit_code,
        }

        return out

# ################################################################################################################################

    @staticmethod
    def from_dict(data:'stranydict') -> 'SFTPOutput':

        out = SFTPOutput(**data)

        return out

# ################################################################################################################################
# ################################################################################################################################
