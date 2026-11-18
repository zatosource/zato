# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The statistics of the SQLite connections of a process - the page cache hits, misses, writes and spills of each
# database file and the bytes spilled to temporary files, read from SQLite each time a connection returns to its pool,
# together with the memory of SQLite in the process, written once per interval as one JSON line to a file per process.

# stdlib
import ctypes
import os
from itertools import count
from json import dumps
from time import monotonic, time

# SQLite
import _sqlite3

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, intlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the directory into which each process writes the statistics of its SQLite connections
Env_Stats_Dir = 'Zato_SQLite_Stats_Dir'

# How often a process writes its statistics, in seconds
Stats_Interval_Seconds = 1.0

# The counters of each connection, by their names and their codes in sqlite3_db_status64
_connection_counters = (
    ('cache_hit', 7),
    ('cache_miss', 8),
    ('cache_write', 9),
    ('cache_spill', 12),
    ('tempbuf_spill', 13),
)

# The counters of SQLite in the whole process, by their names and their codes in sqlite3_status64
_process_counters = (
    ('memory_used', 0),
    ('pagecache_overflow', 2),
    ('malloc_count', 9),
)

# The handle of the database is the first field of a connection object of the sqlite3 module after the object header,
# which consists of the reference count and the type pointer.
_db_handle_offset = 16

# The key under which a connection record keeps the statistics of its connection
_record_key = 'zato_sqlite_stats'

# ################################################################################################################################
# ################################################################################################################################

class _ModuleCtx:

    # The library of SQLite that the sqlite3 module of this process is linked against
    library = ctypes.CDLL(_sqlite3.__file__)

    # A unique number for each connection of this process
    connection_numbers = count()

    # The latest counters of each connection of this process, by the number of the connection
    connection_stats:'anydict' = {}

    # When the statistics were last written
    last_written = 0.0

# ################################################################################################################################

_library = _ModuleCtx.library

_library.sqlite3_db_filename.restype = ctypes.c_char_p
_library.sqlite3_db_filename.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

_library.sqlite3_db_status64.argtypes = [
    ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int]

_library.sqlite3_status64.argtypes = [
    ctypes.c_int, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64), ctypes.c_int]

# ################################################################################################################################
# ################################################################################################################################

def _read_connection_counters(db_handle:'int') -> 'intlist':
    """ Returns the cumulative counters of one connection, in the order of _connection_counters.
    """
    out:'intlist' = []

    current = ctypes.c_int64()
    highwater = ctypes.c_int64()

    for _, code in _connection_counters:
        _ = _library.sqlite3_db_status64(db_handle, code, ctypes.byref(current), ctypes.byref(highwater), 0)
        out.append(current.value)

    return out

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

def _write_stats(stats_dir:'str') -> 'None':
    """ Appends the totals of the connections of each database file of this process to the file of this process.
    """
    # Sum up the counters of all the connections, the closed ones included, by their database files ..
    databases:'anydict' = {}

    for db_path, counters in list(_ModuleCtx.connection_stats.values()):
        if db_path not in databases:
            databases[db_path] = dict.fromkeys(['connections'] + [name for name, _ in _connection_counters], 0)

        totals = databases[db_path]
        totals['connections'] += 1

        for (name, _), value in zip(_connection_counters, counters):
            totals[name] += value

    # .. add the counters of the whole process ..
    line = {'time': time(), 'pid': os.getpid(), 'databases': databases}
    line.update(_read_process_counters())

    # .. and append them as one line to the file of this process.
    path = os.path.join(stats_dir, f'sqlite-stats-{os.getpid()}.jsonl')

    with open(path, 'a') as stats_file:
        _ = stats_file.write(dumps(line) + '\n')

# ################################################################################################################################

def collect_sqlite_stats(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ Records the counters of a connection that returns to its pool, and writes the statistics of this process
    once per interval into the directory that the environment names.
    """
    # A connection that was invalidated returns to the pool without its DBAPI connection.
    if dbapi_connection is None:
        return

    db_handle = cast_('int', ctypes.c_void_p.from_address(id(dbapi_connection) + _db_handle_offset).value)

    # The first time a connection returns, it receives its number and the path of its database file ..
    if _record_key not in connection_record.info:
        db_path = _library.sqlite3_db_filename(db_handle, b'main').decode('utf8')
        connection_record.info[_record_key] = (next(_ModuleCtx.connection_numbers), db_path)

    connection_number, db_path = connection_record.info[_record_key]

    # .. its latest counters replace the ones it had before ..
    _ModuleCtx.connection_stats[connection_number] = (db_path, _read_connection_counters(db_handle))

    # .. and the statistics are written if an interval has passed since they were last written.
    now = monotonic()

    if now - _ModuleCtx.last_written >= Stats_Interval_Seconds:
        _ModuleCtx.last_written = now
        _write_stats(os.environ[Env_Stats_Dir])

# ################################################################################################################################
# ################################################################################################################################
