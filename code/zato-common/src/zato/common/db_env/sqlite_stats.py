# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The statistics of the SQLite files of a process - the bytes, write requests, syncs and the time spent in syncs
# of each type of file, the main databases, the write-ahead logs, the statement journals and the temporary files,
# together with the memory of SQLite in the process, written once per interval as one JSON line to a file per process.
# The counts of the files are read from the vfsstat table, which a build of SQLite with the vfsstat VFS provides.

# stdlib
import ctypes
import os
from json import dumps
from time import monotonic, time

# SQLite
import _sqlite3

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the directory into which each process writes the statistics of its SQLite files
Env_Stats_Dir = 'Zato_SQLite_Stats_Dir'

# How often a process writes its statistics, in seconds
Stats_Interval_Seconds = 1.0

# The counts of the files of the process, by the type of the file and the name of the count
_files_query = 'select file, stat, count from vfsstat where count > 0'

# The counters of SQLite in the whole process, by their names and their codes in sqlite3_status64
_process_counters = (
    ('memory_used', 0),
    ('pagecache_overflow', 2),
    ('malloc_count', 9),
)

# ################################################################################################################################
# ################################################################################################################################

class _ModuleCtx:

    # The library of SQLite that the sqlite3 module of this process is linked against
    library = ctypes.CDLL(_sqlite3.__file__)

    # When the statistics were last written
    last_written = 0.0

# ################################################################################################################################

_library = _ModuleCtx.library

_library.sqlite3_status64.argtypes = [
    ctypes.c_int, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int]

# ################################################################################################################################
# ################################################################################################################################

def _read_process_counters() -> 'anydict':
    """ Returns the current values and the highest values of the counters of SQLite in the whole process.
    """
    out:'anydict' = {}

    current = ctypes.c_int64()
    highwater = ctypes.c_int64()

    for name, code in _process_counters:
        _ = _library.sqlite3_status64(code, ctypes.byref(current), ctypes.byref(highwater), 0)
        out[name] = current.value
        out[f'{name}_high'] = highwater.value

    return out

# ################################################################################################################################

def _write_stats(dbapi_connection:'any_', stats_dir:'str') -> 'None':
    """ Appends the counts of the files of this process and the counters of SQLite to the file of this process.
    """
    # Read the counts of the files, which the VFS keeps for the whole process ..
    files:'anydict' = {}

    for file_type, stat, count in dbapi_connection.execute(_files_query):
        if file_type not in files:
            files[file_type] = {}
        files[file_type][stat] = count

    # .. add the counters of the whole process ..
    line = {'time': time(), 'pid': os.getpid(), 'files': files}
    line.update(_read_process_counters())

    # .. and append them as one line to the file of this process.
    path = os.path.join(stats_dir, f'sqlite-stats-{os.getpid()}.jsonl')

    with open(path, 'a') as stats_file:
        _ = stats_file.write(dumps(line) + '\n')

# ################################################################################################################################

def collect_sqlite_stats(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Writes the statistics of this process into the directory that the environment names, when a connection
    returns to its pool and an interval has passed since they were last written.
    """
    # A connection that was invalidated returns to the pool without its DBAPI connection.
    if dbapi_connection is None:
        return

    now = monotonic()

    if now - _ModuleCtx.last_written >= Stats_Interval_Seconds:
        _ModuleCtx.last_written = now
        _write_stats(dbapi_connection, os.environ[Env_Stats_Dir])

# ################################################################################################################################
# ################################################################################################################################
