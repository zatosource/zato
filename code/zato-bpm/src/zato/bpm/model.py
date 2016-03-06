# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent.lock import RLock

# Zato
from zato.orm import label as _label
from zato.orm.sql import Group, Item, SubGroup

# ################################################################################################################################

class Base(object):

    # Defaults attributes for all subclasses
    __slots__ = ('engine', 'cluster_id', 'group_cache', 'sub_group_cache', 'ident', 'data', '_lock')

    # Will be overwritte by subclasses
    label = ''

    # Default to public so that users have less to type
    is_internal = False

    def __init__(self, engine, cluster_id, group_cache, sub_group_cache, ident=None, data=None):
        self.engine = engine
        self.cluster_id = cluster_id
        self.group_cache = group_cache
        self.sub_group_cache = sub_group_cache
        self.ident = ident
        self.data = data
        self._lock = RLock()

    def get(self, *args):
        print(self.label % args)

    def commit(self):

        item = Item()
        item.name = self.label % self.ident
        item.is_internal = self.is_internal
        item.cluster_id = self.cluster_id
        print(11, self.engine, self.ident, self.data)

# ################################################################################################################################

class _ProcBase(Base):

    # No new slots
    __slots__ = []

    is_internal = True
    group = _label.group.conf.process
    sub_group = _label.sub_group.conf.process_bst

# ################################################################################################################################

class ProcHistory(_ProcBase):

    # No new slots
    __slots__ = []

    label = _label.item.process_bst_inst_history

# ################################################################################################################################

class ProcCurrent(_ProcBase):

    # No new slots
    __slots__ = []

    label = _label.item.process_bst_inst_current

# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import os

    # SQLAlchemy
    from sqlalchemy import create_engine

    # Zato
    from zato.common.odb import util as odb_util
    from zato.common.odb.model import Cluster

    def get_session(engine):
        session = sessionmaker() # noqa
        session.configure(bind=engine)
        return session()

    url = 'sqlite://{}'.format(os.path.expanduser('~/env/qs-1/zato.db'))
    engine = create_engine(url)

    print(engine)

    cluster_id = 1

    c = session.query(Cluster).\
        filter(Cluster.id==args.cluster_id).\
        one()

    g = Group()
    g.name = _label.group.conf.process
    g.is_internal = True
    g.cluster_id = c.id

    pc = ProcCurrent(engine, cluster_id)
    pc.ident = 'abc', 'def'
    pc.data = '123'
    pc.commit()

# ################################################################################################################################
