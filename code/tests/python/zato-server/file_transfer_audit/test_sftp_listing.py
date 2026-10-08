# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A listing of an SFTP directory is a list of its entries, and an empty directory
# is an empty list, the same as for SMB and FTP.

# Test support
from audit_env import audit_db_env
from sftp_stub import new_sftp_connection, ClientRecorder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os

# ################################################################################################################################
# ################################################################################################################################

# A directory nothing was put in, which an `ls` lists with no output at all
_empty_directory = '/documents/empty'

# ################################################################################################################################
# ################################################################################################################################

def test_an_empty_directory_lists_as_an_empty_list(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        conn = new_sftp_connection(ClientRecorder())

        assert conn.list(_empty_directory) == []

# ################################################################################################################################

def test_a_path_with_no_output_has_no_info(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        conn = new_sftp_connection(ClientRecorder())

        assert conn.get_info(_empty_directory) is None

# ################################################################################################################################
# ################################################################################################################################
