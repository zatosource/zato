# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

true_values  =  'true', 'yes',  'on', 'y', 't', '1'
false_values = 'false',  'no', 'off', 'n', 'f', '0'

def as_bool(object_):

    if isinstance(object_, (str, bytes)):
        object_ = object_.strip().lower()
        if object_ in true_values:
            return True
        elif object_ in false_values:
            return False
        else:
            raise ValueError('String is not true/false: %r' % object_)

    return bool(object_)

def as_list(object_, sep=None, strip=True):
    if isinstance(object_, (str, bytes)):
        lst = object_.split(sep)
        if strip:
            lst = [v.strip() for v in lst]
        return lst
    elif isinstance(object_, (list, tuple)):
        return object_
    elif object_ is None:
        return []
    else:
        return [object_]

# ################################################################################################################################
