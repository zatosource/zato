# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
BELOW IS THE ORIGINAL LICENSE ON WHICH THIS SOFTWARE IS BASED.

2009-2018 (c) Benoît Chesneau <benoitc@e-engura.org>
2009-2015 (c) Paul J. Davis <paul.joseph.davis@gmail.com>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import os

SD_LISTEN_FDS_START = 3


def listen_fds(unset_environment=True):
    """
    Get the number of sockets inherited from systemd socket activation.

    :param unset_environment: clear systemd environment variables unless False
    :type unset_environment: bool
    :return: the number of sockets to inherit from systemd socket activation
    :rtype: int

    Returns zero immediately if $LISTEN_PID is not set to the current pid.
    Otherwise, returns the number of systemd activation sockets specified by
    $LISTEN_FDS.

    When $LISTEN_PID matches the current pid, unsets the environment variables
    unless the ``unset_environment`` flag is ``False``.

    .. note::
        Unlike the sd_listen_fds C function, this implementation does not set
        the FD_CLOEXEC flag because the gunicorn arbiter never needs to do this.

    .. seealso::
        `<https://www.freedesktop.org/software/systemd/man/sd_listen_fds.html>`_

    """
    fds = int(os.environ.get('LISTEN_FDS', 0))
    listen_pid = int(os.environ.get('LISTEN_PID', 0))

    if listen_pid != os.getpid():
        return 0

    if unset_environment:
        os.environ.pop('LISTEN_PID', None)
        os.environ.pop('LISTEN_FDS', None)

    return fds
