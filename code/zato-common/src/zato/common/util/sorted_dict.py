# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

class SortedDict(dict): # type: ignore
    def __iter__(self):
        return iter(sorted(super().__iter__()))

    def items(self):
        return ((k, self[k]) for k in sorted(self.keys()))

    def keys(self):
        return sorted(super().keys())

    def values(self):
        return (self[k] for k in sorted(self.keys()))
