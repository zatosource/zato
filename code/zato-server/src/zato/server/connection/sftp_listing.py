# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from datetime import date, datetime, timezone
from time import strptime

# humanize
from humanize import naturalsize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.sftp import SFTPOutput
    from zato.common.typing_ import any_, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

sftp_info_list = list['SFTPInfo']

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

_other_types_check = EntryType.file, EntryType.directory, EntryType.symlink

# One line of `ls -ln`, which the sftp binary formats itself from the attributes of an entry:
#
# -rw-r--r--    ? 1000     1000          336 Mar  3 11:50 /incoming/invoice.csv
# -rwsr-xr-x    ? 1000     1000         1822 Oct 24  2017 /incoming/  report.csv
#
# The name follows the time or the year after exactly one space, so a name may begin with spaces of its own.
_ls_line_attributes = r'^(?P<prefix>.)(?P<permissions>.{9})\s+\S+\s+(?P<owner>\S+)\s+(?P<group>\S+)\s+(?P<size>\d+)\s+'
_ls_line_date_name = r'(?P<month>[A-Za-z]{3})\s+(?P<day>\d{1,2})\s+(?P<year_time_info>\d{1,2}:\d{2}|\d{4}) (?P<name>.+)$'
_ls_line_pattern = re.compile(_ls_line_attributes + _ls_line_date_name)

# The value of the execute position of a permission triad and whether a special bit is set there -
# a lowercase letter means the special bit is set together with execute, an uppercase one without it.
_execute_position = {
    '-': (0, False),
    'x': (1, False),
    's': (1, True),
    'S': (0, True),
    't': (1, True),
    'T': (0, True),
}

# The special bit of each triad in turn - setuid, setgid and sticky
_special_bits = (4, 2, 1)

# Where each of the three triads of a permission string starts
_triad_starts = (0, 3, 6)

# How many characters one triad has
_triad_length = 3

# ################################################################################################################################
# ################################################################################################################################

def get_entry_type(prefix:'str') -> 'str':

    out = _entry_type_map.get(prefix)
    if not out:
        out = EntryType.other

    return out

# ################################################################################################################################

def _parse_triad(triad:'str') -> 'tuple[int, bool]':
    """ Returns the octal digit of one permission triad and whether its special bit is set.
    """
    out = 0

    # Read
    if triad[0] == 'r':
        out += 4

    # Write
    if triad[1] == 'w':
        out += 2

    # Execute, possibly together with a special bit
    execute, is_special = _execute_position[triad[2]]
    out += execute

    return out, is_special

# ################################################################################################################################

def parse_permissions(permissions:'str') -> 'tuple[int, str]':
    """ Turns a permission string, e.g. rwsr-xr-x, into its numeric mode and its octal form, e.g. 4755.
    The octal form has a leading digit only when a special bit is set, the same as `stat -c %a` prints it.
    """
    digits:'strlist' = []
    special = 0

    # Each triad gives one digit and possibly one special bit ..
    for index, start in enumerate(_triad_starts):
        end = start + _triad_length
        triad = permissions[start:end]

        value, is_special = _parse_triad(triad)
        digits.append(str(value))

        if is_special:
            special += _special_bits[index]

    permissions_oct = ''.join(digits)

    # .. and the special bits, if there are any, make up a digit of their own in front.
    if special:
        permissions_oct = f'{special}{permissions_oct}'

    mode = int(permissions_oct, 8)

    return mode, permissions_oct

# ################################################################################################################################

def build_last_modified(month:'str', day:'str', year_time_info:'str') -> 'date | datetime':
    """ Turns the date of a listing line into a date, when the line has a year,
    or into a UTC datetime, when the line has a time of day.
    """
    month_time = strptime(month, '%b')
    month_number = month_time.tm_mon
    day_number = int(day)

    # If there is a colon, it means that it is an hour in the format of HH:mm,
    # otherwise it will be actually a year.
    has_year = ':' not in year_time_info

    # We have a year already so we can immediately build the full date ..
    if has_year:
        year = int(year_time_info)
        out = date(year, month_number, day_number)

    # .. otherwise, we must find that year ourselves.
    else:
        #
        # The sftp binary prints a time of day only for entries modified in the last six months,
        # so a month later than the current one must have been in the previous year.
        #
        # If now is November 2183 and month is March    -> year was 2183
        # If now is February 2183 and month is December -> year was 2182
        #
        today = datetime.today()

        if month_number > today.month:
            year = today.year - 1
        else:
            year = today.year

        hour, minute = year_time_info.split(':')
        hour = int(hour)
        minute = int(minute)

        # The sftp binary formats the time in the local time zone of this process.
        local_time = datetime(year, month_number, day_number, hour, minute)
        out = local_time.astimezone(timezone.utc)

    return out

# ################################################################################################################################

def parse_ls_line(line:'str') -> 'SFTPInfo':

    match = _ls_line_pattern.match(line)

    if not match:
        raise Exception(f'Unrecognized directory listing line `{line}`')

    permissions = match['permissions']
    month = match['month']
    day = match['day']
    year_time_info = match['year_time_info']

    mode, permissions_oct = parse_permissions(permissions)
    last_modified = build_last_modified(month, day, year_time_info)

    out = SFTPInfo()

    out.type = get_entry_type(match['prefix'])
    out.name = match['name']
    out.permissions = mode
    out.permissions_oct = permissions_oct
    out.owner = match['owner']
    out.group = match['group']
    out.size = int(match['size'])
    out.last_modified = last_modified

    return out

# ################################################################################################################################

def parse_ls_output(ls_output:'str') -> 'sftp_info_list':

    out:'sftp_info_list' = []

    for line in ls_output.splitlines():
        parsed = parse_ls_line(line)
        out.append(parsed)

    return out

# ################################################################################################################################

def quote_path(path:'str') -> 'str':
    """ Returns a path in the shape a batch line accepts it. An unquoted name with a space in it
    would become several arguments, so every path is quoted, and a name carrying a quote
    or a backslash of its own has it escaped first.
    """
    escaped = path.replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')

    out = f'"{escaped}"'
    return out

# ################################################################################################################################

def parse_stdout(sftp_output:'SFTPOutput') -> 'sftp_info_list':
    """ The entries of the listing in the output of one `ls` command - the echoed prompt
    is stripped from the output, so an empty directory leaves no output at all.
    """
    out:'sftp_info_list' = []

    if sftp_output.stdout:
        out = parse_ls_output(sftp_output.stdout)

    return out

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

        self.last_modified:'any_' = None

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
