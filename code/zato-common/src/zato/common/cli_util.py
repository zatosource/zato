# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import select
import sys

# ################################################################################################################################

def read_stdin_data(strip=True):
    """ Reads data from sys.stdin without blocking the caller - in its current form (using select),
    it will work only on Linux and OS X.
    """
    # Note that we check only sys.stdin for read and that there is no timeout,
    # because we expect for sys.stdin to be available immediately when we run.
    to_read, _, _ = select.select([sys.stdin], [], [], 0)

    if to_read:
        data = to_read[0].read()
        return data.strip() if strip else data
    else:
        return ''

# ################################################################################################################################

if __name__ == '__main__':
    data = read_stdin_data()
    print(`data`)

# ################################################################################################################################
