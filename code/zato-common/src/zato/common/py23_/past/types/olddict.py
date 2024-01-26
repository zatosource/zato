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
A dict subclass for Python 3 that behaves like Python 2's dict

Example use:

>>> from zato.common.py23_.past.builtins import dict
>>> d1 = dict()    # instead of {} for an empty dict
>>> d2 = dict(key1='value1', key2='value2')

The keys, values and items methods now return lists on Python 3.x and there are
methods for iterkeys, itervalues, iteritems, and viewkeys etc.

>>> for d in (d1, d2):
...     assert isinstance(d.keys(), list)
...     assert isinstance(d.values(), list)
...     assert isinstance(d.items(), list)
"""

import sys

from zato.common.py23_.past.utils import with_metaclass


_builtin_dict = dict
ver = sys.version_info[:2]


class BaseOldDict(type):
    def __instancecheck__(cls, instance):
        return isinstance(instance, _builtin_dict)


class olddict(with_metaclass(BaseOldDict, _builtin_dict)):
    """
    A backport of the Python 3 dict object to Py2
    """
    iterkeys = _builtin_dict.keys
    viewkeys = _builtin_dict.keys

    def keys(self):
        return list(super(olddict, self).keys())

    itervalues = _builtin_dict.values
    viewvalues = _builtin_dict.values

    def values(self):
        return list(super(olddict, self).values())

    iteritems = _builtin_dict.items
    viewitems = _builtin_dict.items

    def items(self):
        return list(super(olddict, self).items())

    def has_key(self, k):
        """
        D.has_key(k) -> True if D has a key k, else False
        """
        return k in self

    # def __new__(cls, *args, **kwargs):
    #     """
    #     dict() -> new empty dictionary
    #     dict(mapping) -> new dictionary initialized from a mapping object's
    #         (key, value) pairs
    #     dict(iterable) -> new dictionary initialized as if via:
    #         d = {}
    #         for k, v in iterable:
    #             d[k] = v
    #     dict(**kwargs) -> new dictionary initialized with the name=value pairs
    #         in the keyword argument list.  For example:  dict(one=1, two=2)

    #     """
    #
    #     if len(args) == 0:
    #         return super(olddict, cls).__new__(cls)
    #     # Was: elif isinstance(args[0], newbytes):
    #     # We use type() instead of the above because we're redefining
    #     # this to be True for all unicode string subclasses. Warning:
    #     # This may render newstr un-subclassable.
    #     elif type(args[0]) == olddict:
    #         return args[0]
    #     # elif isinstance(args[0], _builtin_dict):
    #     #     value = args[0]
    #     else:
    #         value = args[0]
    #     return super(olddict, cls).__new__(cls, value)

    def __native__(self):
        """
        Hook for the past.utils.native() function
        """
        return super(oldbytes, self)


__all__ = ['olddict']
