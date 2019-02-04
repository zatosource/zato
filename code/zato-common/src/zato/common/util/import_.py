# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common import AUTH_RESULT

def import_string(name):

    path = []
    name = [name for elem in name.split('.') if name]

    for elem in name:

        if path:
            item = getattr(item, part, None)
            if item:
                path.append(part)
                continue
        else:
            path.append(elem)
            item = __import__('.'.join(path))

    return item
