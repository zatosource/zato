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

class SSOSearch(object):
    """ SSO search functions, constants and defaults.
    """
    def __init__(self):
        self.columns = []
        self.order_by = self.OrderBy()

# ################################################################################################################################


    def set_up(self):
        for column in _user_basic_columns:
            self.columns.append(getattr(SSOUser, column.name))

# ################################################################################################################################

    class OrderBy(object):
        """ Defaults for the SQL ORDER BY clause.
        """
        def __init__(self):
            self.asc = 'asc'
            self.desc = 'desc'

            # All ORDER BY directions allowed
            self.dir_allowed = set((self.asc, self.desc))

            # All columns that results may be ordered by
            self.columns_allowed = set(('display_name', 'username', 'sign_up_time', 'user_id'))

            # How results will be sorted if no user-defined order is given
            self.default = (
                {'display_name': self.asc},
                {'username': self.asc},
                {'sign_up_time': self.asc},
                {'user_id': self.asc},
            )

# ################################################################################################################################

    @query_wrapper
    def sql_search_func(self, session, ignored_cluster_id, order_by, needs_columns=False):
        return session.query(*Search.columns).\
               order_by(*order_by)

# ################################################################################################################################

    def search(self, session, config):
        """ Looks up users with the configuration given on input.
        """
        # Build the order by list, validating the input first to make sure
        # only explicitly allowed columns and sort directions are used.

        order_by = config.get('order_by')
        order_by = order_by if order_by else self.order_by.default
        _order_by = []

        for item in order_by:
            items = item.items()
            if len(items) != 1 or len(items[0]) != 2:
                raise ValueError('Invalid order_by config `{}`'.format(items))
            else:
                column, dir = items[0]

                if column not in self.order_by.columns_allowed:
                    raise ValueError('Invalid order_by column `{}`'.format(column))

                if dir not in self.order_by.dir_allowed:
                    raise ValueError('Invalid order_by dir `{}`'.format(dir))

                # Columns and directions are valid, we can construct the ORDER BY clause now

                func = asc if dir == self.order_by.asc else desc
                _order_by.append(func(column))

        return util_search(self.sql_search_func, config, [], session, None, _order_by)

# ################################################################################################################################

sso_search = SSOSearch()
sso_search.set_up()

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

def sql_search(self, data, current_ust, current_app, remote_addr):
    """ Looks up users by specific search criteria from the 'data' dictionary.
    Must be called with a UST belonging to a super-user.
    """
    current_session = self._get_current_session(current_ust, current_app, remote_addr, needs_super_user=True)

    config = {
        'paginate': True,
        'page_size': 33,
    }

    with closing(self.odb_session_func()) as session:
        out = sso_search.search(session, config)

        print()
        print(out.num_pages)
        print(out.total)
        print()

# ################################################################################################################################

class MyService(Service):
    def handle(self):

        username = 'admin1'
        password = '****'
        session = self.sso.user.login(username, password, 'CRM', '127.0.0.1', 'my-user-agent', False, False)

        # Request metadata
        current_ust = session.ust
        current_app = 'CRM'
        remote_addr = '127.0.0.1'

        data = {}
        sql_search(self.sso.user, data, current_ust, current_app, remote_addr)

# ################################################################################################################################
