# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import math

# ################################################################################################################################
# ################################################################################################################################

def tmean(data, limit_from=None, limit_to=None):
    """ Trimmed mean - includes only elements up to the input limit, if it is given at all.
    """
    data = data if isinstance(data, list) else [data]

    if limit_from or limit_to:
        _data = []
        for elem in data:
            if limit_from:
                if elem < limit_from:
                    continue
            if limit_to:
                if elem > limit_to:
                    continue
            _data.append(elem)
        data = _data[:]

    count = len(data)
    total = sum(data)

    return total / count if count else 0

# ################################################################################################################################
# ################################################################################################################################

#
# Taken from https://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
#
# Original code by Wai Yip Tung, licensed under the Python Foundation License
#
def percentile(data, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter data - a list of values
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of data.

    @return - the percentile of the values
    """
    if not data:
        return 0

    data.sort()
    k = (len(data)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(data[int(k)])
    d0 = key(data[int(f)]) * (c-k)
    d1 = key(data[int(c)]) * (k-f)

    return d0 + d1

# ################################################################################################################################
# ################################################################################################################################
