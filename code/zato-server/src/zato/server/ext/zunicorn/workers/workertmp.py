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

# flake8: noqa

import os
import platform
import tempfile

from zato.server.ext.zunicorn import util

PLATFORM = platform.system()
IS_CYGWIN = PLATFORM.startswith('CYGWIN')

# ################################################################################################################################
# ################################################################################################################################

class PassThroughTmp:
    """ Used under windows in lieu of WorkerTmp.
    """
    def __init__(self, *ignored_args, **ignored_kwargs):
        pass

    def notify(self, *ignored_args, **ignored_kwargs):
        pass

    def last_update(self, *ignored_args, **ignored_kwargs):
        pass

    def fileno(self, *ignored_args, **ignored_kwargs):
        pass

    def close(self, *ignored_args, **ignored_kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################

class WorkerTmp:

    def __init__(self, cfg):
        old_umask = os.umask(cfg.umask)
        fdir = cfg.worker_tmp_dir
        if fdir and not os.path.isdir(fdir):
            raise RuntimeError("%s doesn't exist. Can't create workertmp." % fdir)
        fd, name = tempfile.mkstemp(prefix="wgunicorn-", dir=fdir)

        # allows the process to write to the file
        util.chown(name, cfg.uid, cfg.gid)
        os.umask(old_umask)

        # unlink the file so we don't leak tempory files
        try:
            if not IS_CYGWIN:
                util.unlink(name)
            self._tmp = os.fdopen(fd, 'w+b')
        except:
            os.close(fd)
            raise

        self.spinner = 0

    def notify(self):
        try:
            self.spinner = (self.spinner + 1) % 2
            os.fchmod(self._tmp.fileno(), self.spinner)
        except AttributeError:
            # python < 2.6
            self._tmp.truncate(0)
            os.write(self._tmp.fileno(), b"X")

    def last_update(self):
        return os.fstat(self._tmp.fileno()).st_ctime

    def fileno(self):
        return self._tmp.fileno()

    def close(self):
        return self._tmp.close()

# ################################################################################################################################
# ################################################################################################################################
