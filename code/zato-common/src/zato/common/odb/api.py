# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from copy import deepcopy
from cStringIO import StringIO
from datetime import datetime, timedelta
from logging import DEBUG, getLogger
from threading import RLock
from time import time
from traceback import format_exc

# Spring Python
from springpython.context import DisposableObject

# SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from sqlalchemy.sql.expression import true

# Bunch
from bunch import Bunch

# Zato
from zato.common import DEPLOYMENT_STATUS, Inactive, MISC, SEC_DEF_TYPE, SECRET_SHADOW, SERVER_UP_STATUS, TRACE1, ZATO_NONE, \
     ZATO_ODB_POOL_NAME
from zato.common.odb.model import APIKeySecurity, Cluster, DeployedService, DeploymentPackage, DeploymentStatus, HTTPBasicAuth, \
     HTTPSOAP, HTTSOAPAudit, JWT, OAuth, Server, Service, TLSChannelSecurity, XPathSecurity, WSSDefinition, \
     VaultConnection
from zato.common.odb import get_ping_query, query
from zato.common.odb.query.pubsub import subscription as query_ps_subscription
from zato.common.util import current_host, get_component_name, get_engine_url, get_http_json_channel, get_http_soap_channel, \
     parse_extra_into_dict, parse_tls_channel_security_definition

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class SessionWrapper(object):
    """ Wraps an SQLAlchemy session.
    """
    def __init__(self):
        self.session_initialized = False
        self.pool = None
        self.config = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def init_session(self, name, config, pool, use_scoped_session=True):
        self.config = config
        self.fs_sql_config = config['fs_sql_config']
        self.pool = pool

        try:
            self.pool.ping(self.fs_sql_config)
        except Exception, e:
            msg = 'Could not ping:`%s`, session will be left uninitialized, e:`%s`'
            self.logger.warn(msg, name, format_exc(e))
        else:
            if use_scoped_session:
                self._Session = scoped_session(sessionmaker(bind=self.pool.engine))
            else:
                self._Session = sessionmaker(bind=self.pool.engine)

            self._session = self._Session()
            self.session_initialized = True

    def session(self):
        return self._Session()

    def close(self):
        self._session.close()

# ################################################################################################################################

class SQLConnectionPool(object):
    """ A pool of SQL connections wrapping an SQLAlchemy engine.
    """
    def __init__(self, name, config, config_no_sensitive):
        self.logger = getLogger(self.__class__.__name__)
        self.has_debug = self.logger.isEnabledFor(DEBUG)

        self.name = name
        self.config = config
        self.engine_name = config['engine'] # self.engine.name is 'mysql' while 'self.engine_name' is mysql+pymysql

        # Safe for printing out to logs, any sensitive data has been shadowed
        self.config_no_sensitive = config_no_sensitive

        _extra = {}

        # MySQL only
        if self.engine_name.startswith('mysql'):
            _extra['pool_recycle'] = 600

        # Postgres-only
        elif self.engine_name.startswith('postgres'):
            _extra['connect_args'] = {'application_name': get_component_name()}

        extra = self.config.get('extra') # Optional, hence .get
        _extra.update(parse_extra_into_dict(extra))

        # SQLite has no pools
        if self.engine_name != 'sqlite':
            _extra['pool_size'] = int(config.get('pool_size', 1))
            if _extra['pool_size'] == 0:
                _extra['poolclass'] = NullPool

        engine_url = get_engine_url(config)
        self.engine = self._create_engine(engine_url, config, _extra)

        if self.engine:
            event.listen(self.engine, 'checkin', self.on_checkin)
            event.listen(self.engine, 'checkout', self.on_checkout)
            event.listen(self.engine, 'connect', self.on_connect)
            event.listen(self.engine, 'first_connect', self.on_first_connect)

        self.checkins = 0
        self.checkouts = 0

        self.checkins = 0
        self.checkouts = 0

    def __str__(self):
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    __repr__ = __str__

    def _create_engine(self, engine_url, config, extra):
        if 'mxodbc' in engine_url:

            from mx.ODBCConnect.Client import ServerSession as mxServerSession
            from mx.ODBCConnect.Error import OperationalError

            config_data = {
                'Server_Connection': {},
                'Logging': {},
                'Integration': {},
            }

            config_data['Server_Connection']['host'] = config['host']
            config_data['Server_Connection']['port'] = config['port']
            config_data['Server_Connection']['using_ssl'] = extra.pop('mxodbc_using_ssl', False)

            config_data['Integration']['gevent'] = True

            try:
                session = mxServerSession(config_data=config_data)
                odbc = session.open()
            except OperationalError, e:
                self.logger.warn('SQL connection could not be created, caught mxODBC exception, e:`%s`', format_exc(e))
            else:
                url = '{engine}://{username}:{password}@{db_name}'.format(**config)
                return create_engine(url, module=odbc, **extra)

        else:
            return create_engine(engine_url, **extra)

    def on_checkin(self, dbapi_conn, conn_record):
        if self.has_debug:
            self.logger.debug('Checked in dbapi_conn:%s, conn_record:%s', dbapi_conn, conn_record)
        self.checkins += 1

    def on_checkout(self, dbapi_conn, conn_record, conn_proxy):
        if self.has_debug:
            self.logger.debug('Checked out dbapi_conn:%s, conn_record:%s, conn_proxy:%s',
                dbapi_conn, conn_record, conn_proxy)

        self.checkouts += 1
        self.logger.debug('co-cin-diff %d-%d-%d', self.checkouts, self.checkins, self.checkouts - self.checkins)

    def on_connect(self, dbapi_conn, conn_record):
        if self.has_debug:
            self.logger.debug('Connect dbapi_conn:%s, conn_record:%s', dbapi_conn, conn_record)

    def on_first_connect(self, dbapi_conn, conn_record):
        if self.has_debug:
            self.logger.debug('First connect dbapi_conn:%s, conn_record:%s', dbapi_conn, conn_record)

    def ping(self, fs_sql_config):
        """ Pings the SQL database and returns the response time, in milliseconds.
        """
        query = get_ping_query(fs_sql_config, self.config)

        self.logger.debug('About to ping the SQL connection pool:`%s`, query:`%s`', self.config_no_sensitive, query)

        start_time = time()
        self.engine.connect().execute(query)
        response_time = time() - start_time

        self.logger.debug('Ping OK, pool:`%s`, response_time:`%s` s', self.config_no_sensitive, response_time)

        return response_time

    def _conn(self):
        """ Returns an SQLAlchemy connection object.
        """
        return self.engine.connect()

    conn = property(fget=_conn, doc=_conn.__doc__)

    def _impl(self):
        """ Returns the underlying connection's implementation, the SQLAlchemy engine.
        """
        return self.engine

    impl = property(fget=_impl, doc=_impl.__doc__)

