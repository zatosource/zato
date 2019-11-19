# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from butler import Butler

class DictNav(Butler):
    """ Easy navigation over Python dicts.
    """
    def get(self, path, default=None):
        """ Overridden from the base class so it doesn't display warnings on non-existing paths.
        """
        try:
            return self[path]
        except (LookupError, TypeError):
            return default

    def has_key(self, key, nested=True):
        if nested:
            return bool(self.findall(key, True))

        return key in self.obj

    def has_path(self, path):
        return super(DictNav, self).path_exists(path)

# For now they are the same class but may part at some time
ListNav = DictNav
