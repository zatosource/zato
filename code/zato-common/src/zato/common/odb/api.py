# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from contextlib import closing
from copy import deepcopy
from datetime import datetime
from io import StringIO
from logging import DEBUG, getLogger
from threading import RLock
from time import time

# Bunch
from bunch import Bunch, bunchify

# SQLAlchemy
from sqlalchemy import and_, create_engine, event, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.query import Query
from sqlalchemy.pool import NullPool
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.type_api import TypeEngine

# Zato
from zato.common.api import DEPLOYMENT_STATUS, GENERIC, HTTP_SOAP, MS_SQL, NotGiven, PUBSUB, SEC_DEF_TYPE, SECRET_SHADOW, \
     SERVER_UP_STATUS, UNITTEST, ZATO_NONE, ZATO_ODB_POOL_NAME
from zato.common.exception import Inactive
from zato.common.mssql_direct import MSSQLDirectAPI, SimpleSession
from zato.common.odb import query
from zato.common.odb.ping import get_ping_query
from zato.common.odb.model import APIKeySecurity, Cluster, DeployedService, DeploymentPackage, DeploymentStatus, HTTPBasicAuth, \
     JWT, NTLM, OAuth, PubSubEndpoint, SecurityBase, Server, Service, TLSChannelSecurity, VaultConnection
from zato.common.odb.testing import UnittestEngine
from zato.common.odb.query.pubsub import subscription as query_ps_subscription
from zato.common.odb.query import generic as query_generic
from zato.common.util.api import current_host, get_component_name, get_engine_url, new_cid, parse_extra_into_dict, \
     parse_tls_channel_security_definition, spawn_greenlet
from zato.common.util.sql import ElemsWithOpaqueMaker, elems_with_opaque
from zato.common.util.url_dispatcher import get_match_target
from zato.sso.odb.query import get_rate_limiting_info as get_sso_user_rate_limiting_info

# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session as SASession
    from zato.common.crypto.api import CryptoManager
    from zato.common.odb.model import Cluster as ClusterModel, Server as ServerModel
    from zato.common.typing_ import any_, anylistnone, anyset, callable_, commondict, strdict, strdictnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

rate_limit_keys = 'is_rate_limit_active', 'rate_limit_def', 'rate_limit_type', 'rate_limit_check_parent_def'

unittest_fs_sql_config = {
    UNITTEST.SQL_ENGINE: {
        'ping_query': 'SELECT 1+1'
    }
}

# ################################################################################################################################

ServiceTable = Service.__table__
ServiceTableInsert = ServiceTable.insert

DeployedServiceTable = DeployedService.__table__
DeployedServiceInsert = DeployedServiceTable.insert
DeployedServiceDelete = DeployedServiceTable.delete

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
        self.config = config
        self.fs_sql_config = config['fs_sql_config']
        self.pool = pool

        is_ms_sql_direct = config['engine'] == MS_SQL.ZATO_DIRECT

        if is_ms_sql_direct:
            self._Session = SimpleSession(self.pool.engine) # type: ignore
        else:
            if use_scoped_session:
                self._Session = scoped_session(sessionmaker(bind=self.pool.engine, query_cls=WritableTupleQuery))
            else:
                self._Session = sessionmaker(bind=self.pool.engine, query_cls=WritableTupleQuery)
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