# ################################################################################################################################

class PoolStore(DisposableObject):
    """ A main class for accessing all of the SQL connection pools. Each server
    thread has its own store.
    """
    def __init__(self, sql_conn_class=SQLConnectionPool):
        super(PoolStore, self).__init__()
        self.sql_conn_class = sql_conn_class
        self._lock = RLock()
        self.wrappers = {}
        self.logger = getLogger(self.__class__.__name__)

    def __getitem__(self, name, enforce_is_active=True):
        """ Checks out the connection pool. If enforce_is_active is False,
        the pool's is_active flag will be ignored.
        """
        with self._lock:
            if enforce_is_active:
                wrapper = self.wrappers[name]
                if wrapper.config['is_active']:
                    return wrapper
                raise Inactive(name)
            else:
                return self.wrappers[name]

    get = __getitem__

    def __setitem__(self, name, config):
        """ Stops a connection pool if it exists and replaces it with a new one
        using updated settings.
        """
        with self._lock:
            if name in self.wrappers:
                del self[name]

            config_no_sensitive = deepcopy(config)
            config_no_sensitive['password'] = SECRET_SHADOW
            pool = self.sql_conn_class(name, config, config_no_sensitive)

            wrapper = SessionWrapper()
            wrapper.init_session(name, config, pool)

            self.wrappers[name] = wrapper

    def __delitem__(self, name):
        """ Stops a pool and deletes it from the store.
        """
        with self._lock:
            self.wrappers[name].pool.engine.dispose()
            del self.wrappers[name]

    def __str__(self):
        out = StringIO()
        out.write('<{} at {} wrappers:['.format(self.__class__.__name__, hex(id(self))))
        out.write(', '.join(sorted(self.wrappers.keys())))
        out.write(']>')
        return out.getvalue()

    __repr__ = __str__

    def change_password(self, name, password):
        """ Updates the password which means recreating the pool using the new
        password.
        """
        with self._lock:
            self[name].pool.engine.dispose()
            config = deepcopy(self.wrappers[name].pool.config)
            config['password'] = password
            self[name] = config

    def destroy(self):
        """ Invoked when Spring Python's container is releasing the store.
        """
        with self._lock:
            for name, wrapper in self.wrappers.items():
                wrapper.pool.engine.dispose()

# ################################################################################################################################

