# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ##################################################################################################################################

class Bunch(dict):

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            try:
                return self[key]
            except KeyError:
                raise AttributeError(key)

    def to_dict(self):
        return dict(self)

    toDict = to_dict

# ##################################################################################################################################

def _bunchify(data, _Bunch):

    if isinstance(data, dict):
        b = _Bunch()
        for k, v in data.items():
            b[k] = _bunchify(v, _Bunch)
        return b

    elif isinstance(data, (list, tuple)):
        out = list()
        for elem in data:
            out.append(_bunchify(elem, _Bunch))

        if isinstance(data, list):
            return out
        else:
            return tuple(out)

    else:
        return data

# ##################################################################################################################################

def bunchify(data, _Bunch=Bunch):
    return _bunchify(data, _Bunch)

# ##################################################################################################################################