class WritableTupleQuery(Query):

    def __iter__(self):
        out = super(WritableTupleQuery, self).__iter__()

        columns_desc = self.column_descriptions

        first_type = columns_desc[0]['type']
        len_columns_desc = len(columns_desc)

        # This is a simple result of a query such as session.query(ObjectName).count()
        if len_columns_desc == 1 and isinstance(first_type, TypeEngine):
            return out

        # A list of objects, e.g. from .all()
        elif len_columns_desc > 1:
            return (SQLRow(elem) for elem in out)

        # Anything else
        else:
            return out

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
        _extra.update(parse_extra_into_dict(extra)) # type: ignore

        # SQLite has no pools
        if self.engine_name != 'sqlite':
            _extra['pool_size'] = int(self.config.get('pool_size', 1)) # type: ignore
            if _extra['pool_size'] == 0:
                _extra['poolclass'] = NullPool # type: ignore

        engine_url = get_engine_url(self.config)

        if engine_url.startswith('oracle://'):
            engine_url = engine_url.replace('oracle://', 'oracle+oracledb://')

        try:
            self.engine = self._create_engine(engine_url, self.config, _extra)
        except Exception as e:
            self.logger.warning('Could not create SQL connection `%s`, e:`%s`', self.name, e.args[0])

        if self.engine and (not self._is_unittest_engine(engine_url)) and self._is_sa_engine(engine_url):
            event.listen(self.engine, 'checkin', self.on_checkin)
            event.listen(self.engine, 'checkout', self.on_checkout)
            event.listen(self.engine, 'connect', self.on_connect)
            event.listen(self.engine, 'first_connect', self.on_first_connect)

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

        return create_engine(
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
            return create_engine(engine_url, **extra)

        else:
            # This is a direct MS SQL connection
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

            return MSSQLDirectAPI(config['name'], config['pool_size'], connect_kwargs, extra)

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

class _Server:
    """ A plain Python object which is used instead of an SQLAlchemy model so the latter is not tied to a session
    for as long a server is up.
    """
    def __init__(self, odb_server, odb_cluster):
        self.id = odb_server.id
        self.name = odb_server.name
        self.last_join_status = odb_server.last_join_status
        self.token = odb_server.token
        self.cluster_id = odb_cluster.id
        self.cluster = odb_cluster

# ################################################################################################################################

class ODBManager(SessionWrapper):
    """ Manages connections to a given component's Operational Database.
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
    server:'ServerModel'
    cluster:'ClusterModel'

# ################################################################################################################################

    def on_deployment_finished(self):
        """ Commits all the implicit BEGIN blocks opened by SELECTs.
        """
        self._session.commit()

# ################################################################################################################################

    def fetch_server(self, odb_config):
        """ Fetches the server from the ODB. Also sets the 'cluster' attribute
        to the value pointed to by the server's .cluster attribute.
        """
        if not self.session_initialized:
            self.init_session(ZATO_ODB_POOL_NAME, odb_config, self.pool, False)

        with closing(self.session()) as session:
            try:

                server = session.query(Server).filter(Server.token == self.token).one() # type: ignore
                self.server = _Server(server, server.cluster)
                self.server_id = server.id
                self.cluster = server.cluster
                self.cluster_id = server.cluster.id
                return self.server
            except Exception:
                msg = 'Could not find server in ODB, token:`{}`'.format(
                    self.token)
                logger.error(msg)
                raise

# ################################################################################################################################

    def get_servers(self, up_status=SERVER_UP_STATUS.RUNNING, filter_out_self=True):
        """ Returns all servers matching criteria provided on input.
        """
        with closing(self.session()) as session:

            query = session.query( # type: ignore
                        Server).\
                        filter(Server.cluster_id == self.cluster_id)

            if up_status:
                query = query.filter(Server.up_status == up_status) # type: ignore

            if filter_out_self:
                query = query.filter(Server.id != self.server_id) # type: ignore

            return query.all() # type: ignore

# ################################################################################################################################

    def get_default_internal_pubsub_endpoint(self):
        with closing(self.session()) as session:
            return session.query(  # type: ignore
                PubSubEndpoint).\
                    filter(PubSubEndpoint.name==PUBSUB.DEFAULT.INTERNAL_ENDPOINT_NAME).\
                    filter(PubSubEndpoint.endpoint_type==PUBSUB.ENDPOINT_TYPE.INTERNAL.id).\
                    filter(PubSubEndpoint.cluster_id==self.cluster_id).one()

# ################################################################################################################################

    def get_missing_services(self, server, locally_deployed) -> 'anyset':
        """ Returns services deployed on the server given on input that are not among locally_deployed.
        """
        missing = set()

        with closing(self.session()) as session:
            server_services = session.query(
                Service.id, Service.name,
                DeployedService.source_path, DeployedService.source # type: ignore
                ).\
                join(DeployedService, Service.id==DeployedService.service_id # type: ignore
                ).\
                join(Server, DeployedService.server_id==Server.id # type: ignore
                ).\
                filter(Service.is_internal!=true()).\
                all()

            for item in server_services:
                if item.name not in locally_deployed:
                    missing.add(item)

        return missing

# ################################################################################################################################

    def server_up_down(self, token, status, update_host=False, bind_host=None, bind_port=None, preferred_address=None,
        crypto_use_tls=None):
        """ Updates the information regarding the server is RUNNING or CLEAN_DOWN etc.
        and what host it's running on.
        """
        with closing(self.session()) as session:
            server = session.query(Server # type: ignore
                ).\
                filter(Server.token==token).\
                first() # type: ignore

            # It may be the case that the server has been deleted from web-admin before it shut down,
            # in which case during the shut down it will not be able to find itself in ODB anymore.
            if not server:
                logger.info('No server found for token `%s`, status:`%s`', token, status)
                return

            server.up_status = status
            server.up_mod_date = datetime.utcnow() # type: ignore

            if update_host:
                server.host = current_host()
                server.bind_host = bind_host
                server.bind_port = bind_port
                server.preferred_address = preferred_address
                server.crypto_use_tls = crypto_use_tls

            session.add(server)
            session.commit()

# ################################################################################################################################

    def _copy_rate_limiting_config(self, copy_from, copy_to, _keys=rate_limit_keys):
        for key in _keys:
            copy_to[key] = copy_from.get(key)

# ################################################################################################################################

    def get_url_security(self, cluster_id, connection=None, any_internal=HTTP_SOAP.ACCEPT.ANY_INTERNAL):
        """ Returns the security configuration of HTTP URLs.
        """

        # Temporary cache of security definitions visited so as not to
        # look the same ones for each HTTP object that uses them.
        sec_def_cache = {}

        with closing(self.session()) as session:
            # What DB class to fetch depending on the string value of the security type.
            sec_type_db_class = {
                SEC_DEF_TYPE.APIKEY: APIKeySecurity,
                SEC_DEF_TYPE.BASIC_AUTH: HTTPBasicAuth,
                SEC_DEF_TYPE.JWT: JWT,
                SEC_DEF_TYPE.NTLM: NTLM,
                SEC_DEF_TYPE.OAUTH: OAuth,
                SEC_DEF_TYPE.TLS_CHANNEL_SEC: TLSChannelSecurity,
                SEC_DEF_TYPE.VAULT: VaultConnection,
            }

            result = {}

            q = query.http_soap_security_list(session, cluster_id, connection)
            columns = Bunch()

            # So ConfigDict has its data in the format it expects
            for c in q.statement.columns:
                columns[c.name] = None

            for item in elems_with_opaque(q):
                target = get_match_target({
                    'http_accept': item.get('http_accept'),
                    'http_method': item.get('method'),
                    'soap_action': item.soap_action,
                    'url_path': item.url_path,
                }, http_methods_allowed_re=self.parallel_server.http_methods_allowed_re)

                result[target] = Bunch()
                result[target].is_active = item.is_active
                result[target].transport = item.transport
                result[target].data_format = item.data_format
                result[target].sec_use_rbac = item.sec_use_rbac

                if item.security_id:

                    # Ignore WS-Security (WSS) which has been removed in 3.2
                    if item.sec_type == 'wss':
                        continue

                    # For later use
                    result[target].sec_def = Bunch()

                    # We either have already seen this security definition ..
                    if item.security_id in sec_def_cache:
                        sec_def = sec_def_cache[item.security_id]

                    # .. or we have not, in which case we need to look it up
                    # and then cache it for later use.
                    else:

                        # Will raise KeyError if the DB gets somehow misconfigured.
                        db_class = sec_type_db_class[item.sec_type]
                        sec_def_item = session.query(db_class # type: ignore
                                ).\
                                filter(db_class.id==item.security_id).\
                                one() # type: ignore
                        sec_def = bunchify(sec_def_item.asdict())
                        ElemsWithOpaqueMaker.process_config_dict(sec_def)
                        sec_def_cache[item.security_id] = sec_def

                    # Common things first
                    result[target].sec_def.id = sec_def.id
                    result[target].sec_def.name = sec_def.name
                    result[target].sec_def.password = self.decrypt_func(sec_def.password or '')
                    result[target].sec_def.sec_type = item.sec_type

                    if item.sec_type == SEC_DEF_TYPE.BASIC_AUTH:
                        result[target].sec_def.username = sec_def.username
                        result[target].sec_def.realm = sec_def.realm
                        self._copy_rate_limiting_config(sec_def, result[target].sec_def)

                    elif item.sec_type == SEC_DEF_TYPE.JWT:
                        result[target].sec_def.username = sec_def.username
                        self._copy_rate_limiting_config(sec_def, result[target].sec_def)

                    elif item.sec_type == SEC_DEF_TYPE.APIKEY:
                        result[target].sec_def.header = 'HTTP_{}'.format(sec_def.header.upper().replace('-', '_'))
                        self._copy_rate_limiting_config(sec_def, result[target].sec_def)

                    elif item.sec_type == SEC_DEF_TYPE.WSS:
                        result[target].sec_def.username = sec_def.username
                        result[target].sec_def.password_type = sec_def.password_type
                        result[target].sec_def.reject_empty_nonce_creat = sec_def.reject_empty_nonce_creat
                        result[target].sec_def.reject_stale_tokens = sec_def.reject_stale_tokens
                        result[target].sec_def.reject_expiry_limit = sec_def.reject_expiry_limit
                        result[target].sec_def.nonce_freshness_time = sec_def.nonce_freshness_time

                    elif item.sec_type == SEC_DEF_TYPE.TLS_CHANNEL_SEC:
                        result[target].sec_def.value = dict(parse_tls_channel_security_definition(sec_def.value))

                    elif item.sec_type == SEC_DEF_TYPE.NTLM:
                        result[target].sec_def.username = sec_def.username

                else:
                    result[target].sec_def = ZATO_NONE

            return result, columns

# ################################################################################################################################

    def get_sql_internal_service_list(self, cluster_id):
        """ Returns a list of service name and IDs for input cluster ID. It represents what is currently found in the ODB
        and is used during server startup to decide if any new services should be added from what is found in the filesystem.
        """
        with closing(self.session()) as session:
            return session.query( # type: ignore
                Service.id,
                Service.impl_name,
                Service.is_active,
                Service.slow_threshold,
                ).\
                filter(Service.cluster_id==cluster_id).\
                all() # type: ignore

# ################################################################################################################################

    def get_basic_data_service_list(self, session):
        """ Returns basic information about all the services in ODB.
        """
        query = select([
            ServiceTable.c.id,
            ServiceTable.c.name,
            ServiceTable.c.impl_name,
        ]).where(
            ServiceTable.c.cluster_id==self.cluster_id
        )

        return session.execute(query).\
            fetchall()

# ################################################################################################################################

    def get_basic_data_deployed_service_list(self):
        """ Returns basic information about all the deployed services in ODB.
        """
        with closing(self.session()) as session:

            query = select([
                ServiceTable.c.name,
                DeployedServiceTable.c.source,
            ]).where(and_(
                DeployedServiceTable.c.service_id==ServiceTable.c.id,
                DeployedServiceTable.c.server_id==self.server_id
            ))

            return session.execute(query).fetchall() # type: ignore

# ################################################################################################################################

    def add_services(self, session, data):
        # type: (list[dict]) -> None
        try:
            session.execute(ServiceTableInsert().values(data)) # type: ignore
        except IntegrityError:
            # This can be ignored because it is possible that there will be
            # more than one server trying to insert rows related to services
            # that are hot-deployed from web-admin or another source.
            logger.debug('Ignoring IntegrityError with `%s`', data) # type: ignore

# ################################################################################################################################

    def add_deployed_services(self, session, data):

        try:
            session.execute(DeployedServiceInsert().values(data))
        except OperationalError as e:
            if 'duplicate key value violates unique constraint' in str(e):
                pass
            else:
                raise

# ################################################################################################################################

    def drop_deployed_services_by_name(self, session, service_id_list):
        session.execute(
            DeployedServiceDelete().\
            where(DeployedService.service_id.in_(service_id_list)) # type: ignore
        )

# ################################################################################################################################

    def drop_deployed_services(self, server_id):
        """ Removes all the deployed services from a server.
        """
        with closing(self.session()) as session:
            session.execute(
                DeployedServiceDelete(). # type: ignore
                \
                where(DeployedService.server_id==server_id)  # type: ignore
            )
            session.commit()

# ################################################################################################################################

    def is_service_active(self, service_id):
        """ Returns whether the given service is active or not.
        """
        with closing(self.session()) as session:
            return session.query(Service.is_active # type: ignore
                ).\
                filter(Service.id==service_id).\
                one()[0] # type: ignore

# ################################################################################################################################

    def hot_deploy(self, deployment_time, details, payload_name, payload, server_id):
        """ Inserts hot-deployed data into the DB along with setting the preliminary
        AWAITING_DEPLOYMENT status for each of the servers this server's cluster
        is aware of.
        """
        with closing(self.session()) as session:
            # Create the deployment package info ..
            dp = DeploymentPackage()
            dp.deployment_time = deployment_time
            dp.details = details
            dp.payload_name = payload_name
            dp.payload = payload
            dp.server_id = server_id

            # .. add it to the session ..
            session.add(dp)

            # .. for each of the servers in this cluster set the initial status ..
            servers = session.query(Cluster # type: ignore
                   ).\
                   filter(Cluster.id == self.server.cluster_id).\
                   one().servers # type: ignore

            for server in servers:
                ds = DeploymentStatus()
                ds.package_id = dp.id
                ds.server_id = server.id
                ds.status = DEPLOYMENT_STATUS.AWAITING_DEPLOYMENT
                ds.status_change_time = datetime.utcnow() # type: ignore

                session.add(ds)

            session.commit()

            return dp.id

# ################################################################################################################################

    def add_delivery(self, deployment_time, details, service, source_info):
        """ Adds information about the server's deployed service into the ODB.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def get_internal_channel_list(self, cluster_id, needs_columns=False):
        """ Returns the list of internal HTTP/SOAP channels, that is,
        channels pointing to internal services.
        """
        with closing(self.session()) as session:
            return query.internal_channel_list(session, cluster_id, needs_columns) # type: ignore

    def get_http_soap_list(self, cluster_id, connection=None, transport=None, needs_columns=False):
        """ Returns the list of all HTTP/SOAP connections.
        """
        with closing(self.session()) as session:
            return query.http_soap_list(session, cluster_id, connection, transport, True, None, needs_columns)

# ################################################################################################################################

    def get_job_list(self, cluster_id, needs_columns=False):
        """ Returns a list of jobs defined on the given cluster.
        """
        with closing(self.session()) as session:
            return query.job_list(session, cluster_id, None, needs_columns)

# ################################################################################################################################

    def get_service_list(self, cluster_id, needs_columns=False):
        """ Returns a list of services defined on the given cluster.
        """
        with closing(self.session()) as session:
            return elems_with_opaque(query.service_list(session, cluster_id, needs_columns=needs_columns))

# ################################################################################################################################

    def get_service_id_list(self, session, cluster_id, name_list):
        """ Returns a list of IDs matching input service names.
        """
        return query.service_id_list(session, cluster_id, name_list)

# ################################################################################################################################

    def get_service_list_with_include(self, session, cluster_id, include_list, needs_columns=False):
        """ Returns a list of all services from the input include_list.
        """
        return query.service_list_with_include(session, cluster_id, include_list, needs_columns)

# ################################################################################################################################

    def get_apikey_security_list(self, cluster_id, needs_columns=False):
        """ Returns a list of API keys existing on the given cluster.
        """
        with closing(self.session()) as session:
            return elems_with_opaque(query.apikey_security_list(session, cluster_id, needs_columns))

# ################################################################################################################################

    def get_aws_security_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AWS definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.aws_security_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_basic_auth_list(self, cluster_id, cluster_name, needs_columns=False):
        """ Returns a list of HTTP Basic Auth definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return elems_with_opaque(query.basic_auth_list(session, cluster_id, cluster_name, needs_columns))

# ################################################################################################################################

    def get_jwt_list(self, cluster_id, cluster_name, needs_columns=False):
        """ Returns a list of JWT definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return elems_with_opaque(query.jwt_list(session, cluster_id, cluster_name, needs_columns))

# ################################################################################################################################

    def get_ntlm_list(self, cluster_id, needs_columns=False):
        """ Returns a list of NTLM definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.ntlm_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_oauth_list(self, cluster_id, needs_columns=False):
        """ Returns a list of OAuth accounts existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.oauth_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_tls_ca_cert_list(self, cluster_id, needs_columns=False):
        """ Returns a list of TLS CA certs on the given cluster.
        """
        with closing(self.session()) as session:
            return query.tls_ca_cert_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_tls_channel_sec_list(self, cluster_id, needs_columns=False):
        """ Returns a list of definitions for securing TLS channels.
        """
        with closing(self.session()) as session:
            return query.tls_channel_sec_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_tls_key_cert_list(self, cluster_id, needs_columns=False):
        """ Returns a list of TLS key/cert pairs on the given cluster.
        """
        with closing(self.session()) as session:
            return query.tls_key_cert_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_wss_list(self, cluster_id, needs_columns=False):
        """ Returns a list of WS-Security definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.wss_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_vault_connection_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Vault connections on the given cluster.
        """
        with closing(self.session()) as session:
            return query.vault_connection_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_xpath_sec_list(self, cluster_id, needs_columns=False):
        """ Returns a list of XPath-based security definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.xpath_sec_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_definition_amqp(self, cluster_id, def_id):
        """ Returns an AMQP definition's details.
        """
        with closing(self.session()) as session:
            return query.definition_amqp(session, cluster_id, def_id)

# ################################################################################################################################

    def get_definition_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.definition_amqp_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_amqp(self, cluster_id, out_id):
        """ Returns an outgoing AMQP connection's details.
        """
        with closing(self.session()) as session:
            return query.out_amqp(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing AMQP connections.
        """
        with closing(self.session()) as session:
            return query.out_amqp_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_channel_amqp(self, cluster_id, channel_id):
        """ Returns a particular AMQP channel.
        """
        with closing(self.session()) as session:
            return query.channel_amqp(session, cluster_id, channel_id)

# ################################################################################################################################

    def get_channel_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP channels.
        """
        with closing(self.session()) as session:
            return query.channel_amqp_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_def_wmq(self, cluster_id, def_id):
        """ Returns an IBM MQ definition's details.
        """
        with closing(self.session()) as session:
            return query.definition_wmq(session, cluster_id, def_id)

# ################################################################################################################################

    def get_definition_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of IBM MQ definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.definition_wmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_wmq(self, cluster_id, out_id):
        """ Returns an outgoing IBM MQ connection's details.
        """
        with closing(self.session()) as session:
            return query.out_wmq(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing IBM MQ connections.
        """
        with closing(self.session()) as session:
            return query.out_wmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_channel_wmq(self, cluster_id, channel_id):
        """ Returns a particular IBM MQ channel.
        """
        with closing(self.session()) as session:
            return query.channel_wmq(session, cluster_id, channel_id)

# ################################################################################################################################

    def get_channel_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of IBM MQ channels.
        """
        with closing(self.session()) as session:
            return query.channel_wmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_zmq(self, cluster_id, out_id):
        """ Returns an outgoing ZMQ connection's details.
        """
        with closing(self.session()) as session:
            return query.out_zmq(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing ZMQ connections.
        """
        with closing(self.session()) as session:
            return query.out_zmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_channel_zmq(self, cluster_id, channel_id):
        """ Returns a particular ZMQ channel.
        """
        with closing(self.session()) as session:
            return query.channel_zmq(session, cluster_id, channel_id)

# ################################################################################################################################

    def get_channel_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of ZMQ channels.
        """
        with closing(self.session()) as session:
            return query.channel_zmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_channel_file_transfer_list(self, cluster_id, needs_columns=False):
        """ Returns a list of file transfer channels.
        """
        with closing(self.session()) as session:
            return query_generic.connection_list(
                session, cluster_id, GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER, needs_columns)

# ################################################################################################################################

    def get_channel_web_socket(self, cluster_id, channel_id):
        """ Returns a particular WebSocket channel.
        """
        with closing(self.session()) as session:
            return query.channel_web_socket(session, cluster_id, channel_id)

# ################################################################################################################################

    def get_channel_web_socket_list(self, cluster_id, needs_columns=False):
        """ Returns a list of WebSocket channels.
        """
        with closing(self.session()) as session:
            return query.channel_web_socket_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_sql(self, cluster_id, out_id):
        """ Returns an outgoing SQL connection's details.
        """
        with closing(self.session()) as session:
            return query.out_sql(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_sql_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing SQL connections.
        """
        with closing(self.session()) as session:
            return query.out_sql_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_odoo(self, cluster_id, out_id):
        """ Returns an outgoing Odoo connection's details.
        """
        with closing(self.session()) as session:
            return query.out_odoo(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_odoo_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing Odoo connections.
        """
        with closing(self.session()) as session:
            return query.out_odoo_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_sap(self, cluster_id, out_id):
        """ Returns an outgoing SAP RFC connection's details.
        """
        with closing(self.session()) as session:
            return query.out_sap(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_sap_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing SAP RFC connections.
        """
        with closing(self.session()) as session:
            return query.out_sap_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_sftp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing SFTP connections.
        """
        with closing(self.session()) as session:
            return query_generic.connection_list(session, cluster_id, GENERIC.CONNECTION.TYPE.OUTCONN_SFTP, needs_columns)

# ################################################################################################################################

    def get_out_ftp(self, cluster_id, out_id):
        """ Returns an outgoing FTP connection's details.
        """
        with closing(self.session()) as session:
            return query.out_ftp(session, cluster_id, out_id)

# ################################################################################################################################

    def get_out_ftp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing FTP connections.
        """
        with closing(self.session()) as session:
            return query.out_ftp_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_cache_builtin(self, cluster_id, id):
        """ Returns a built-in cache definition's details.
        """
        with closing(self.session()) as session:
            return query.cache_builtin(session, cluster_id, id)

# ################################################################################################################################

    def get_cache_builtin_list(self, cluster_id, needs_columns=False):
        """ Returns a list of built-in cache definitions.
        """
        with closing(self.session()) as session:
            return query.cache_builtin_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_cache_memcached(self, cluster_id, id):
        """ Returns a Memcached-based definition's details.
        """
        with closing(self.session()) as session:
            return query.cache_memcached(session, cluster_id, id)

# ################################################################################################################################

    def get_cache_memcached_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Memcached-based cache definitions.
        """
        with closing(self.session()) as session:
            return query.cache_memcached_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_namespace_list(self, cluster_id, needs_columns=False):
        """ Returns a list of XML namespaces.
        """
        with closing(self.session()) as session:
            return query.namespace_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_xpath_list(self, cluster_id, needs_columns=False):
        """ Returns a list of XPath expressions.
        """
        with closing(self.session()) as session:
            return query.xpath_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_json_pointer_list(self, cluster_id, needs_columns=False):
        """ Returns a list of JSON Pointer expressions.
        """
        with closing(self.session()) as session:
            return query.json_pointer_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_cloud_aws_s3_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AWS S3 connections.
        """
        with closing(self.session()) as session:
            return query.cloud_aws_s3_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_pubsub_topic_list(self, cluster_id, needs_columns=False):
        """ Returns a list of pub/sub topics defined in a cluster.
        """
        return elems_with_opaque(query.pubsub_topic_list(self._session, cluster_id, needs_columns))

# ################################################################################################################################

    def get_pubsub_subscription_list(self, cluster_id, needs_columns=False):
        """ Returns a list of pub/sub subscriptions defined in a cluster.
        """
        return query_ps_subscription.pubsub_subscription_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_notif_sql_list(self, cluster_id, needs_columns=False):
        """ Returns a list of SQL notification definitions.
        """
        return query.notif_sql_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_cassandra_conn_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Cassandra connections.
        """
        return query.cassandra_conn_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_cassandra_query_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Cassandra queries.
        """
        return query.cassandra_query_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_search_es_list(self, cluster_id, needs_columns=False):
        """ Returns a list of ElasticSearch connections.
        """
        return query.search_es_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_search_solr_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Solr connections.
        """
        return query.search_solr_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_sms_twilio_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Twilio connections.
        """
        return query.sms_twilio_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_email_smtp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of SMTP connections.
        """
        return query.email_smtp_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_email_imap_list(self, cluster_id, needs_columns=False):
        """ Returns a list of IMAP connections.
        """
        return query.email_imap_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_rbac_permission_list(self, cluster_id, needs_columns=False):
        """ Returns a list of RBAC permissions.
        """
        return query.rbac_permission_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_rbac_role_list(self, cluster_id, needs_columns=False):
        """ Returns a list of RBAC roles.
        """
        return query.rbac_role_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_rbac_client_role_list(self, cluster_id, needs_columns=False):
        """ Returns a list of RBAC roles assigned to clients.
        """
        return query.rbac_client_role_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_rbac_role_permission_list(self, cluster_id, needs_columns=False):
        """ Returns a list of RBAC permissions for roles.
        """
        return query.rbac_role_permission_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_pubsub_endpoint_list(self, cluster_id, needs_columns=False):
        """ Returns a list of pub/sub endpoints.
        """
        out = query.pubsub_endpoint_list(self._session, cluster_id, needs_columns)
        return out

# ################################################################################################################################

    def get_generic_connection_list(self, cluster_id, needs_columns=False):
        """ Returns a list of generic connections.
        """
        return query_generic.connection_list(self._session, cluster_id, needs_columns=needs_columns)

# ################################################################################################################################

    def get_sso_user_rate_limiting_info(self):
        """ Returns a list of SSO users that have rate limiting enabled.
        """
        with closing(self.session()) as session:
            return get_sso_user_rate_limiting_info(session)

# ################################################################################################################################

    def _migrate_30_encrypt_sec_base(self, session, id, attr_name, encrypted_value):
        """ Sets an encrypted value of a named attribute in a security definition.
        """
        item = session.query(SecurityBase).\
            filter(SecurityBase.id==id).\
            one()

        setattr(item, attr_name, encrypted_value)
        session.add(item)

    _migrate_30_encrypt_sec_apikey             = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_aws                = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_basic_auth         = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_jwt                = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_ntlm               = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_oauth              = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_vault_conn_sec     = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_wss                = _migrate_30_encrypt_sec_base
    _migrate_30_encrypt_sec_xpath_sec          = _migrate_30_encrypt_sec_base

# ################################################################################################################################
