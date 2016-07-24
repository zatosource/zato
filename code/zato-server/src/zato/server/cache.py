# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import datetime
from contextlib import closing
from logging import getLogger

# gevent
import gevent

# Zato
from zato.common.odb.model import KVCache

logger = getLogger(__name__)

class RobustCache(object):
    """Robust Cache that uses KVDB as a first option but keeps ODB as a failsafe alternative."""

    def __init__(self, kvdb, odb, miss_fallback=False):
        self.kvdb = kvdb
        self.odb = odb
        self.miss_fallback = miss_fallback

    def _kvdb_put(self, key, value, ttl):
        try:
            self.kvdb.conn.set(key, value)
            if ttl:
                self.kvdb.conn.expire(key, ttl)

        except Exception:
            logger.exception('KVDB Exception while putting %s.', key)

    def _odb_put(self, key, value, ttl):
        with closing(self.odb.session()) as session:
            try:
                kvcache = session.query(KVCache).filter_by(key=key).first()

                if not kvcache:
                    kvcache = KVCache()

                now = datetime.datetime.utcnow()

                kvcache.key = key
                kvcache.value = value
                kvcache.insert_time = now
                kvcache.expire_time = now + datetime.timedelta(seconds=ttl)

                session.add(kvcache)
                session.commit()

            except Exception:
                logger.exception('Unable to put key %s into ODB', key)
                session.rollback()

                raise

    def _odb_get(self, key):
        with closing(self.odb.session()) as session:
            return session.query(KVCache).filter_by(key=key).first()

    def put(self, key, value, ttl=None, async=True):
        """Put key/value into both KVDB and ODB, in parallel.

        if async is False, we join the greenlets until they are done.
        otherwise, we do not wait for them to finish.
        """
        greenlets = [
            gevent.spawn(self._kvdb_put, key, value, ttl),
            gevent.spawn(self._odb_put, key, value, ttl)
        ]

        if not async:
            gevent.join(greenlets)

    def get(self, key):
        try:
            return self.kvdb.conn.get(key)

        except Exception:
            logger.exception('KVDB Exception while getting key %s. Falling back to ODB.', key)
            return self._odb_get(key)

        if self.miss_fallback:
            logger.warning('Key %s not found in KVDB. Falling back to ODB.', key)
            return self._odb_get(key)
