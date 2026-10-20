# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A listing of an SFTP directory is a list of its entries, and an empty directory
# is an empty list, the same as for SMB and FTP. Each entry is parsed from a line
# the sftp binary formats itself, and a directory is described by its entry in its parent.

# stdlib
from datetime import date, timezone

# pytest
import pytest

# Zato
from zato.server.connection.sftp_listing import parse_ls_line

# Test support
from audit_env import audit_db_env
from sftp_stub import new_sftp_connection, ClientRecorder, Ls_Line

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os

# ################################################################################################################################
# ################################################################################################################################

# A directory nothing was put in, which an `ls` lists with no output at all
_empty_directory = '/documents/empty'

# A directory with one file in it, and its parent
_directory = '/documents/incoming'
_parent_directory = '/documents'

# A file to read and what it holds
_file_path = '/documents/results.csv'
_file_content = b'order_id,amount\n1001,250.00\n'

# A path the server does not have
_missing_path = '/documents/missing.csv'

# A file whose name begins with spaces
_leading_spaces_path = '/documents/  report.csv'

# The listing line of a directory
_directory_line = 'drwxr-xr-x    ? 1000     1000         4096 Mar  3 11:50 {name}'

# The listing line of an entry modified in an earlier year, on a leap day
_leap_day_line = '-rw-r--r--    ? 1000     1000           12 Feb 29  2024 /documents/leap.csv'

# The listing line of an entry modified recently, which has a time of day instead of a year
_time_of_day_line = '-rw-r--r--    ? 1000     1000           12 Mar  3 11:50 /documents/recent.csv'

# The hour and minute of that line, in local time
_time_of_day_hour = 11
_time_of_day_minute = 50

# ################################################################################################################################
# ################################################################################################################################

def test_a_name_with_leading_spaces_keeps_them() -> 'None':

    line = Ls_Line.format(size=12, name=_leading_spaces_path)
    info = parse_ls_line(line)

    assert info.name == _leading_spaces_path
    assert info.size == 12

# ################################################################################################################################

@pytest.mark.parametrize('permissions, expected_oct', [
    ('-rwsr-xr-x', '4755'),
    ('-rw-r-Sr--', '2644'),
    ('drwxrwxrwt', '1777'),
    ('drwxrwxrwT', '1776'),
    ('-rw-r--r--', '644'),
])
def test_special_permission_bits_are_kept(permissions:'str', expected_oct:'str') -> 'None':

    line = f'{permissions}    ? 1000     1000           12 Mar  3 11:50 /documents/file.csv'
    info = parse_ls_line(line)

    assert info.permissions_oct == expected_oct
    assert info.permissions == int(expected_oct, 8)

# ################################################################################################################################

def test_owner_and_group_are_numeric() -> 'None':

    line = Ls_Line.format(size=12, name='/documents/file.csv')
    info = parse_ls_line(line)

    assert info.owner == '1000'
    assert info.group == '1000'

# ################################################################################################################################

def test_a_time_of_day_is_a_utc_datetime() -> 'None':

    info = parse_ls_line(_time_of_day_line)
    last_modified = info.last_modified

    # The time is in UTC ..
    assert last_modified.tzinfo == timezone.utc

    # .. and it is the local time of the line converted.
    local_time = last_modified.astimezone()

    assert local_time.hour == _time_of_day_hour
    assert local_time.minute == _time_of_day_minute

# ################################################################################################################################

def test_a_year_on_a_leap_day_is_a_date() -> 'None':

    info = parse_ls_line(_leap_day_line)

    assert info.last_modified == date(2024, 2, 29)

# ################################################################################################################################

def test_an_unrecognized_line_raises() -> 'None':

    with pytest.raises(Exception, match='Unrecognized directory listing line'):
        _ = parse_ls_line('total 0')

# ################################################################################################################################

def test_an_empty_directory_lists_as_an_empty_list(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)

        assert conn.list(_empty_directory) == []
        assert sftp_client.commands == [f'ls -ln "{_empty_directory}"']

# ################################################################################################################################

def test_a_path_with_no_output_has_no_info(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        conn = new_sftp_connection(ClientRecorder())

        assert conn.get_info(_empty_directory) is None

# ################################################################################################################################

def test_a_directory_is_described_by_its_entry_in_the_parent(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()

        # The directory lists its file, while the parent lists the directory itself
        sftp_client.listing_by_path[_directory] = Ls_Line.format(size=12, name=f'{_directory}/file.csv')
        sftp_client.listing_by_path[_parent_directory] = _directory_line.format(name=_directory)

        conn = new_sftp_connection(sftp_client)
        info = conn.get_info(_directory)

        assert info is not None
        assert info.is_directory
        assert info.name == _directory

        assert sftp_client.commands == [f'ls -ln "{_directory}"', f'ls -lna "{_parent_directory}"']

# ################################################################################################################################

def test_a_missing_path_has_no_info(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        sftp_client.missing_paths.add(_missing_path)

        conn = new_sftp_connection(sftp_client)

        # Without raising, a missing path has no information ..
        assert conn.get_info(_missing_path, raise_on_error=False) is None

        # .. while the checks of its type raise an exception.
        with pytest.raises(Exception):
            _ = conn.is_file(_missing_path)

# ################################################################################################################################

def test_a_path_absent_from_its_parent_does_not_exist(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        conn = new_sftp_connection(ClientRecorder())

        with pytest.raises(Exception, match='does not exist'):
            _ = conn.is_directory(_empty_directory)

# ################################################################################################################################

def test_a_move_never_replaces_its_target(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)

        _ = conn.move('/documents/a.csv', '/documents/b.csv')

        assert sftp_client.commands == ['rename -l "/documents/a.csv" "/documents/b.csv"']

# ################################################################################################################################

def test_a_directory_that_may_exist_is_created_without_failing(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        conn = new_sftp_connection(sftp_client)

        _ = conn.create_directory(_directory, exist_ok=True)
        _ = conn.create_directory(_directory)

        assert sftp_client.commands == [f'-mkdir "{_directory}"', f'mkdir "{_directory}"']

# ################################################################################################################################

def test_a_read_is_a_single_get(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        sftp_client = ClientRecorder()
        sftp_client.content_by_path[_file_path] = _file_content
        conn = new_sftp_connection(sftp_client)

        data = conn.read(_file_path)

        assert data == _file_content
        assert len(sftp_client.commands) == 1
        assert sftp_client.commands[0].startswith(f'get "{_file_path}" ')

# ################################################################################################################################
# ################################################################################################################################
