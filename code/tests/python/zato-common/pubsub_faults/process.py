# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the server of one fault of a single server - the cgroup that the server runs in
# and the libraries preloaded into its processes, which change nothing until a fault is applied.

# stdlib
import os
from itertools import count

# Zato
from process_faults import Clock_No_Offset, Scope, write_control_file
from tools import build_faketime, build_fsfault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How often libfaketime reads its timestamp file, in seconds.
_faketime_cache_seconds = '1'

# The numbers of the scopes of this test process.
_scope_numbers = count(1)

# ################################################################################################################################
# ################################################################################################################################

class ProcessEnvironment:
    """ The database of the faults of single servers - a PostgreSQL container whose processes preload the library
    of the file system faults - and the control files of that library.
    """

    def __init__(self, work_dir:'str', database:'PubSubDatabase') -> 'None':
        self.work_dir = work_dir
        self.database = database

        # The control file and the prefix of the files of the server and its cleanup process ..
        self.server_control = os.path.join(work_dir, 'fsfault-server')
        self.server_prefix = work_dir

        # .. and those of PostgreSQL, as its container sees them.
        self.database_control = os.path.join(work_dir, 'fsfault-control', 'postgresql')
        self.database_prefix = '/var/lib/postgresql/data'

        self.timestamp_file = os.path.join(work_dir, 'faketime')

# ################################################################################################################################
# ################################################################################################################################

def new_scope() -> 'Scope':
    number = next(_scope_numbers)
    pid = os.getpid()

    out = Scope(f'zato-pubsub-fault-{pid}-{number}')
    out.create()

    return out

# ################################################################################################################################

def get_process_env(environment:'ProcessEnvironment') -> 'strstrdict':
    """ The variables of the server and its cleanup process, whose processes preload both libraries after
    the libraries that this process preloads itself, with the clock of the server starting without an offset.
    """
    write_control_file(environment.timestamp_file, Clock_No_Offset)

    fsfault_path = build_fsfault()
    faketime_path = build_faketime()

    preload = f'{fsfault_path} {faketime_path}'

    if current_preload := os.environ.get('LD_PRELOAD', ''):
        preload = f'{current_preload} {preload}'

    out:'strstrdict' = {
        'LD_PRELOAD': preload,
        'ZATO_FSFAULT_CONTROL': environment.server_control,
        'FAKETIME_TIMESTAMP_FILE': environment.timestamp_file,
        'FAKETIME_CACHE_DURATION': _faketime_cache_seconds,
        'FAKETIME_DONT_FAKE_MONOTONIC': '1',
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
