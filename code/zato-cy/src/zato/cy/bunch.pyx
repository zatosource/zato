# -*- coding: utf-8 -*-

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

cdef object _debunchify(object data):

    if isinstance(data, dict):
        return {
            k: _debunchify(v)
            for k, v in data.items()
        }

    elif isinstance(data, list):
        return [_debunchify(v) for v in data]

    elif isinstance(data, tuple):
        return tuple(_debunchify(v) for v in data)

    else:
        return data


# ##################################################################################################################################

cdef object _bunchify(object data, _Bunch):

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

def debunchify(data, _Bunch=Bunch):
    return _debunchify(data)

# ##################################################################################################################################
