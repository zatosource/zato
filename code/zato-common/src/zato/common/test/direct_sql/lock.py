# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Fault injection - a process of its own holds the write lock of the SQLite file of the Zato database without writing,
# which is what a session of another program that keeps a write transaction open does.

# stdlib
import sqlite3
import sys

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The line that the process writes to its stdout once it holds the lock
    Lock_Held_Line = 'Write lock held'

# ################################################################################################################################
# ################################################################################################################################

def hold_sqlite_write_lock(db_path:'str') -> 'None':
    """ Holds the write lock of an SQLite file until a line, or the end of input, arrives on stdin.
    """

    # Take the lock ..
    connection = sqlite3.connect(db_path, isolation_level=None)
    _ = connection.execute('begin immediate')

    # .. let the parent process know that it is held ..
    _ = sys.stdout.write(ModuleCtx.Lock_Held_Line + '\n')
    _ = sys.stdout.flush()

    # .. wait until the parent process releases it ..
    _ = sys.stdin.readline()

    # .. and release it with nothing written.
    _ = connection.execute('rollback')
    connection.close()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    hold_sqlite_write_lock(sys.argv[1])

# ################################################################################################################################
# ################################################################################################################################
