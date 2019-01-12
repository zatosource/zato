# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys

# Python2/3 compatibility
from future.utils import PY2

if PY2:
    maxint = sys.maxint
    from itertools import ifilter
else:
    maxint = sys.maxsize
    ifilter = filter
