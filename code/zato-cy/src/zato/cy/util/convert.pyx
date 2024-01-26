# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

true_values = ('true', 'yes', 'on', 'y', 't', '1')
false_values = ('false', 'no', 'off', 'n', 'f', '0', '', None)

def to_bool(data):

    if isinstance(data, (str, bytes)):
        data = data.strip().lower()
        if data in true_values:
            return True
        elif data in false_values:
            return False
        else:
            raise ValueError('String is not true/false: %r' % data)

    return bool(data)

def to_list(data, sep=None, strip=True):
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

as_bool = to_bool
as_list = to_list
