# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.server.store import BaseAPI, BaseStore

logger = getLogger(__name__)

class CassandraQueryAPI(BaseAPI):
    """ API to query Cassandra through prepared statements.
    """

class CassandraQueryStore(BaseStore):
    """ Stores Cassandra prepared statements.
    """
    def create_impl(self, config, config_no_sensitive, **extra):
        conn = extra['def_'].conn
        if not conn:
            logger.warning('Could not create a Cassandra query `%s`, conn is None`', config_no_sensitive)
        else:
            return conn.prepare(config.value)

    def update_by_def(self, del_name, new_def):
        """ Invoked when the underlying definition got updated.
        Iterates through all the queries that were using it and updates them accordingly.
        """
        with self.lock:
            for value in self.items.values():
                if value.config.def_name == del_name:
                    self._edit(value.config.name, value.config, def_=new_def)
