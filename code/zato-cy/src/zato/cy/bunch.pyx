
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

cdef object _bunchify(object data):

    if isinstance(data, dict):
        b = Bunch()
        for k, v in data.iteritems():
            b[k] = _bunchify(v)
        return b

    elif isinstance(data, (list, tuple)):
        out = list()
        for elem in data:
            out.append(_bunchify(elem))

        if isinstance(data, list):
            return out
        else:
            return tuple(out)

    else:
        return data

def bunchify(data):
    return _bunchify(data)
