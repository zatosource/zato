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
from zato.common.odb.query import query_wrapper
from zato.common.util.search import SearchResults as _SearchResults
from zato.common.util.sql import search as util_search
from zato.server.service import Service
from zato.sso.odb.query import _user_basic_columns

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
            asc('display_name'),
            asc('username'),
            asc('sign_up_time'),
            asc('user_id'),
        )

# ################################################################################################################################

class SSOSearch(object):
    """ SSO search functions, constants and defaults.
    """
    def __init__(self):
        self.columns = []
        self.order_by = OrderBy()

# ################################################################################################################################

    def set_up(self):
        for column in _user_basic_columns:
            self.columns.append(getattr(SSOUser, column.name))

# ################################################################################################################################

    @query_wrapper
    def sql_search_func(self, session, ignored_cluster_id, order_by, needs_columns=False):
        return session.query(*self.columns).\
               order_by(*order_by)

# ################################################################################################################################

    def _get_order_by(self, order_by):
        """ Constructs an ORDER BY clause for the user search query.
        """
        out = []

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
                out.append(func(column))

        return out

# ################################################################################################################################

    def search(self, session, config):
        """ Looks up users with the configuration given on input.
        """
        # Build the order by list, validating the input first to make sure
        # only explicitly allowed columns and sort directions are used.

        order_by = config.get('order_by')
        order_by = self._get_order_by(order_by) if order_by else self.order_by.default

        return util_search(self.sql_search_func, config, [], session, None, order_by, False)

# ################################################################################################################################

sso_search = SSOSearch()
sso_search.set_up()

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
        password = '5c5Apw67534s55ukR_EZSVyH3DKr2ajNaa'
        session = self.sso.user.login(username, password, 'CRM', '127.0.0.1', 'my-user-agent', False, False)

        # Request metadata
        current_ust = session.ust
        current_app = 'CRM'
        remote_addr = '127.0.0.1'

        data = {}
        sql_search(self.sso.user, data, current_ust, current_app, remote_addr)

# ################################################################################################################################