class _Server(object):
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
    def __init__(self, well_known_data=None, token=None, crypto_manager=None, server_id=None, server_name=None, cluster_id=None,
            pool=None):
        super(ODBManager, self).__init__()
        self.well_known_data = well_known_data
        self.token = token
        self.crypto_manager = crypto_manager
        self.server_id = server_id
        self.server_name = server_name
        self.cluster_id = cluster_id
        self.pool = pool

    def on_deployment_finished(self):
        """ Commits all the implicit BEGIN blocks opened by SELECTs.
        """
        self._session.commit()

    def fetch_server(self, odb_config):
        """ Fetches the server from the ODB. Also sets the 'cluster' attribute
        to the value pointed to by the server's .cluster attribute.
        """
        if not self.session_initialized:
            self.init_session(ZATO_ODB_POOL_NAME, odb_config, self.pool, False)

        with closing(self.session()) as session:
            try:
                server = session.query(Server).\
                       filter(Server.token == self.token).\
                       one()
                self.server = _Server(server, server.cluster)
                self.server_id = server.id
                self.cluster = server.cluster
                self.cluster_id = server.cluster.id
                return self.server
            except Exception:
                msg = 'Could not find the server in the ODB, token:[{0}]'.format(
                    self.token)
                logger.error(msg)
                raise

    def get_servers(self, up_status=SERVER_UP_STATUS.RUNNING, filter_out_self=True):
        """ Returns all servers matching criteria provided on input.
        """
        with closing(self.session()) as session:

            query = session.query(Server).\
                filter(Server.cluster_id == self.cluster_id)

            if up_status:
                query = query.filter(Server.up_status == up_status)

            if filter_out_self:
                query = query.filter(Server.id != self.server_id)

            return query.all()

    def get_missing_services(self, server, locally_deployed):
        """ Returns services deployed on the server given on input that are not among locally_deployed.
        """
        missing = []

        with closing(self.session()) as session:

            server_services = session.query(
                Service.id, Service.name,
                DeployedService.source_path, DeployedService.source).\
                join(DeployedService, Service.id==DeployedService.service_id).\
                join(Server, DeployedService.server_id==Server.id).\
                filter(Service.is_internal!=true()).\
                all()

            for item in server_services:
                if item.name not in locally_deployed:
                    missing.append(item)

        return missing

    def server_up_down(self, token, status, update_host=False, bind_host=None, bind_port=None, preferred_address=None,
        crypto_use_tls=None):
        """ Updates the information regarding the server is RUNNING or CLEAN_DOWN etc.
        and what host it's running on.
        """
        with closing(self.session()) as session:
            server = session.query(Server).\
                filter(Server.token==token).\
                one()

            server.up_status = status
            server.up_mod_date = datetime.utcnow()

            if update_host:
                server.host = current_host()
                server.bind_host = bind_host
                server.bind_port = bind_port
                server.preferred_address = preferred_address
                server.crypto_use_tls = crypto_use_tls

            session.add(server)
            session.commit()

    def get_url_security(self, cluster_id, connection=None):
        """ Returns the security configuration of HTTP URLs.
        """
        with closing(self.session()) as session:
            # What DB class to fetch depending on the string value of the security type.
            sec_type_db_class = {
                SEC_DEF_TYPE.APIKEY: APIKeySecurity,
                SEC_DEF_TYPE.BASIC_AUTH: HTTPBasicAuth,
                SEC_DEF_TYPE.JWT: JWT,
                SEC_DEF_TYPE.OAUTH: OAuth,
                SEC_DEF_TYPE.TLS_CHANNEL_SEC: TLSChannelSecurity,
                SEC_DEF_TYPE.WSS: WSSDefinition,
                SEC_DEF_TYPE.VAULT: VaultConnection,
                SEC_DEF_TYPE.XPATH_SEC: XPathSecurity,
                }

            result = {}

            q = query.http_soap_security_list(session, cluster_id, connection)
            columns = Bunch()

            # So ConfigDict has its data in the format it expects
            for c in q.statement.columns:
                columns[c.name] = None

            for item in q.all():
                target = '{}{}{}'.format(item.soap_action, MISC.SEPARATOR, item.url_path)

                result[target] = Bunch()
                result[target].is_active = item.is_active
                result[target].transport = item.transport
                result[target].data_format = item.data_format
                result[target].sec_use_rbac = item.sec_use_rbac

                if item.security_id:
                    result[target].sec_def = Bunch()

                    # Will raise KeyError if the DB gets somehow misconfigured.
                    db_class = sec_type_db_class[item.sec_type]

                    sec_def = session.query(db_class).\
                            filter(db_class.id==item.security_id).\
                            one()

                    # Common things first
                    result[target].sec_def.id = sec_def.id
                    result[target].sec_def.name = sec_def.name
                    result[target].sec_def.password = sec_def.password
                    result[target].sec_def.sec_type = item.sec_type

                    if item.sec_type == SEC_DEF_TYPE.BASIC_AUTH:
                        result[target].sec_def.username = sec_def.username
                        result[target].sec_def.password = sec_def.password
                        result[target].sec_def.realm = sec_def.realm

                    elif item.sec_type == SEC_DEF_TYPE.JWT:
                        result[target].sec_def.username = sec_def.username
                        result[target].sec_def.password = sec_def.password

                    elif item.sec_type == SEC_DEF_TYPE.APIKEY:
                        result[target].sec_def.username = 'HTTP_{}'.format(sec_def.username.upper().replace('-', '_'))
                        result[target].sec_def.password = sec_def.password

                    elif item.sec_type == SEC_DEF_TYPE.WSS:
                        result[target].sec_def.username = sec_def.username
                        result[target].sec_def.password = sec_def.password
                        result[target].sec_def.password_type = sec_def.password_type
                        result[target].sec_def.reject_empty_nonce_creat = sec_def.reject_empty_nonce_creat
                        result[target].sec_def.reject_stale_tokens = sec_def.reject_stale_tokens
                        result[target].sec_def.reject_expiry_limit = sec_def.reject_expiry_limit
                        result[target].sec_def.nonce_freshness_time = sec_def.nonce_freshness_time

                    elif item.sec_type == SEC_DEF_TYPE.TLS_CHANNEL_SEC:
                        result[target].sec_def.value = dict(parse_tls_channel_security_definition(sec_def.value))

                    elif item.sec_type == SEC_DEF_TYPE.XPATH_SEC:
                        result[target].sec_def.username = sec_def.username
                        result[target].sec_def.password = sec_def.password
                        result[target].sec_def.username_expr = sec_def.username_expr
                        result[target].sec_def.password_expr = sec_def.password_expr

                else:
                    result[target].sec_def = ZATO_NONE

            return result, columns

    def add_service(self, name, impl_name, is_internal, deployment_time, details, source_info):
        """ Adds information about the server's service into the ODB.
        """
        try:
            service = Service(None, name, True, impl_name, is_internal, self.cluster)
            self._session.add(service)
            try:
                self._session.commit()
            except(IntegrityError, ProgrammingError), e:
                logger.log(TRACE1, 'IntegrityError (Service), e:[%s]', format_exc(e).decode('utf-8'))
                self._session.rollback()

                service = self._session.query(Service).\
                    join(Cluster, Service.cluster_id==Cluster.id).\
                    filter(Service.name==name).\
                    filter(Cluster.id==self.cluster.id).\
                    one()

            self.add_deployed_service(deployment_time, details, service, source_info)

            return service.id, service.is_active, service.slow_threshold

        except Exception, e:
            logger.error('Could not add service, name:[%s], e:[%s]', name, format_exc(e).decode('utf-8'))
            self._session.rollback()

    def drop_deployed_services(self, server_id):
        """ Removes all the deployed services from a server.
        """
        with closing(self.session()) as session:
            session.query(DeployedService).\
                filter(DeployedService.server_id==server_id).\
                delete()
            session.commit()

    def add_deployed_service(self, deployment_time, details, service, source_info):
        """ Adds information about the server's deployed service into the ODB.
        """
        try:
            ds = DeployedService(deployment_time, details, self.server.id, service,
                source_info.source, source_info.path, source_info.hash, source_info.hash_method)
            self._session.add(ds)
            try:
                self._session.commit()
            except(IntegrityError, ProgrammingError), e:

                logger.log(TRACE1, 'IntegrityError (DeployedService), e:[%s]', format_exc(e).decode('utf-8'))
                self._session.rollback()

                ds = self._session.query(DeployedService).\
                    filter(DeployedService.service_id==service.id).\
                    filter(DeployedService.server_id==self.server.id).\
                    one()

                ds.deployment_time = deployment_time
                ds.details = details
                ds.source = source_info.source
                ds.source_path = source_info.path
                ds.source_hash = source_info.hash
                ds.source_hash_method = source_info.hash_method

                self._session.add(ds)
                self._session.commit()

        except Exception, e:
            msg = 'Could not add the DeployedService, e:[{e}]'.format(e=format_exc(e))
            logger.error(msg)
            self._session.rollback()

    def is_service_active(self, service_id):
        """ Returns whether the given service is active or not.
        """
        with closing(self.session()) as session:
            return session.query(Service.is_active).\
                filter(Service.id==service_id).\
                one()[0]

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
            servers = session.query(Cluster).\
                   filter(Cluster.id == self.server.cluster_id).\
                   one().servers

            for server in servers:
                ds = DeploymentStatus()
                ds.package_id = dp.id
                ds.server_id = server.id
                ds.status = DEPLOYMENT_STATUS.AWAITING_DEPLOYMENT
                ds.status_change_time = datetime.utcnow()

                session.add(ds)

            session.commit()

            return dp.id

    def _become_cluster_wide(self, cluster, session):
        """ Update all the Cluster's attributes that are related to connector servers.
        """
        cluster.cw_srv_id = self.server.id
        cluster.cw_srv_keep_alive_dt = datetime.utcnow()

        session.add(cluster)
        session.commit()

        msg = 'Server id:[{}], name:[{}] is now a connector server for cluster id:[{}], name:[{}]'.format(
            self.server.id, self.server.name, cluster.id, cluster.name)
        logger.info(msg)

        return True

    def conn_server_past_grace_time(self, cluster, grace_time):
        """ Whether it's already past the grace time the connector server had
        for updating its keep-alive timestamp.
        """
        last_keep_alive = cluster.cw_srv_keep_alive_dt
        max_allowed = last_keep_alive + timedelta(seconds=grace_time)
        now = datetime.utcnow()

        msg = 'last_keep_alive:[{}], grace_time:[{}], max_allowed:[{}], now:[{}]'.format(
            last_keep_alive, grace_time, max_allowed, now)
        logger.info(msg)

        # Return True if 'now' is past what it's allowed
        return now > max_allowed

    def become_cluster_wide(self, grace_time):
        """ Makes an attempt for the server to become a connector one, that is,
        the server to start all the connectors.
        """
        with closing(self.session()) as session:
            cluster = session.query(Cluster).\
                with_lockmode('update').\
                filter(Cluster.id == self.server.cluster_id).\
                one()

            # No cluster-wide singleton server at all so we made it first
            if not cluster.cw_srv_id:
                return self._become_cluster_wide(cluster, session)
            elif self.conn_server_past_grace_time(cluster, grace_time):
                return self._become_cluster_wide(cluster, session)
            else:
                session.rollback()
                msg = ('Server id:[{}], name:[{}] will not be a connector server for '
                'cluster id:[{}], name:[{}], cluster.cw_srv_id:[{}], cluster.cw_srv_keep_alive_dt:[{}]').format(
                    self.server.id, self.server.name, cluster.id, cluster.name, cluster.cw_srv_id, cluster.cw_srv_keep_alive_dt)
                logger.debug(msg)

    def clear_cluster_wide(self):
        """ Invoked when the cluster-wide singleton server is making a clean shutdown, sets
        all the relevant data to NULL in the ODB.
        """
        with closing(self.session()) as session:
            cluster = session.query(Cluster).\
                with_lockmode('update').\
                filter(Cluster.id == self.server.cluster_id).\
                one()

            cluster.cw_srv_id = None
            cluster.cw_srv_keep_alive_dt = None

            session.add(cluster)
            session.commit()

            self.logger.info('({}) Cleared cluster-wide singleton server flag'.format(self.server.name))

    def add_delivery(self, deployment_time, details, service, source_info):
        """ Adds information about the server's deployed service into the ODB.
        """
        raise NotImplementedError()

    def add_channels_2_0(self):
        """ Adds channels new in 2.0 - cannot be added to Alembic migrations because they need access
        to already deployed services.
        """
        # Difference between 1.1 and 2.0.
        diff = (
            ('zato.cloud.aws.s3.create', 'zato.server.service.internal.cloud.aws.s3.Create'),
            ('zato.cloud.aws.s3.create.json', 'zato.server.service.internal.cloud.aws.s3.Create'),
            ('zato.cloud.aws.s3.delete', 'zato.server.service.internal.cloud.aws.s3.Delete'),
            ('zato.cloud.aws.s3.delete.json', 'zato.server.service.internal.cloud.aws.s3.Delete'),
            ('zato.cloud.aws.s3.edit', 'zato.server.service.internal.cloud.aws.s3.Edit'),
            ('zato.cloud.aws.s3.edit.json', 'zato.server.service.internal.cloud.aws.s3.Edit'),
            ('zato.cloud.aws.s3.get-list', 'zato.server.service.internal.cloud.aws.s3.GetList'),
            ('zato.cloud.aws.s3.get-list.json', 'zato.server.service.internal.cloud.aws.s3.GetList'),
            ('zato.cloud.openstack.swift.create', 'zato.server.service.internal.cloud.openstack.swift.Create'),
            ('zato.cloud.openstack.swift.create.json', 'zato.server.service.internal.cloud.openstack.swift.Create'),
            ('zato.cloud.openstack.swift.delete', 'zato.server.service.internal.cloud.openstack.swift.Delete'),
            ('zato.cloud.openstack.swift.delete.json', 'zato.server.service.internal.cloud.openstack.swift.Delete'),
            ('zato.cloud.openstack.swift.edit', 'zato.server.service.internal.cloud.openstack.swift.Edit'),
            ('zato.cloud.openstack.swift.edit.json', 'zato.server.service.internal.cloud.openstack.swift.Edit'),
            ('zato.cloud.openstack.swift.get-list', 'zato.server.service.internal.cloud.openstack.swift.GetList'),
            ('zato.cloud.openstack.swift.get-list.json', 'zato.server.service.internal.cloud.openstack.swift.GetList'),
            ('zato.definition.cassandra.create', 'zato.server.service.internal.definition.cassandra.Create'),
            ('zato.definition.cassandra.create.json', 'zato.server.service.internal.definition.cassandra.Create'),
            ('zato.definition.cassandra.delete', 'zato.server.service.internal.definition.cassandra.Delete'),
            ('zato.definition.cassandra.delete.json', 'zato.server.service.internal.definition.cassandra.Delete'),
            ('zato.definition.cassandra.edit', 'zato.server.service.internal.definition.cassandra.Edit'),
            ('zato.definition.cassandra.edit.json', 'zato.server.service.internal.definition.cassandra.Edit'),
            ('zato.definition.cassandra.get-list', 'zato.server.service.internal.definition.cassandra.GetList'),
            ('zato.definition.cassandra.get-list.json', 'zato.server.service.internal.definition.cassandra.GetList'),
            ('zato.info.get-info', 'zato.server.service.internal.info.GetInfo'),
            ('zato.info.get-info.json', 'zato.server.service.internal.info.GetInfo'),
            ('zato.info.get-server-info', 'zato.server.service.internal.info.GetServerInfo'),
            ('zato.info.get-server-info.json', 'zato.server.service.internal.info.GetServerInfo'),
            ('zato.security.apikey.change-password', 'zato.server.service.internal.security.apikey.ChangePassword'),
            ('zato.security.apikey.change-password.json', 'zato.server.service.internal.security.apikey.ChangePassword'),
            ('zato.security.apikey.create', 'zato.server.service.internal.security.apikey.Create'),
            ('zato.security.apikey.create.json', 'zato.server.service.internal.security.apikey.Create'),
            ('zato.security.apikey.delete', 'zato.server.service.internal.security.apikey.Delete'),
            ('zato.security.apikey.delete.json', 'zato.server.service.internal.security.apikey.Delete'),
            ('zato.security.apikey.edit', 'zato.server.service.internal.security.apikey.Edit'),
            ('zato.security.apikey.edit.json', 'zato.server.service.internal.security.apikey.Edit'),
            ('zato.security.apikey.get-list', 'zato.server.service.internal.security.apikey.GetList'),
            ('zato.security.apikey.get-list.json', 'zato.server.service.internal.security.apikey.GetList'),
            ('zato.security.aws.change-password', 'zato.server.service.internal.security.aws.ChangePassword'),
            ('zato.security.aws.change-password.json', 'zato.server.service.internal.security.aws.ChangePassword'),
            ('zato.security.aws.create', 'zato.server.service.internal.security.aws.Create'),
            ('zato.security.aws.create.json', 'zato.server.service.internal.security.aws.Create'),
            ('zato.security.aws.delete', 'zato.server.service.internal.security.aws.Delete'),
            ('zato.security.aws.delete.json', 'zato.server.service.internal.security.aws.Delete'),
            ('zato.security.aws.edit', 'zato.server.service.internal.security.aws.Edit'),
            ('zato.security.aws.edit.json', 'zato.server.service.internal.security.aws.Edit'),
            ('zato.security.aws.get-list', 'zato.server.service.internal.security.aws.GetList'),
            ('zato.security.aws.get-list.json', 'zato.server.service.internal.security.aws.GetList'),
            ('zato.security.ntlm.change-password', 'zato.server.service.internal.security.ntlm.ChangePassword'),
            ('zato.security.ntlm.change-password.json', 'zato.server.service.internal.security.ntlm.ChangePassword'),
            ('zato.security.ntlm.create', 'zato.server.service.internal.security.ntlm.Create'),
            ('zato.security.ntlm.create.json', 'zato.server.service.internal.security.ntlm.Create'),
            ('zato.security.ntlm.delete', 'zato.server.service.internal.security.ntlm.Delete'),
            ('zato.security.ntlm.delete.json', 'zato.server.service.internal.security.ntlm.Delete'),
            ('zato.security.ntlm.edit', 'zato.server.service.internal.security.ntlm.Edit'),
            ('zato.security.ntlm.edit.json', 'zato.server.service.internal.security.ntlm.Edit'),
            ('zato.security.ntlm.get-list', 'zato.server.service.internal.security.ntlm.GetList'),
            ('zato.security.ntlm.get-list.json', 'zato.server.service.internal.security.ntlm.GetList'),
            ('zato.security.rbac.client-role.create', 'zato.server.service.internal.security.rbac.client_role.Create'),
            ('zato.security.rbac.client-role.create.json', 'zato.server.service.internal.security.rbac.client_role.Create'),
            ('zato.security.rbac.client-role.delete', 'zato.server.service.internal.security.rbac.client_role.Delete'),
            ('zato.security.rbac.client-role.delete.json', 'zato.server.service.internal.security.rbac.client_role.Delete'),
            ('zato.security.rbac.client-role.get-client-def-list', 'zato.server.service.internal.security.rbac.client_role.GetClientDefList'),
            ('zato.security.rbac.client-role.get-client-def-list.json', 'zato.server.service.internal.security.rbac.client_role.GetClientDefList'),
            ('zato.security.rbac.permission.create', 'zato.server.service.internal.security.rbac.permission.Create'),
            ('zato.security.rbac.permission.create.json', 'zato.server.service.internal.security.rbac.permission.Create'),
            ('zato.security.rbac.permission.delete', 'zato.server.service.internal.security.rbac.permission.Delete'),
            ('zato.security.rbac.permission.delete.json', 'zato.server.service.internal.security.rbac.permission.Delete'),
            ('zato.security.rbac.permission.edit', 'zato.server.service.internal.security.rbac.permission.Edit'),
            ('zato.security.rbac.permission.edit.json', 'zato.server.service.internal.security.rbac.permission.Edit'),
            ('zato.security.rbac.role.create', 'zato.server.service.internal.security.rbac.role.Create'),
            ('zato.security.rbac.role.create.json', 'zato.server.service.internal.security.rbac.role.Create'),
            ('zato.security.rbac.role.delete', 'zato.server.service.internal.security.rbac.role.Delete'),
            ('zato.security.rbac.role.delete.json', 'zato.server.service.internal.security.rbac.role.Delete'),
            ('zato.security.rbac.role.edit', 'zato.server.service.internal.security.rbac.role.Edit'),
            ('zato.security.rbac.role.edit.json', 'zato.server.service.internal.security.rbac.role.Edit'),
            ('zato.security.rbac.role-permission.create', 'zato.server.service.internal.security.rbac.role_permission.Create'),
            ('zato.security.rbac.role-permission.create.json', 'zato.server.service.internal.security.rbac.role_permission.Create'),
            ('zato.security.rbac.role-permission.delete', 'zato.server.service.internal.security.rbac.role_permission.Delete'),
            ('zato.security.rbac.role-permission.delete.json', 'zato.server.service.internal.security.rbac.role_permission.Delete'),
            ('zato.security.xpath.change-password', 'zato.server.service.internal.security.xpath.ChangePassword'),
            ('zato.security.xpath.change-password.json', 'zato.server.service.internal.security.xpath.ChangePassword'),
            ('zato.security.xpath.create', 'zato.server.service.internal.security.xpath.Create'),
            ('zato.security.xpath.create.json', 'zato.server.service.internal.security.xpath.Create'),
            ('zato.security.xpath.delete', 'zato.server.service.internal.security.xpath.Delete'),
            ('zato.security.xpath.delete.json', 'zato.server.service.internal.security.xpath.Delete'),
            ('zato.security.xpath.edit', 'zato.server.service.internal.security.xpath.Edit'),
            ('zato.security.xpath.edit.json', 'zato.server.service.internal.security.xpath.Edit'),
            ('zato.security.xpath.get-list', 'zato.server.service.internal.security.xpath.GetList'),
            ('zato.security.xpath.get-list.json', 'zato.server.service.internal.security.xpath.GetList'),
        )

        with closing(self.session()) as session:

            cluster = session.query(Cluster).\
                filter(Cluster.id==self.cluster.id).\
                one()

            pubapi_sec = session.query(HTTPBasicAuth).\
                filter(HTTPBasicAuth.name=='pubapi').\
                filter(HTTPBasicAuth.cluster_id==self.cluster.id).\
                one()

            for channel_name, impl_name in diff:

                service = session.query(Service).\
                    filter(Service.impl_name==impl_name).\
                    filter(Service.cluster_id==self.cluster.id).\
                    one()

                channel = session.query(HTTPSOAP).\
                    filter(HTTPSOAP.name==channel_name).\
                    filter(HTTPSOAP.cluster_id==self.cluster.id).\
                    first()

                if not channel:
                    func = get_http_json_channel if 'json' in channel_name else get_http_soap_channel
                    session.add(func(channel_name.replace('.json', ''), service, cluster, pubapi_sec))

            session.commit()

