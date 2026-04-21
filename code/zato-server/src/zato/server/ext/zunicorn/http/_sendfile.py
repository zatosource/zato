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

import errno
import os
import sys

try:
    import ctypes
    import ctypes.util
except MemoryError:
    # selinux execmem denial
    # https://bugzilla.redhat.com/show_bug.cgi?id=488396
    raise ImportError

SUPPORTED_PLATFORMS = (
    'darwin',
    'freebsd',
    'dragonfly',
    'linux2')

if sys.platform not in SUPPORTED_PLATFORMS:
    raise ImportError("sendfile isn't supported on this platform")

_libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
_sendfile = _libc.sendfile


def sendfile(fdout, fdin, offset, nbytes):
    if sys.platform == 'darwin':
        _sendfile.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                              ctypes.POINTER(ctypes.c_uint64), ctypes.c_voidp,
                              ctypes.c_int]
        _nbytes = ctypes.c_uint64(nbytes)
        result = _sendfile(fdin, fdout, offset, _nbytes, None, 0)

        if result == -1:
            e = ctypes.get_errno()
            if e == errno.EAGAIN and _nbytes.value is not None:
                return _nbytes.value
            raise OSError(e, os.strerror(e))
        return _nbytes.value
    elif sys.platform in ('freebsd', 'dragonfly',):
        _sendfile.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                              ctypes.c_uint64, ctypes.c_voidp,
                              ctypes.POINTER(ctypes.c_uint64), ctypes.c_int]
        _sbytes = ctypes.c_uint64()
        result = _sendfile(fdin, fdout, offset, nbytes, None, _sbytes, 0)
        if result == -1:
            e = ctypes.get_errno()
            if e == errno.EAGAIN and _sbytes.value is not None:
                return _sbytes.value
            raise OSError(e, os.strerror(e))
        return _sbytes.value

    else:
        _sendfile.argtypes = [ctypes.c_int, ctypes.c_int,
                ctypes.POINTER(ctypes.c_uint64), ctypes.c_size_t]

        _offset = ctypes.c_uint64(offset)
        sent = _sendfile(fdout, fdin, _offset, nbytes)
        if sent == -1:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e))
        return sent
