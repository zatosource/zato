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
A resurrection of some old functions from Python 2 for use in Python 3. These
should be used sparingly, to help with porting efforts, since code using them
is no longer standard Python 3 code.

This module provides the following:

1. Implementations of these builtin functions which have no equivalent on Py3:

- apply
- chr
- cmp
- execfile

2. Aliases:

- intern <- sys.intern
- raw_input <- input
- reduce <- functools.reduce
- reload <- imp.reload
- unichr <- chr
- unicode <- str
- xrange <- range

3. List-producing versions of the corresponding Python 3 iterator-producing functions:

- filter
- map
- range
- zip

4. Forward-ported Py2 types:

- basestring
- dict
- str
- long
- unicode

"""

from zato.common.ext.future.utils import PY3
from zato.common.py23_.past.builtins.noniterators import (filter, map, range, reduce, zip)
# from zato.common.py23_.past.builtins.misc import (ascii, hex, input, oct, open)
if PY3:
    from zato.common.py23_.past.types import (basestring,
                            olddict as dict,
                            oldstr as str,
                            long,
                            unicode)
else:
    from __builtin__ import (basestring, dict, str, long, unicode)

from zato.common.py23_.past.builtins.misc import (apply, chr, cmp, execfile, intern, oct,
                                raw_input, unichr, unicode, xrange)
from zato.common.py23_.past import utils


if utils.PY3:
    # We only import names that shadow the builtins on Py3. No other namespace
    # pollution on Py3.

    # Only shadow builtins on Py3; no new names
    __all__ = ['filter', 'map', 'range', 'reduce', 'zip',
               'basestring', 'dict', 'str', 'long', 'unicode',
               'apply', 'chr', 'cmp', 'execfile', 'intern', 'raw_input',
               'unichr', 'xrange'
              ]

else:
    # No namespace pollution on Py2
    __all__ = []
