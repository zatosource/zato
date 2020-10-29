# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

true_values = ('true', 'yes', 'on', 'y', 't', '1')
false_values = ('false', 'no', 'off', 'n', 'f', '0', '', None)

def to_bool(value):
    if isinstance(value, basestring):
        _value = value.strip().lower()
        if _value in true_values:
            return True
        elif _value in false_values:
            return False
        else:
            raise ValueError('Value `{}` is not an expected boolean'.format(value))
    else:
        return bool(value)
