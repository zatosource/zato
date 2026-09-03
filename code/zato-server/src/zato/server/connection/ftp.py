# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from logging import getLogger
from shlex import split as shlex_split
from time import monotonic
from traceback import format_exc

# Zato
from zato.server.connection.file_transfer_base import EntryType, FileInfo, FileTransferConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strlist
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The MLST and MLSD modification time formats - the basic one and the one with a fraction of a second
_modify_format          = '%Y%m%d%H%M%S'
_modify_format_fraction = '%Y%m%d%H%M%S.%f'

# What the shell shows for a boolean answer
_shell_true = 'True'
_shell_false = 'False'

# ################################################################################################################################
# ################################################################################################################################

def parse_modify_fact(value:'str') -> 'datetime':
    """ Turns an MLST or MLSD modification time fact, e.g. 20260820103000, into a UTC-aware datetime object.
    """
    if '.' in value:
        out = datetime.strptime(value, _modify_format_fraction)
    else:
        out = datetime.strptime(value, _modify_format)

    out = out.replace(tzinfo=timezone.utc)
    return out

# ################################################################################################################################
# ################################################################################################################################

class FTPShellOutput:
    """ Represents output resulting from execution of FTP shell command(s).
    """
    __slots__ = 'is_ok', 'cid', 'command_no', 'stdout', 'stderr', 'response_time'

    def __init__(self, cid:'str') -> 'None':
        self.cid           = cid
        self.is_ok         = False # type: bool
        self.command_no    = 0     # type: int
        self.stdout        = ''    # type: str
        self.stderr        = ''    # type: str
        self.response_time = ''    # type: str

# ################################################################################################################################
# ################################################################################################################################

class FTPConnection(FileTransferConnection):
    """ The public API of a single outgoing FTP connection, obtained via self.ftp['My Connection'] in services.

    Remote paths are relative to the account's root directory and use forward slashes, e.g. documents/invoice.pdf.
    """

    # What each shell command may be and the name of the method that handles it
    _shell_handlers = {
        'ls': '_shell_ls',
        'stat': '_shell_stat',
        'exists': '_shell_exists',
        'mkdir': '_shell_mkdir',
        'rmdir': '_shell_rmdir',
        'rm': '_shell_rm',
        'delete': '_shell_rm',
        'mv': '_shell_mv',
        'rename': '_shell_mv',
        'cat': '_shell_cat',
        'ping': '_shell_ping',
    }

# ################################################################################################################################

    def _entry_type_from_fact(self, type_fact:'str') -> 'str':

        # Map the MLST or MLSD type fact to one of our entry types.
        if type_fact == 'dir':
            out = EntryType.directory
        elif 'link' in type_fact:
            out = EntryType.symlink
        else:
            out = EntryType.file

        return out

# ################################################################################################################################

    def _build_info_from_facts(self, name:'str', facts:'stranydict') -> 'FileInfo':

        # Our response to produce
        out = FileInfo()

        # Directories may report no size fact at all.
        if size := facts.get('size'):
            size = int(size)
        else:
            size = 0

        out.type = self._entry_type_from_fact(facts['type'])
        out.name = name
        out.size = size
        out.last_modified = parse_modify_fact(facts['modify'])

        return out

# ################################################################################################################################

    def _build_info(self, name:'str', stat_result:'any_') -> 'FileInfo':

        out = self._build_info_from_facts(name, stat_result)
        return out

# ################################################################################################################################

    def _build_info_from_dir_entry(self, entry:'any_') -> 'FileInfo':

        # Each listing entry is a (name, facts) tuple
        name, facts = entry

        out = self._build_info_from_facts(name, facts)
        return out

# ################################################################################################################################

    def _shell_ls(self, args:'strlist') -> 'str':

        # Without a path, the account's root directory is listed.
        if args:
            directory = args[0]
        else:
            directory = '.'

        entries = self.list(directory)

        # One line per entry - its type, size, modification time and name
        lines:'strlist' = []

        for info in entries:
            if info.is_directory:
                type_indicator = 'd'
            else:
                type_indicator = '-'
            line = '{} {:>12} {} {}'.format(type_indicator, info.size, info.last_modified_iso, info.name)
            lines.append(line)

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    def _shell_stat(self, args:'strlist') -> 'str':

        info = self.get_info(args[0])
        details = info.to_dict()

        # One line per detail, in a stable order
        lines:'strlist' = []

        for key in sorted(details):
            lines.append(f'{key}: {details[key]}')

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    def _shell_exists(self, args:'strlist') -> 'str':

        if self.exists(args[0]):
            out = _shell_true
        else:
            out = _shell_false

        return out

# ################################################################################################################################

    def _shell_mkdir(self, args:'strlist') -> 'str':

        self.create_directory(args[0], exist_ok=True)

        out = ''
        return out

# ################################################################################################################################

    def _shell_rmdir(self, args:'strlist') -> 'str':

        self.delete_directory(args[0])

        out = ''
        return out

# ################################################################################################################################

    def _shell_rm(self, args:'strlist') -> 'str':

        self.delete_file(args[0])

        out = ''
        return out

# ################################################################################################################################

    def _shell_mv(self, args:'strlist') -> 'str':

        self.move(args[0], args[1])

        out = ''
        return out

# ################################################################################################################################

    def _shell_cat(self, args:'strlist') -> 'str':

        data = self.read(args[0])

        # The file's bytes are shown as text - it is external data, so bytes
        # that do not form valid text are replaced rather than being an error.
        out = data.decode('utf8', 'replace')
        return out

# ################################################################################################################################

    def _shell_ping(self, _args:'strlist') -> 'str':

        self.ping()

        out = ''
        return out

# ################################################################################################################################

    def execute(self, data:'str', raise_on_error:'bool' = True) -> 'FTPShellOutput':
        """ Executes one or more FTP shell commands, one per line, stopping at the first one that fails.
        """

        # Our response to produce
        out = FTPShellOutput(self.cid)

        stdout_lines:'strlist' = []
        start = monotonic()

        # Until something fails, the commands ran fine.
        is_ok = True

        for line in data.splitlines():

            line = line.strip()

            # Empty lines are skipped rather than counted.
            if not line:
                continue

            out.command_no += 1

            # Split the line into the command and its arguments, honoring quoted names with spaces.
            parts = shlex_split(line)
            first_part = parts[0]
            command = first_part.lower()
            args = parts[1:]

            # An unrecognized command ends the run ..
            if handler_name := self._shell_handlers.get(command):
                handler = getattr(self, handler_name)
            else:
                sorted_commands = sorted(self._shell_handlers)
                known_commands = ', '.join(sorted_commands)
                out.stderr = f'Unknown command `{command}` - use one of: {known_commands}'
                is_ok = False
                break

            # .. and so does one that fails - the traceback goes to the log
            # .. while the caller only ever sees the error message itself.
            try:
                result = handler(args)
            except Exception as e:
                logger.warning('FTP shell command error, cid:`%s`, `%s`', self.cid, format_exc())
                out.stderr = str(e)
                is_ok = False
                break
            else:
                if result:
                    stdout_lines.append(result)

        elapsed = monotonic() - start

        out.is_ok = is_ok
        out.stdout = '\n'.join(stdout_lines)
        out.response_time = '{:.3f}s'.format(elapsed)

        # Perhaps we are to raise an exception on an error encountered.
        if not is_ok:
            if raise_on_error:
                raise Exception(out.stderr)

        return out

# ################################################################################################################################
# ################################################################################################################################
