# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import datetime
from contextlib import closing
from logging import getLogger

# gevent
import gevent

# Zato
from zato.common.odb.model import KVData

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class JWTCache:
    """ A previous-generation, JWT-only, cache that uses ODB.
    """

# ################################################################################################################################

    def __init__(self, odb, miss_fallback=False, cluster_id=None):
        self.odb = odb
        self.miss_fallback = miss_fallback
        self.cluster_id = cluster_id

# ################################################################################################################################

    def _get_odb_key(self, key):
        return 'cluster_id:{}/{}'.format(self.cluster_id, key) if self.cluster_id else key

# ################################################################################################################################

    def _odb_put(self, key, value, ttl):
        key = self._get_odb_key(key)

        if isinstance(key, unicode):
            key = key.encode('utf8')

        if isinstance(value, unicode):
            value = value.encode('utf8')

        with closing(self.odb.session()) as session:
            try:
                item = session.query(KVData).filter_by(key=key).first()

                if not item:
                    item = KVData()

                now = datetime.datetime.utcnow()

                item.key = key
                item.value = value
                item.creation_time = now
                item.expiry_time = now + datetime.timedelta(seconds=ttl)

                session.add(item)
                session.commit()

            except Exception:
                logger.exception('Unable to put key/value `%r` `%r` (%s %s) into ODB', key, value, type(key), type(value))
                session.rollback()

                raise

# ################################################################################################################################

    def _odb_get(self, key):
        with closing(self.odb.session()) as session:
            return session.query(KVData).filter_by(key=self._get_odb_key(key)).first()

# ################################################################################################################################

    def put(self, key, value, ttl=None, is_async=True):
        """Put key/value into ODB. If is_async is False, we join the greenlets until they are done.
        otherwise, we do not wait for them to finish.
        """
        greenlets = [
            gevent.spawn(self._odb_put, key, value, ttl)
        ]

        if not is_async:
            gevent.joinall(greenlets)

# ################################################################################################################################

    def get(self, key):
        return self._odb_get(key)

# ################################################################################################################################

    def delete(self, key):

        # Delete from ODB
        key = self._get_odb_key(key)

        with closing(self.odb.session()) as session:
            item = session.query(KVData).filter_by(key=key).first()

            if item:
                session.delete(item)
                session.commit()

# ################################################################################################################################
