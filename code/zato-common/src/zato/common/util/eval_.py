# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

true_values  =  'true', 'yes',  'on', 'y', 't', '1' # noqa: E222
false_values = 'false',  'no', 'off', 'n', 'f', '0'

def as_bool(data):

    if isinstance(data, (str, bytes)):
        data = data.strip().lower()
        if data in true_values:
            return True
        elif data in false_values:
            return False
        elif data == '':
            return False
        else:
            raise ValueError('String is not true/false: %r' % data)

    return bool(data)

def as_list(data, sep=None, strip=True):
    if isinstance(data, (str, bytes)):
        lst = data.split(sep)
        if strip:
            lst = [v.strip() for v in lst]
        return lst
    elif isinstance(data, (list, tuple)):
        return data
    elif data is None:
        return []
    else:
        return [data]

# ################################################################################################################################
