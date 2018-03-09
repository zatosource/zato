# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import SEARCH

# ################################################################################################################################

_default_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value
_max_page_size = _default_page_size * 5

# ################################################################################################################################

def search(search_func, config, filter_by, session=None, cluster_id=None, *args, **kwargs):
    """ Adds search criteria to an SQLAlchemy query based on current search configuration.
    """
    # No pagination requested at all
    if not config.get('paginate'):
        return search_func(session, cluster_id, *args)

    try:
        cur_page = int(config.get('cur_page', 1))
    except(ValueError, TypeError):
        cur_page = 1

    try:
        page_size = min(int(config.get('page_size', _default_page_size)), _max_page_size)
    except(ValueError, TypeError):
        page_size = _default_page_size

    # We need to substract 1 because externally our API exposes human-readable numbers,
    # i.e. starting from 1, not 0, but internally the database needs 0-based slices.
    if cur_page > 0:
        cur_page -= 1

    kwargs = {
        'cur_page': cur_page,
        'page_size': page_size,
        'filter_by': filter_by,
        'where': kwargs.get('where')
    }

    query = config.get('query')
    if query:
        query = query.strip().split()
        if query:
            kwargs['query'] = query

    result = search_func(session, cluster_id, *args, **kwargs)
    num_pages, rest = divmod(result.total, page_size)

    # Apparently there are some results in rest that did not fit a full page
    if rest:
        num_pages += 1

    result.num_pages = num_pages
    result.cur_page = cur_page + 1 # Adding 1 because, again, the external API is 1-indexed
    result.prev_page = result.cur_page - 1 if result.cur_page > 1 else None
    result.next_page = result.cur_page + 1 if result.cur_page < result.num_pages else None
    result.has_prev_page = result.prev_page >= 1
    result.has_next_page = bool(result.next_page and result.next_page <= result.num_pages) or False
    result.page_size = page_size

    return result

# ################################################################################################################################
