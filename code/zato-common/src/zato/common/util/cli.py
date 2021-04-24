# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################

if 0:
    from logging import Logger

    Logger = Logger

# ################################################################################################################################

def read_stdin_data(strip=True):
    """ Reads data from sys.stdin without blocking the caller - in its current form (using select),
    it will work only on Linux and OS X.
    """
    # stdlib
    import select
    import sys

    # Note that we check only sys.stdin for read and that there is no timeout,
    # because we expect for sys.stdin to be available immediately when we run.
    to_read, _, _ = select.select([sys.stdin], [], [], 0)

    if to_read:
        data = to_read[0].readline()
        out = data.strip() if strip else data
    else:
        out = ''

    return out

# ################################################################################################################################

def delete_pidfile(logger, component_dir):
    # type: (Logger, str) -> None

    # stdlib
    import os

    # Zato
    from zato.common.api import MISC

    try:
        path = os.path.join(component_dir, MISC.PIDFILE)
        os.remove(path)
    except Exception as e:
        logger.info('Pidfile `%s` could not be deleted; `%s`', path, e)

# ################################################################################################################################
