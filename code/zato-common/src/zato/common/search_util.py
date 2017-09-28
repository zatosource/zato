# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

class SearchResults(object):
    def __init__(self, q, result, columns, total):
        self.q = q
        self.result = result
        self.total = total
        self.columns = columns
        self.num_pages = 0
        self.cur_page = 0
        self.prev_page = 0
        self.next_page = 0
        self.has_prev_page = False
        self.has_next_page = False

    def __iter__(self):
        return iter(self.result)

    def __repr__(self):
        # To avoice circular imports - this is OK because we very rarely repr(self) anyway
        from zato.common.util import make_repr
        return make_repr(self)
