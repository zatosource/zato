# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

"""

Copyright (c) 2013-2019 Python Charmers Pty Ltd, Australia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

# ################################################################################################################################
# ################################################################################################################################

"""
Pure-Python implementation of a Python 2-like str object for Python 3.
"""

from numbers import Integral

from zato.common.py23_.past.utils import PY2, with_metaclass

if PY2:
    from collections import Iterable
else:
    from collections.abc import Iterable

_builtin_bytes = bytes


class BaseOldStr(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, _builtin_bytes)


def unescape(s):
    return s.encode().decode('unicode_escape')


class oldstr(with_metaclass(BaseOldStr, _builtin_bytes)):
    """
    A forward port of the Python 2 8-bit string object to Py3
    """
    # Python 2 strings have no __iter__ method:
    @property
    def __iter__(self):
        raise AttributeError

    def __dir__(self):
        return [thing for thing in dir(_builtin_bytes) if thing != '__iter__']

    # def __new__(cls, *args, **kwargs):
    #     """
    #     From the Py3 bytes docstring:

    #     bytes(iterable_of_ints) -> bytes
    #     bytes(string, encoding[, errors]) -> bytes
    #     bytes(bytes_or_buffer) -> immutable copy of bytes_or_buffer
    #     bytes(int) -> bytes object of size given by the parameter initialized with null bytes
    #     bytes() -> empty bytes object
    #
    #     Construct an immutable array of bytes from:
    #       - an iterable yielding integers in range(256)
    #       - a text string encoded using the specified encoding
    #       - any object implementing the buffer API.
    #       - an integer
    #     """
    #
    #     if len(args) == 0:
    #         return super(newbytes, cls).__new__(cls)
    #     # Was: elif isinstance(args[0], newbytes):
    #     # We use type() instead of the above because we're redefining
    #     # this to be True for all unicode string subclasses. Warning:
    #     # This may render newstr un-subclassable.
    #     elif type(args[0]) == newbytes:
    #         return args[0]
    #     elif isinstance(args[0], _builtin_bytes):
    #         value = args[0]
    #     elif isinstance(args[0], unicode):
    #         if 'encoding' not in kwargs:
    #             raise TypeError('unicode string argument without an encoding')
    #         ###
    #         # Was:   value = args[0].encode(**kwargs)
    #         # Python 2.6 string encode() method doesn't take kwargs:
    #         # Use this instead:
    #         newargs = [kwargs['encoding']]
    #         if 'errors' in kwargs:
    #             newargs.append(kwargs['errors'])
    #         value = args[0].encode(*newargs)
    #         ###
    #     elif isinstance(args[0], Iterable):
    #         if len(args[0]) == 0:
    #             # What is this?
    #             raise ValueError('unknown argument type')
    #         elif len(args[0]) > 0 and isinstance(args[0][0], Integral):
    #             # It's a list of integers
    #             value = b''.join([chr(x) for x in args[0]])
    #         else:
    #             raise ValueError('item cannot be interpreted as an integer')
    #     elif isinstance(args[0], Integral):
    #         if args[0] < 0:
    #             raise ValueError('negative count')
    #         value = b'\x00' * args[0]
    #     else:
    #         value = args[0]
    #     return super(newbytes, cls).__new__(cls, value)

    def __repr__(self):
        s = super(oldstr, self).__repr__()   # e.g. b'abc' on Py3, b'abc' on Py3
        return s[1:]

    def __str__(self):
        s = super(oldstr, self).__str__()   # e.g. "b'abc'" or "b'abc\\ndef'
        # TODO: fix this:
        assert s[:2] == "b'" and s[-1] == "'"
        return unescape(s[2:-1])            # e.g. 'abc'    or 'abc\ndef'

    def __getitem__(self, y):
        if isinstance(y, Integral):
            return super(oldstr, self).__getitem__(slice(y, y+1))
        else:
            return super(oldstr, self).__getitem__(y)

    def __getslice__(self, *args):
        return self.__getitem__(slice(*args))

    def __contains__(self, key):
        if isinstance(key, int):
            return False

    def __native__(self):
        return bytes(self)


__all__ = ['oldstr']
