# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import warnings
from contextlib import closing
from copy import deepcopy
from functools import lru_cache
from io import StringIO
from logging import DEBUG, getLogger
from threading import RLock
from time import time

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import MS_SQL, NotGiven, SECRET_SHADOW, UNITTEST
from zato.common.exception import Inactive
from zato.common.odb.ping import get_ping_query
from zato.common.odb.testing import UnittestEngine
from zato.common.util.api import get_component_name, get_engine_url, new_cid, parse_extra_into_dict, spawn_greenlet

# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session as SASession
    from zato.common.crypto.api import CryptoManager
    from zato.common.typing_ import any_, callable_, strdict, strdictnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

unittest_fs_sql_config = {
    UNITTEST.SQL_ENGINE: {
        'ping_query': 'SELECT 1+1'
    }
}

# ################################################################################################################################

@lru_cache(maxsize=1)
def _get_sa():
    """ Returns a namespace object holding all SQLAlchemy names, loaded once on first call.
    """
    from sqlalchemy import and_, create_engine, event, select
    from sqlalchemy.exc import IntegrityError, OperationalError
    from sqlalchemy.orm import sessionmaker, scoped_session
    from sqlalchemy.orm.query import Query
    from sqlalchemy.pool import NullPool
    from sqlalchemy.sql.expression import true
    from sqlalchemy.sql.type_api import TypeEngine
    from sqlalchemy import exc as _sa_exc

    warnings.filterwarnings('ignore', category=_sa_exc.SAWarning, message='.*')

    from zato.common.mssql_direct import MSSQLDirectAPI, SimpleSession

    class WritableTupleQuery(Query):

        def __iter__(self):
            out = super(WritableTupleQuery, self).__iter__()
            columns_desc = self.column_descriptions
            first_type = columns_desc[0]['type']
            len_columns_desc = len(columns_desc)
            if len_columns_desc == 1 and isinstance(first_type, TypeEngine):
                return out
            elif len_columns_desc > 1:
                return (SQLRow(elem) for elem in out)
            else:
                return out

    class _SA:
        pass

    sa = _SA()
    sa.and_ = and_
    sa.create_engine = create_engine
    sa.event = event
    sa.select = select
    sa.IntegrityError = IntegrityError
    sa.OperationalError = OperationalError
    sa.sessionmaker = sessionmaker
    sa.scoped_session = scoped_session
    sa.NullPool = NullPool
    sa.true = true
    sa.TypeEngine = TypeEngine
    sa.WritableTupleQuery = WritableTupleQuery
    sa.MSSQLDirectAPI = MSSQLDirectAPI
    sa.SimpleSession = SimpleSession

    return sa


# ################################################################################################################################
# ################################################################################################################################

# Based on https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/WriteableTuple

class SQLRow:

    def __init__(self, elem):
        object.__setattr__(self, '_elem', elem)

# ################################################################################################################################

    def __getattr__(self, key):
        return getattr(self._elem, key)

# ################################################################################################################################

    def __getitem__(self, idx):
        return self._elem.__getitem__(idx)

# ################################################################################################################################

    def __setitem__(self, idx, value):
        return self._elem.__setitem__(idx, value)

# ################################################################################################################################

    def __nonzero__(self):
        return bool(self._elem)

# ################################################################################################################################

    def __repr__(self):
        return '<SQLRow at {}>'.format(hex(id(self)))

# ################################################################################################################################

    def get_value(self) -> 'commondict':
        return self._elem._asdict()

# For backward compatibility
WritableKeyedTuple = SQLRow

# ################################################################################################################################
# ################################################################################################################################