# ################################################################################################################################

    def get_internal_channel_list(self, cluster_id, needs_columns=False):
        """ Returns the list of internal HTTP/SOAP channels, that is,
        channels pointing to internal services.
        """
        with closing(self.session()) as session:
            return query.internal_channel_list(session, cluster_id, needs_columns)

    def get_http_soap_list(self, cluster_id, connection=None, transport=None, needs_columns=False):
        """ Returns the list of all HTTP/SOAP connections.
        """
        with closing(self.session()) as session:
            item_list = query.http_soap_list(session, cluster_id, connection, transport, True, needs_columns)

            if connection == 'channel':
                for item in item_list:
                    item.replace_patterns_json_pointer = [elem.pattern.name for elem in session.query(HTTPSOAP).
                        filter(HTTPSOAP.id == item.id).one().replace_patterns_json_pointer]

                    item.replace_patterns_xpath = [elem.pattern.name for elem in session.query(HTTPSOAP).
                        filter(HTTPSOAP.id == item.id).one().replace_patterns_xpath]

            return item_list

# ################################################################################################################################

    def get_job_list(self, cluster_id, needs_columns=False):
        """ Returns a list of jobs defined on the given cluster.
        """
        with closing(self.session()) as session:
            return query.job_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_service_list(self, cluster_id, needs_columns=False):
        """ Returns a list of services defined on the given cluster.
        """
        with closing(self.session()) as session:
            return query.service_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_apikey_security_list(self, cluster_id, needs_columns=False):
        """ Returns a list of API keys existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.apikey_security_list(session, cluster_id, needs_columns)

    def get_aws_security_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AWS definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.aws_security_list(session, cluster_id, needs_columns)

    def get_basic_auth_list(self, cluster_id, cluster_name, needs_columns=False):
        """ Returns a list of HTTP Basic Auth definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.basic_auth_list(session, cluster_id, cluster_name, needs_columns)

    def get_jwt_list(self, cluster_id, cluster_name, needs_columns=False):
        """ Returns a list of JWT definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.jwt_list(session, cluster_id, cluster_name, needs_columns)

    def get_ntlm_list(self, cluster_id, needs_columns=False):
        """ Returns a list of NTLM definitions existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.ntlm_list(session, cluster_id, needs_columns)

    def get_oauth_list(self, cluster_id, needs_columns=False):
        """ Returns a list of OAuth accounts existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.oauth_list(session, cluster_id, needs_columns)

    def get_openstack_security_list(self, cluster_id, needs_columns=False):
        """ Returns a list of OpenStack security accounts existing on the given cluster.
        """
        with closing(self.session()) as session:
            return query.openstack_security_list(session, cluster_id, needs_columns)

    def get_tls_ca_cert_list(self, cluster_id, needs_columns=False):
        """ Returns a list of TLS CA certs on the given cluster.
        """
        with closing(self.session()) as session:
            return query.tls_ca_cert_list(session, cluster_id, needs_columns)

    def get_tls_channel_sec_list(self, cluster_id, needs_columns=False):
        """ Returns a list of definitions for securing TLS channels.
        """
        with closing(self.session()) as session:
            return query.tls_channel_sec_list(session, cluster_id, needs_columns)

    def get_tls_key_cert_list(self, cluster_id, needs_columns=False):
        """ Returns a list of TLS key/cert pairs on the given cluster.
        """
        with closing(self.session()) as session:
            return query.tls_key_cert_list(session, cluster_id, needs_columns)

    def get_wss_list(self, cluster_id, needs_columns=False):
        """ Returns a list of WS-Security definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.wss_list(session, cluster_id, needs_columns)

    def get_vault_connection_list(self, cluster_id, needs_columns=False):
        """ Returns a list of Vault connections on the given cluster.
        """
        with closing(self.session()) as session:
            return query.vault_connection_list(session, cluster_id, needs_columns)

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

    def get_definition_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.definition_amqp_list(session, cluster_id, needs_columns)

    def get_out_amqp(self, cluster_id, out_id):
        """ Returns an outgoing AMQP connection's details.
        """
        with closing(self.session()) as session:
            return query.out_amqp(session, cluster_id, out_id)

    def get_out_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing AMQP connections.
        """
        with closing(self.session()) as session:
            return query.out_amqp_list(session, cluster_id, needs_columns)

    def get_channel_amqp(self, cluster_id, channel_id):
        """ Returns a particular AMQP channel.
        """
        with closing(self.session()) as session:
            return query.channel_amqp(session, cluster_id, channel_id)

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

    def get_definition_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of IBM MQ definitions on the given cluster.
        """
        with closing(self.session()) as session:
            return query.definition_wmq_list(session, cluster_id, needs_columns)

    def get_out_wmq(self, cluster_id, out_id):
        """ Returns an outgoing IBM MQ connection's details.
        """
        with closing(self.session()) as session:
            return query.out_wmq(session, cluster_id, out_id)

    def get_out_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing IBM MQ connections.
        """
        with closing(self.session()) as session:
            return query.out_wmq_list(session, cluster_id, needs_columns)

    def get_channel_wmq(self, cluster_id, channel_id):
        """ Returns a particular IBM MQ channel.
        """
        with closing(self.session()) as session:
            return query.channel_wmq(session, cluster_id, channel_id)

    def get_channel_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of IBM MQ channels.
        """
        with closing(self.session()) as session:
            return query.channel_wmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_channel_stomp(self, cluster_id, channel_id):
        """ Returns a particular STOMP channel.
        """
        with closing(self.session()) as session:
            return query.channel_stomp(session, cluster_id, channel_id)

    def get_channel_stomp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of STOMP channels.
        """
        with closing(self.session()) as session:
            return query.channel_stomp_list(session, cluster_id, needs_columns)

    def get_out_stomp(self, cluster_id, out_id):
        """ Returns an outgoing STOMP connection's details.
        """
        with closing(self.session()) as session:
            return query.out_stomp(session, cluster_id, out_id)

    def get_out_stomp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing STOMP connections.
        """
        with closing(self.session()) as session:
            return query.out_stomp_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_zmq(self, cluster_id, out_id):
        """ Returns an outgoing ZMQ connection's details.
        """
        with closing(self.session()) as session:
            return query.out_zmq(session, cluster_id, out_id)

    def get_out_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing ZMQ connections.
        """
        with closing(self.session()) as session:
            return query.out_zmq_list(session, cluster_id, needs_columns)

    def get_channel_zmq(self, cluster_id, channel_id):
        """ Returns a particular ZMQ channel.
        """
        with closing(self.session()) as session:
            return query.channel_zmq(session, cluster_id, channel_id)

    def get_channel_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of ZMQ channels.
        """
        with closing(self.session()) as session:
            return query.channel_zmq_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_channel_web_socket(self, cluster_id, channel_id):
        """ Returns a particular WebSocket channel.
        """
        with closing(self.session()) as session:
            return query.channel_web_socket(session, cluster_id, channel_id)

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

    def get_out_odoo_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing Odoo connections.
        """
        with closing(self.session()) as session:
            return query.out_odoo_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_out_ftp(self, cluster_id, out_id):
        """ Returns an outgoing FTP connection's details.
        """
        with closing(self.session()) as session:
            return query.out_ftp(session, cluster_id, out_id)

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

    def get_xpath_list(self, cluster_id, needs_columns=False):
        """ Returns a list of XPath expressions.
        """
        with closing(self.session()) as session:
            return query.xpath_list(session, cluster_id, needs_columns)

    def get_json_pointer_list(self, cluster_id, needs_columns=False):
        """ Returns a list of JSON Pointer expressions.
        """
        with closing(self.session()) as session:
            return query.json_pointer_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def audit_set_request_http_soap(self, conn_id, name, cid, transport,
            connection, req_time, user_token, remote_addr, req_headers,
            req_payload):

        with closing(self.session()) as session:

            audit = HTTSOAPAudit()
            audit.conn_id = conn_id
            audit.cluster_id = self.cluster.id
            audit.name = name
            audit.cid = cid
            audit.transport = transport
            audit.connection = connection
            audit.req_time = req_time
            audit.user_token = user_token
            audit.remote_addr = remote_addr
            audit.req_headers = req_headers
            audit.req_payload = req_payload

            session.add(audit)
            session.commit()

# ################################################################################################################################

    def get_cloud_openstack_swift_list(self, cluster_id, needs_columns=False):
        """ Returns a list of OpenStack Swift connections.
        """
        with closing(self.session()) as session:
            return query.cloud_openstack_swift_list(session, cluster_id, needs_columns)

    def get_cloud_aws_s3_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AWS S3 connections.
        """
        with closing(self.session()) as session:
            return query.cloud_aws_s3_list(session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_pubsub_topic_list(self, cluster_id, needs_columns=False):
        """ Returns a list of pub/sub topics defined in a cluster.
        """
        return query.pubsub_topic_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_pubsub_subscription_list(self, cluster_id, needs_columns=False):
        """ Returns a list of pub/sub subscriptions defined in a cluster.
        """
        return query_ps_subscription.pubsub_subscription_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################

    def get_notif_cloud_openstack_swift_list(self, cluster_id, needs_columns=False):
        """ Returns a list of OpenStack Swift notification definitions.
        """
        return query.notif_cloud_openstack_swift_list(self._session, cluster_id, needs_columns)

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
        return query.pubsub_endpoint_list(self._session, cluster_id, needs_columns)

# ################################################################################################################################
