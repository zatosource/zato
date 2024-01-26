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
Various non-built-in utility functions and definitions for Py2
compatibility in Py3.

For example:

    >>> # The old_div() function behaves like Python 2's / operator
    >>> # without "from __future__ import division"
    >>> from zato.common.py23_.past.utils import old_div
    >>> old_div(3, 2)    # like 3/2 in Py2
    0
    >>> old_div(3, 2.0)  # like 3/2.0 in Py2
    1.5
"""

import sys
import numbers

PY3 = sys.version_info[0] >= 3
PY2 = sys.version_info[0] == 2
PYPY = hasattr(sys, 'pypy_translation_info')


def with_metaclass(meta, *bases):
    """
    Function from jinja2/_compat.py. License: BSD.

    Use it like this::

        class BaseForm(object):
            pass

        class FormType(type):
            pass

        class Form(with_metaclass(FormType, BaseForm)):
            pass

    This requires a bit of explanation: the basic idea is to make a
    dummy metaclass for one level of class instantiation that replaces
    itself with the actual metaclass.  Because of internal type checks
    we also need to make sure that we downgrade the custom metaclass
    for one level to something closer to type (that's why __call__ and
    __init__ comes back from type etc.).

    This has the advantage over six.with_metaclass of not introducing
    dummy classes into the final MRO.
    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})


def native(obj):
    """
    On Py2, this is a no-op: native(obj) -> obj

    On Py3, returns the corresponding native Py3 types that are
    superclasses for forward-ported objects from Py2:

    >>> from zato.common.py23_.past.builtins import str, dict

    >>> native(str(b'ABC'))   # Output on Py3 follows. On Py2, output is 'ABC'
    b'ABC'
    >>> type(native(str(b'ABC')))
    bytes

    Existing native types on Py3 will be returned unchanged:

    >>> type(native(b'ABC'))
    bytes
    """
    if hasattr(obj, '__native__'):
        return obj.__native__()
    else:
        return obj


# An alias for future.utils.old_div():
def old_div(a, b):
    """
    Equivalent to ``a / b`` on Python 2 without ``from __future__ import
    division``.

    TODO: generalize this to other objects (like arrays etc.)
    """
    if isinstance(a, numbers.Integral) and isinstance(b, numbers.Integral):
        return a // b
    else:
        return a / b

__all__ = ['PY3', 'PY2', 'PYPY', 'with_metaclass', 'native', 'old_div']
