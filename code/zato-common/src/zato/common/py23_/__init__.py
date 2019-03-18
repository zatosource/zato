# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys
from threading import Thread

# Python2/3 compatibility
from future.utils import PY2

if PY2:
    maxint = sys.maxint
    from itertools import ifilter
    from itertools import izip
    from cPickle import dumps as pickle_dumps
    from cPickle import loads as pickle_loads
else:
    maxint = sys.maxsize
    ifilter = filter
    izip = zip
    from pickle import dumps as pickle_dumps
    from pickle import loads as pickle_loads

# For pyflakes
maxint = maxint
ifilter = ifilter
izip = izip
pickle_dumps = pickle_dumps
pickle_loads = pickle_loads

def start_new_thread(target, args):
    return Thread(target=target, args=args).start()
