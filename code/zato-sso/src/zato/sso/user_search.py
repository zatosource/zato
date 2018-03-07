# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from functools import wraps
from inspect import getargspec
from logging import getLogger
from random import randint

# SQALchemy
from sqlalchemy import asc, desc, func

# Zato
from zato.common.odb.model import SSOUser
from zato.common.util.search import SearchResults as _SearchResults
from zato.common.util.sql import search as util_search
from zato.server.service import Service
from zato.sso.odb.query import _user_basic_columns

# ################################################################################################################################

class search:
    columns = []
    asc = 'asc'
    desc = 'desc'

    class order_by:

        @staticmethod
        def default():
            return (
                {'display_name': search.asc},
                {'username': search.asc},
                {'sign_up_time': search.asc},
                {'user_id': search.asc},
            )

for column in _user_basic_columns:
    search.columns.append(getattr(SSOUser, column.name))

# ################################################################################################################################

_no_page_limit = 2 ** 24 # ~16.7 million results, tops

# ################################################################################################################################

def count(session, q):
    _q = q.statement.with_only_columns([func.count()]).order_by(None)
    return session.execute(_q).scalar()

# ################################################################################################################################

class _SearchWrapper(object):
    """ Wraps results in pagination and/or filters out objects by their name or other attributes.
    """
    def __init__(self, q, default_page_size=_no_page_limit, **config):

        # Apply WHERE conditions
        complex_filter = config.get('complex_filter')
        if complex_filter:
            q = q.filter(complex_filter)
        else:
            for filter_by in config.get('filter_by', []):
                for criterion in config.get('query', []):
                    q = q.filter(filter_by.contains(criterion))

        # Total number of results
        total_q = q.statement.with_only_columns([func.count()]).order_by(None)
        self.total = q.session.execute(total_q).scalar()

        # Pagination
        page_size = config.get('page_size', default_page_size)
        cur_page = config.get('cur_page', 0)

        slice_from = cur_page * page_size
        slice_to = slice_from + page_size

        self.q = q.slice(slice_from, slice_to)

# ################################################################################################################################

def query_wrapper(func):
    """ A decorator for queries which works out whether a given query function should return the result only
    or a column list retrieved in addition to the result. This is useful because some callers prefer the former
    and some need the latter. Also, paginates the results if requested to by the caller.
    """
    @wraps(func)
    def inner(*args, **kwargs):

        # Each query function will have a keyword argument 'needs_columns' as the last one
        # in its definition, e.g. needs_columns=False.
        func_spec = getargspec(func)
        needs_columns = func_spec.defaults[-1]

        tool = _SearchWrapper(func(*args), **kwargs)
        result = _SearchResults(tool.q, tool.q.all(), tool.q.statement.columns, tool.total)

        if needs_columns:
            return result, result.columns

        return result

    return inner

# ################################################################################################################################

@query_wrapper
def search_func(session, cluster_id, order_by, needs_columns=False):
    print(333, session, cluster_id, order_by, needs_columns)
    return session.query(*search.columns).\
           order_by('id')

# ################################################################################################################################

def sql_search(self, data, current_ust, current_app, remote_addr):
    """ Looks up users by specific search criteria from the 'data' dictionary.
    Must be called with a UST belonging to a super-user.
    """
    current_session = self._get_current_session(current_ust, current_app, remote_addr, needs_super_user=True)

    config = {
        'paginate': True,
        'page_size': 33,
    }

    order_by = search.order_by.default()

    with closing(self.odb_session_func()) as session:
        out = util_search(search_func, config, [], session, None, order_by)

        print()
        print(out.num_pages)
        print(out.total)
        print()

# ################################################################################################################################

class MyService(Service):
    def handle(self):

        username = 'admin1'
        password = '******'
        session = self.sso.user.login(username, password, 'CRM', '127.0.0.1', 'my-user-agent', False, False)

        # Request metadata
        current_ust = session.ust
        current_app = 'CRM'
        remote_addr = '127.0.0.1'

        data = {}
        sql_search(self.sso.user, data, current_ust, current_app, remote_addr)

# ################################################################################################################################
