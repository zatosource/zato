# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta
from logging import getLogger
from random import randint

# Zato
from zato.common.odb.model import SSOUser
from zato.common.odb.query import query_wrapper
from zato.common.util.sql import search as util_search
from zato.server.service import Service
from zato.sso.odb.query import _user_basic_columns

# ################################################################################################################################

_user_search_columns = []
for column in _user_basic_columns:
    _user_search_columns.append(getattr(SSOUser, column.name))

# ################################################################################################################################

@query_wrapper
def search_func(session, ignored_cluster_id, needs_columns=False):
    return session.query(*_user_search_columns).\
           order_by('id')

# ################################################################################################################################

def sql_search(self, data, current_ust, current_app, remote_addr):
    """ Looks up users by specific search criteria from the 'data' dictionary.
    Must be called with a UST belonging to a super-user.
    """
    current_session = self._get_current_session(current_ust, current_app, remote_addr, needs_super_user=True)

    with closing(self.odb_session_func()) as session:
        out = util_search(search_func, {}, None, session, None)

        print()
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
