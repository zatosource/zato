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
Forward-ports of types from Python 2 for use with Python 3:

- ``basestring``: equivalent to ``(str, bytes)`` in ``isinstance`` checks
- ``dict``: with list-producing .keys() etc. methods
- ``str``: bytes-like, but iterating over them doesn't product integers
- ``long``: alias of Py3 int with ``L`` suffix in the ``repr``
- ``unicode``: alias of Py3 str with ``u`` prefix in the ``repr``

"""

from zato.common.py23_.past import utils

if utils.PY2:
    import __builtin__
    basestring = __builtin__.basestring
    dict = __builtin__.dict
    str = __builtin__.str
    long = __builtin__.long
    unicode = __builtin__.unicode
    __all__ = []
else:
    from .basestring import basestring
    from .olddict import olddict
    from .oldstr import oldstr
    long = int
    unicode = str
    # from .unicode import unicode
    __all__ = ['basestring', 'olddict', 'oldstr', 'long', 'unicode']
