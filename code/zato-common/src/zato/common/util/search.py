# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

_search_attrs = 'num_pages', 'cur_page', 'prev_page', 'next_page', 'has_prev_page', 'has_next_page', 'page_size', 'total'

# ################################################################################################################################

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
        self.page_size = None

# ################################################################################################################################

    def __iter__(self):
        return iter(self.result)

# ################################################################################################################################

    def __repr__(self):
        # To avoice circular imports - this is OK because we very rarely repr(self) anyway
        from zato.common.util import make_repr
        return make_repr(self)

# ################################################################################################################################

    def set_data(self, cur_page, page_size):

        num_pages, rest = divmod(self.total, page_size)

        # Apparently there are some results in rest that did not fit a full page
        if rest:
            num_pages += 1

        self.num_pages = num_pages
        self.cur_page = cur_page + 1 # Adding 1 because, again, the external API is 1-indexed
        self.prev_page = self.cur_page - 1 if self.cur_page > 1 else 0
        self.next_page = self.cur_page + 1 if self.cur_page < self.num_pages else None
        self.has_prev_page = self.prev_page >= 1
        self.has_next_page = bool(self.next_page and self.next_page <= self.num_pages) or False
        self.page_size = page_size

# ################################################################################################################################

    def to_dict(self, _search_attrs=_search_attrs):
        out = {}
        for name in _search_attrs:
            out[name] = getattr(self, name, None)
        return out

# ################################################################################################################################
