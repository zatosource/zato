# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class SessionWrapper(object):
    """ Wraps an SQLAlchemy session.
    """
    def __init__(self):
        self.session_initialized = False
        self.pool = None      # type: SQLConnectionPool
        self.config = None    # type: dict
        self.is_sqlite = None # type: bool
        self.logger = logging.getLogger(self.__class__.__name__)

    def init_session(self, *args, **kwargs):
        spawn_greenlet(self._init_session, *args, **kwargs)

    def _init_session(self, name, config, pool, use_scoped_session=True):
        # type: (str, dict, SQLConnectionPool, bool)
        self.config = config
        self.fs_sql_config = config['fs_sql_config']
        self.pool = pool

        try:
            self.pool.ping(self.fs_sql_config)
        except Exception:
            msg = 'Could not ping:`%s`, session will be left uninitialized, e:`%s`'
            self.logger.warn(msg, name, format_exc())
        else:
            if config['engine'] == MS_SQL.ZATO_DIRECT:
                self._Session = SimpleSession(self.pool.engine)
            else:
                if use_scoped_session:
                    self._Session = scoped_session(sessionmaker(bind=self.pool.engine, query_cls=WritableTupleQuery))
                else:
                    self._Session = sessionmaker(bind=self.pool.engine, query_cls=WritableTupleQuery)
                self._session = self._Session()

            self.session_initialized = True
            self.is_sqlite = self.pool.engine.name == 'sqlite'

    def session(self):
        return self._Session()

    def close(self):
        self._session.close()

# ################################################################################################################################
# ################################################################################################################################
