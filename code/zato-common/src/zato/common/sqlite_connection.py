# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connections of the sqlite3 module to the SQLite files of Zato - the settings of durability of each connection,
# the SQL functions of Zato and the compressed form of the text that SQLite stores. The module imports no SQLAlchemy,
# so that a process that only opens a SQLite file does not load it.

# stdlib
import sqlite3
import zlib

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

# The type of a SQLite database, as the configuration of a database names it
Type_SQLite = 'sqlite'

# How long an SQLite write waits for another writer to finish before giving up,
# in milliseconds - without this, two processes sharing one file, e.g. a server
# and the cron-driven cleanup process, fail immediately with a locked-database
# error instead of taking turns. Writes are bounded batches, so the wait is short.
SQLite_Busy_Timeout_Ms = 5000

# How much of an SQLite database file is read through memory mapping rather than copied in with a read call per page,
# in bytes. SQLite lowers it to the maximum its build allows.
SQLite_MMAP_Size = 1024 ** 4

# The size of a page of a new SQLite database, in bytes. A commit writes each page that it modifies to the write-ahead log
# in full, and a commit of one event modifies a leaf page of each of the tables and indexes of the audit log.
SQLite_Page_Size = 1024

# The SQL function of each SQLite connection of Zato that returns the text of a value of CompressedText
SQLite_Decompress_Function = 'zato_decompress'

# The zlib level of the text that SQLite stores compressed, the fastest one
_compression_level = 1

# The encoding of the text that SQLite stores compressed
_compressed_text_encoding = 'utf8'

# ################################################################################################################################
# ################################################################################################################################

def compress_text(value:'str') -> 'bytes':
    """ Returns the text compressed as SQLite stores a value of CompressedText.
    """
    encoded = value.encode(_compressed_text_encoding)

    out = zlib.compress(encoded, _compression_level)
    return out

# ################################################################################################################################

def decompress_text(value:'bytes') -> 'str':
    """ Returns the text of a value of CompressedText as SQLite stores it.
    """
    decompressed = zlib.decompress(value)

    out = decompressed.decode(_compressed_text_encoding)
    return out

# ################################################################################################################################

def sqlite_decompress(value:'bytes | None') -> 'strnone':
    """ The SQL function SQLite_Decompress_Function, which returns the text of a value of CompressedText,
    or NULL for NULL.
    """
    if value is None:
        return None

    out = decompress_text(value)
    return out

# ################################################################################################################################

def set_sqlite_pragmas(dbapi_connection:'any_', connection_record:'any_') -> 'None':
    """ WAL mode lets multiple processes share the file safely, synchronous=FULL
    flushes the write-ahead log at each commit so that a committed transaction survives a power loss
    or a forced detachment of the volume, and the busy timeout makes concurrent writers from separate processes take turns.
    Secure deletion in its fast form zeroes deleted content on the pages a delete writes anyway and leaves freed
    overflow pages as they are, because SQLite builds that enable full secure deletion by default otherwise write
    each freed page of a large payload again, which doubles the cost of every commit that removes message bodies.
    Foreign keys are enforced, as on PostgreSQL. The file is read through memory mapping, which shares the pages
    of the operating system's cache among all the connections and processes instead of copying each page
    into the cache of each connection. A new database uses small pages, which reduces the bytes that each commit
    writes to the write-ahead log.
    """
    cursor = dbapi_connection.cursor()
    _ = cursor.execute(f'pragma page_size={SQLite_Page_Size}')
    _ = cursor.execute('pragma journal_mode=wal')
    _ = cursor.execute('pragma synchronous=full')
    _ = cursor.execute('pragma secure_delete=fast')
    _ = cursor.execute('pragma foreign_keys=on')
    _ = cursor.execute(f'pragma busy_timeout={SQLite_Busy_Timeout_Ms}')
    _ = cursor.execute(f'pragma mmap_size={SQLite_MMAP_Size}')
    cursor.close()

    register_sqlite_functions(dbapi_connection)

# ################################################################################################################################

def register_sqlite_functions(dbapi_connection:'any_') -> 'None':
    """ Registers the SQL functions of Zato on a connection of the sqlite3 module, the one that returns the text
    of a value of CompressedText among them.
    """
    dbapi_connection.create_function(SQLite_Decompress_Function, 1, sqlite_decompress, deterministic=True)

# ################################################################################################################################

def connect_sqlite_file(db_path:'str') -> 'sqlite3.Connection':
    """ Returns a connection of the sqlite3 module to a SQLite file of Zato, with the settings of durability
    that each connection of the engine factory has.
    """
    out = sqlite3.connect(db_path)
    set_sqlite_pragmas(out, None)

    return out

# ################################################################################################################################
# ################################################################################################################################
