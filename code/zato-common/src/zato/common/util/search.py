# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Callable

    Callable = Callable

# ################################################################################################################################
# ################################################################################################################################

_search_attrs = 'num_pages', 'cur_page', 'prev_page', 'next_page', 'has_prev_page', 'has_next_page', 'page_size', 'total'

# ################################################################################################################################
# ################################################################################################################################

class SearchResults(object):
    def __init__(self, q, result, columns, total):
        # type: (object, object, object, int) -> None
        self.q = q
        self.result = result
        self.total = total
        self.columns = columns # type: list
        self.num_pages = 0
        self.cur_page = 0
        self.prev_page = 0
        self.next_page = 0
        self.has_prev_page = False
        self.has_next_page = False
        self.page_size = None # type: int

# ################################################################################################################################

    def __iter__(self):
        return iter(self.result)

# ################################################################################################################################

    def __repr__(self):
        # To avoice circular imports - this is OK because we very rarely repr(self) anyway
        from zato.common.util.api import make_repr
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

    @staticmethod
    def from_list(
        data_list, # type: list
        cur_page,  # type: int
        page_size, # type: int
        needs_sort=False,   # type: bool
        post_process_func=None, # type: Callable
        sort_key=None,     # type: object
        needs_reverse=True # type: bool
        ):

        cur_page = cur_page - 1 if cur_page else 0 # We index lists from 0

        # Set it here because later on it may be shortened to the page_size of elements
        total = len(data_list)

        # If we get here, we must have collected some data at all
        if data_list:

            # We need to sort the output ..
            if needs_sort:
                data_list.sort(key=sort_key, reverse=needs_reverse)

            # .. the output may be already sorted but we may perhaps need to reverse it.
            else:
                if needs_reverse:
                    data_list.reverse()

            start = cur_page * page_size
            end = start + page_size
            data_list = data_list[start:end]

        if post_process_func:
            post_process_func(data_list)

        search_results = SearchResults(None, data_list, None, total)
        search_results.set_data(cur_page, page_size)

        return search_results

# ################################################################################################################################

    def to_dict(self, _search_attrs=_search_attrs):
        out = {}
        out['result'] = self.result
        for name in _search_attrs:
            out[name] = getattr(self, name, None)
        return out

# ################################################################################################################################
# ################################################################################################################################