class SessionWrapper:
    """ Wraps an SQLAlchemy session.
    """
    _Session: 'SASession'

    def __init__(self) -> 'None':
        self.session_initialized = False
        self.pool = None      # type: SQLConnectionPool
        self.config = {}    # type: dict
        self.is_sqlite = False # type: bool
        self.is_oracle_db = False # type: bool
        self.logger = logging.getLogger(self.__class__.__name__)

    def init_session(self, *args, **kwargs):
        _ = spawn_greenlet(self._init_session, *args, **kwargs)

    def _init_session(self, name, config, pool, use_scoped_session=True):
        # type: (str, dict, SQLConnectionPool, bool)  # type: ignore
        sa = _get_sa()
        self.config = config
        self.fs_sql_config = config['fs_sql_config']
        self.pool = pool

        is_ms_sql_direct = config['engine'] == MS_SQL.ZATO_DIRECT

        if is_ms_sql_direct:
            self._Session = sa.SimpleSession(self.pool.engine) # type: ignore
        else:
            if use_scoped_session:
                self._Session = sa.scoped_session(sa.sessionmaker(bind=self.pool.engine, query_cls=sa.WritableTupleQuery))
            else:
                self._Session = sa.sessionmaker(bind=self.pool.engine, query_cls=sa.WritableTupleQuery)
            self._session = self._Session() # type: ignore

        self.session_initialized = True
        self.is_sqlite = self.pool.engine and self.pool.engine.name == 'sqlite'
        self.is_oracle_db = self.pool.engine and self.pool.engine.name.startswith('oracle')

    def execute(self, query:'str', params:'strdictnone'=None) -> 'any_':

        with closing(self.session()) as session:
            result = session.execute(query, params)
            column_names = result.keys() # type: ignore
            result = [dict(zip(column_names, row)) for row in result] # type: ignore
            return result

    def one(self, *args:'any_', **kwargs:'any_') -> 'any_':
        result = self.execute(*args, **kwargs)

        if not result:
            needs_one = kwargs.get('zato_needs_one') or False
            if needs_one:
                raise Exception('Query returned no rows')
            else:
                return None # Explicitly return None
        else:
            len_result = len(result)
            if len_result > 1:
                raise Exception(f'Query returned multiple rows (len={len_result})')
            else:
                return result[0]

    def one_or_none(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self.one(*args, zato_needs_one=True, **kwargs)

    def callproc(self, proc_name:'str', params:'anylistnone'=None) -> 'any_':

        if not self.is_oracle_db:
            raise Exception('This method works with Oracle DB only.')

        params = params or []

        with closing(self.session()) as session:

            conn = session.connection().connection
            cursor = conn.cursor()

            _params = [elem.bind(cursor) for elem in params]
            cursor.callproc(proc_name, _params)

            result = []
            for idx, item in enumerate(_params):
                input_item = params[idx]
                if input_item.is_out:
                    result.append(item.getvalue())

            return result

    def session(self) -> 'SASession':
        return self._Session() # type: ignore

    def close(self):
        self._session.close()

# ################################################################################################################################
# ################################################################################################################################

class SQLConnectionPool:
    """ A pool of SQL connections wrapping an SQLAlchemy engine.
    """
    def __init__(self, name:'str', config:'strdict', config_no_sensitive:'strdict', should_init:'bool'=True):
        self.name = name
        self.config = config
        self.config_no_sensitive = config_no_sensitive

        self.logger = getLogger(self.__class__.__name__)
        self.has_debug = self.logger.isEnabledFor(DEBUG)

        self.engine = None
        self.engine_name:'str' = config['engine'] # self.engine.name is 'mysql' while 'self.engine_name' is mysql+pymysql

        self._is_oracle_db = self.engine_name.startswith('oracle')

        if should_init: # type: ignore
            self.init()

    def init(self):
        sa = _get_sa()

        # Check if Oracle DB connections are enabled
        if self._is_oracle_db:
            if not (key := os.environ.get('Zato_License_Key')): # type: ignore
                self.logger.warning('Zato license key not found. Oracle DB connections will not be available.')
                return

        _extra = {
            'pool_pre_ping': True, # Make sure SQLAlchemy 1.2+ can refresh connections on transient errors
        }

        # MySQL only
        if self.engine_name.startswith('mysql'):
            _extra['pool_recycle'] = 600 # type: ignore

        # Postgres-only
        elif self.engine_name.startswith('postgres'):
            _extra['connect_args'] = {'application_name': get_component_name()} # type: ignore

        # Oracle DB-only
        elif self.engine_name.startswith('oracle'):
            self.engine_name = 'oracle+oracledb'

        extra = self.config.get('extra') # Optional, hence .get

        if extra and isinstance(extra, str) and extra.startswith('\\x'):
            try:
                extra = bytes.fromhex(extra.replace('\\x', '')).decode('utf-8')
            except Exception as e:
                self.logger.error('Failed to decode hex-encoded extra parameter: %s', e)

        _extra.update(parse_extra_into_dict(extra)) # type: ignore

        # SQLite has no pools
        if self.engine_name != 'sqlite':
            _extra['pool_size'] = int(self.config.get('pool_size', 1)) # type: ignore
            if _extra['pool_size'] == 0:
                _extra['poolclass'] = sa.NullPool # type: ignore

        engine_url = get_engine_url(self.config)

        if engine_url.startswith('oracle://'):
            engine_url = engine_url.replace('oracle://', 'oracle+oracledb://')

        try:
            self.engine = self._create_engine(engine_url, self.config, _extra)
        except Exception as e:
            self.logger.warning('Could not create SQL connection `%s`, e:`%s`', self.name, e.args[0])

        if self.engine and (not self._is_unittest_engine(engine_url)) and self._is_sa_engine(engine_url):
            sa.event.listen(self.engine, 'checkin', self.on_checkin)
            sa.event.listen(self.engine, 'checkout', self.on_checkout)
            sa.event.listen(self.engine, 'connect', self.on_connect)
            sa.event.listen(self.engine, 'first_connect', self.on_first_connect)

        self.checkins = 0
        self.checkouts = 0

        self.checkins = 0
        self.checkouts = 0

# ################################################################################################################################

    def __str__(self):
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

# ################################################################################################################################

    __repr__ = __str__

# ################################################################################################################################

    def _is_oracle_engine(self, engine_url:'str') -> 'bool':
        return engine_url.startswith('oracle')

# ################################################################################################################################

    def _is_sa_engine(self, engine_url:'str') -> 'bool':
        return 'zato+mssql1' not in engine_url

# ################################################################################################################################

    def _is_unittest_engine(self, engine_url:'str') -> 'bool':
        return 'zato+unittest' in engine_url

# ################################################################################################################################

    def _create_unittest_engine(self, engine_url, config):
        return UnittestEngine(engine_url, config)

# ################################################################################################################################

    def _create_oracle_engine(self, engine_url, config):
        sa = _get_sa()
        return sa.create_engine(
            'oracle://:@',
            connect_args={
                'user': 'system',
                'password': 'new_password',
                'host': 'localhost',
                'port': '1521',
                'service_name': 'FREEPDB1',
            }
        )

# ################################################################################################################################

    def _create_engine(self, engine_url, config, extra):

        if self._is_unittest_engine(engine_url):
            return self._create_unittest_engine(engine_url, config)

        elif self._is_oracle_engine(engine_url):
            return self._create_oracle_engine(engine_url, config)

        elif self._is_sa_engine(engine_url):
            sa = _get_sa()
            return sa.create_engine(engine_url, **extra)

        else:
            sa = _get_sa()
            connect_kwargs = {
                'dsn': config['host'],
                'port': config['port'],
                'database': config['db_name'],
                'user': config['username'],
                'password': config['password'],
                'login_timeout': 3,
                'as_dict': True,
            }

            for name in MS_SQL.EXTRA_KWARGS:
                value = extra.get(name, NotGiven)
                if value is not NotGiven:
                    connect_kwargs[name] = value

            return sa.MSSQLDirectAPI(config['name'], config['pool_size'], connect_kwargs, extra)

# ################################################################################################################################

    def on_checkin(self, dbapi_conn, conn_record):
        if self.has_debug:
            self.logger.debug('Checked in dbapi_conn:%s, conn_record:%s', dbapi_conn, conn_record)
        self.checkins += 1

# ################################################################################################################################

    def on_checkout(self, dbapi_conn, conn_record, conn_proxy):
        if self.has_debug:
            self.logger.debug('Checked out dbapi_conn:%s, conn_record:%s, conn_proxy:%s',
                dbapi_conn, conn_record, conn_proxy)

        self.checkouts += 1
        self.logger.debug('co-cin-diff %d-%d-%d', self.checkouts, self.checkins, self.checkouts - self.checkins)

# ################################################################################################################################

    def on_connect(self, dbapi_conn, conn_record):
        if self.has_debug:
            self.logger.debug('Connect dbapi_conn:%s, conn_record:%s', dbapi_conn, conn_record)

# ################################################################################################################################

    def on_first_connect(self, dbapi_conn, conn_record):
        if self.has_debug:
            self.logger.debug('First connect dbapi_conn:%s, conn_record:%s', dbapi_conn, conn_record)

# ################################################################################################################################

    def ping(self, fs_sql_config):
        """ Pings the SQL database and returns the response time, in milliseconds.
        """
        if not self.engine:
            return

        if hasattr(self.engine, 'ping'):
            func = self.engine.ping
            query = self.engine.ping_query
            args = []
        else:
            func = self.engine.connect().execute
            query = get_ping_query(fs_sql_config, self.config)
            args = [query]

        self.logger.debug('About to ping the SQL connection pool:`%s`, query:`%s`', self.config_no_sensitive, query)

        start_time = time()
        _ = func(*args)
        response_time = time() - start_time

        self.logger.debug('Ping OK, pool:`%s`, response_time:`%s` s', self.config_no_sensitive, response_time)

        return response_time

# ################################################################################################################################

    def _conn(self):
        """ Returns an SQLAlchemy connection object.
        """
        return self.engine.connect() # type: ignore

# ################################################################################################################################

    conn = property(fget=_conn, doc=_conn.__doc__)

# ################################################################################################################################

    def _impl(self):
        """ Returns the underlying connection's implementation, the SQLAlchemy engine.
        """
        return self.engine

# ################################################################################################################################

    impl = property(fget=_impl, doc=_impl.__doc__)

# ################################################################################################################################

class PoolStore:
    """ A main class for accessing all of the SQL connection pools. Each server
    thread has its own store.
    """
    def __init__(self, sql_conn_class=SQLConnectionPool):
        self.sql_conn_class = sql_conn_class
        self._lock = RLock()
        self.wrappers = {}
        self.logger = getLogger(self.__class__.__name__)

# ################################################################################################################################

    def __getitem__(self, name, enforce_is_active=True):
        """ Checks out the connection pool. If enforce_is_active is False,
        the pool's is_active flag will be ignored.
        """
        with self._lock:
            if enforce_is_active:
                wrapper = self.wrappers[name]
                if wrapper.config.get('is_active', True):
                    return wrapper
                raise Inactive(name)
            else:
                return self.wrappers[name]

# ################################################################################################################################

    get = __getitem__

# ################################################################################################################################

    def __setitem__(self, name, config):
        """ Stops a connection pool if it exists and replaces it with a new one
        using updated settings.
        """
        with self._lock:
            if name in self.wrappers:
                del self[name]

            config_no_sensitive = {}

            for key in config:
                if key != 'callback_func':
                    config_no_sensitive[key] = config[key]

            config_no_sensitive['password'] = SECRET_SHADOW
            pool = self.sql_conn_class(name, config, config_no_sensitive)

            wrapper = SessionWrapper()
            wrapper.init_session(name, config, pool)

            self.wrappers[name] = wrapper

    set_item = __setitem__

# ################################################################################################################################

    def add_unittest_item(self, name, fs_sql_config=unittest_fs_sql_config):
        self.set_item(name, {
            'password': 'password.{}'.format(new_cid),
            'engine': UNITTEST.SQL_ENGINE,
            'fs_sql_config': fs_sql_config,
            'is_active': True,
        })

# ################################################################################################################################

    def __delitem__(self, name):
        """ Stops a pool and deletes it from the store.
        """
        with self._lock:
            engine = self.wrappers[name].pool.engine
            if engine:
                engine.dispose()
            del self.wrappers[name]

# ################################################################################################################################

    def __str__(self):
        out = StringIO()
        _ = out.write('<{} at {} wrappers:['.format(self.__class__.__name__, hex(id(self))))
        _ = out.write(', '.join(sorted(self.wrappers.keys())))
        _ = out.write(']>')
        return out.getvalue()

# ################################################################################################################################

    __repr__ = __str__

# ################################################################################################################################

    def change_password(self, name, password):
        """ Updates the password which means recreating the pool using the new
        password.
        """
        with self._lock:
            # Do not check if the connection is active when changing the password,
            # sometimes it is desirable to change it even if it is Inactive.
            item = self.get(name, enforce_is_active=False)
            if item.pool.engine:
                item.pool.engine.dispose()
                config = deepcopy(self.wrappers[name].pool.config)
                config['password'] = password
                self[name] = config
            else:
                self.logger.warning('No engine found for %s (change password)', name)

# ################################################################################################################################

    def cleanup_on_stop(self):
        """ Invoked when the server is stopping.
        """
        with self._lock:
            for _ignored_name, wrapper in self.wrappers.items():
                if wrapper.pool:
                    if wrapper.pool.engine:
                        wrapper.pool.engine.dispose()

# ################################################################################################################################

class ODBManager(SessionWrapper):
    """ Manages connections to the Operational Database.
    """
    parallel_server: 'ParallelServer'
    well_known_data:'str'
    token:'str'
    crypto_manager:'CryptoManager'
    server_id:'int'
    server_name:'str'
    cluster_id:'int'
    pool:'SQLConnectionPool'
    decrypt_func:'callable_'

# ################################################################################################################################

    def __init__(self) -> 'None':
        super().__init__()

# ################################################################################################################################
