# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from ftplib import FTP_PORT

# SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, \
    LargeBinary, Sequence, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import backref, relationship

# Zato
from zato.common.api import AMQP, HTTP_SOAP_SERIALIZATION_TYPE, MISC, ODOO, SAP, SCHEDULER, PARAMS_PRIORITY, \
    URL_PARAMS_PRIORITY
from zato.common.json_internal import json_dumps
from zato.common.odb.model.base import Base, _JSON

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import boolnone, floatnone, intnone, strnone
    boolnone = boolnone
    floatnone = floatnone
    intnone = intnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

def to_json(model, return_as_dict=False):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    out = {}
    out['fields'] = {}
    out['pk'] = getattr(model, 'id', None)

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        out['fields'][col.name] = getattr(model, col.name)

    if return_as_dict:
        return out
    else:
        return json_dumps([out])

# ################################################################################################################################

class AlembicRevision(Base):
    """ A table for Alembic to store its revision IDs for SQL migrations.
    Note that Alembic as of version 0.6.0 which is the latest one right now (Sun, Jun 8 2014)
    doesn't declare 'version_num' to be a primary key but we need to because SQLAlchemy always needs one.
    """
    __tablename__ = 'alembic_version'
    version_num = Column(String(32), primary_key=True)

    def __init__(self, version_num=None):
        self.version_num = version_num

# ################################################################################################################################

class ZatoInstallState(Base):
    """ Contains a row for each Zato installation belonging to that particular
    ODB. For instance, installing Zato 1.0 will add a new row, installing 1.1
    """
    __tablename__ = 'install_state'

    id = Column(Integer, Sequence('install_state_seq'), primary_key=True)
    version = Column(Integer, unique=True, nullable=False)
    install_time = Column(DateTime(), nullable=False)
    source_host = Column(String(200), nullable=False)
    source_user = Column(String(200), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    def __init__(self, id=None, version=None, install_time=None, source_host=None, source_user=None):
        self.id = id
        self.version = version
        self.install_time = install_time
        self.source_host = source_host
        self.source_user = source_user

# ################################################################################################################################

class Cluster(Base):
    """ Represents a Zato cluster.
    """
    __tablename__ = 'cluster'

    id = Column(Integer, Sequence('cluster_id_seq'), primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    odb_type = Column(String(30), nullable=False)
    odb_host = Column(String(200), nullable=True)
    odb_port = Column(Integer(), nullable=True)
    odb_user = Column(String(200), nullable=True)
    odb_db_name = Column(String(200), nullable=True)
    odb_schema = Column(String(200), nullable=True)
    broker_host = Column(String(200), nullable=False, default='broker-host-unused')
    broker_port = Column(Integer(), nullable=False, default=998877)
    cw_srv_id = Column(Integer(), nullable=True)
    cw_srv_keep_alive_dt = Column(DateTime(), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    def __init__(self, id=None, name=None, description=None, odb_type=None, odb_host=None, odb_port=None, odb_user=None,
            odb_db_name=None, odb_schema=None, broker_host=None, broker_port=None, cw_srv_id=None, cw_srv_keep_alive_dt=None):
        self.id = id
        self.name = name
        self.description = description
        self.odb_type = odb_type
        self.odb_host = odb_host
        self.odb_port = odb_port
        self.odb_user = odb_user
        self.odb_db_name = odb_db_name
        self.odb_schema = odb_schema
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.cw_srv_id = cw_srv_id
        self.cw_srv_keep_alive_dt = cw_srv_keep_alive_dt

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class Server(Base):
    """ Represents a Zato server.
    """
    __tablename__ = 'server'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('server_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    host = Column(String(400), nullable=True)

    bind_host = Column(String(400), nullable=True)
    bind_port = Column(Integer(), nullable=True)
    preferred_address = Column(String(400), nullable=True)
    crypto_use_tls = Column(Boolean(), nullable=True)

    # If the server's request to join a cluster has been accepted, and for now
    # it will always be.
    last_join_status = Column(String(40), nullable=True)
    last_join_mod_date = Column(DateTime(), nullable=True)
    last_join_mod_by = Column(String(200), nullable=True)

    # Whether the server's up or not
    up_status = Column(String(40), nullable=True)
    up_mod_date = Column(DateTime(), nullable=True)

    token = Column(String(32), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('servers', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, cluster=None, token=None, last_join_status=None, last_join_mod_date=None,
            last_join_mod_by=None):
        self.id = id
        self.name = name
        self.cluster = cluster
        self.token = token
        self.last_join_status = last_join_status
        self.last_join_mod_date = last_join_mod_date
        self.last_join_mod_by = last_join_mod_by
        self.may_be_deleted = None # Not used by the database
        self.up_mod_date_user = None # Not used by the database

# ################################################################################################################################

class SecurityBase(Base):
    """ A base class for all the security definitions.
    """
    __tablename__ = 'sec_base'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'),
        UniqueConstraint('cluster_id', 'username', 'sec_type'), {})
    __mapper_args__ = {'polymorphic_on': 'sec_type'}

    id = Column(Integer, Sequence('sec_base_seq'), primary_key=True)
    name = Column(String(200), nullable=False)

    # It's nullable because some children classes do not use usernames
    username = Column(String(200), nullable=True)

    password = Column(String(1000), nullable=True)
    password_type = Column(String(45), nullable=True)
    is_active = Column(Boolean(), nullable=False)
    sec_type = Column(String(45), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('security_list', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class MultiSecurity(Base):
    """ An N:N mapping between security definitions and objects making use of them.
    """
    __tablename__ = 'sec_multi'
    __table_args__ = (UniqueConstraint('cluster_id', 'conn_id', 'conn_type', 'security_id', 'is_channel', 'is_outconn'), {})

    id = Column(Integer, Sequence('sec_multi_seq'), primary_key=True)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    priority = Column(Integer(), nullable=False)
    conn_id = Column(String(100), nullable=False)
    conn_type = Column(String(100), nullable=False)

    is_channel = Column(Boolean(), nullable=False)
    is_outconn = Column(Boolean(), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False)
    security = relationship(SecurityBase, backref=backref('sec_multi_list', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('sec_multi_list', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class HTTPBasicAuth(SecurityBase):
    """ An HTTP Basic Auth definition.
    """
    __tablename__ = 'sec_basic_auth'
    __mapper_args__ = {'polymorphic_identity': 'basic_auth'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    realm = Column(String(200), nullable=False)

    def __init__(self, id=None, name=None, is_active=None, username=None, realm=None, password=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.realm = realm
        self.password = password
        self.cluster = cluster

# ################################################################################################################################

class OAuth(SecurityBase):
    """ Stores OAuth credentials.
    """
    __tablename__ = 'sec_oauth'
    __mapper_args__ = {'polymorphic_identity':'oauth'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    proto_version = Column(String(32), nullable=False)
    sig_method = Column(String(32), nullable=False) # HMAC-SHA1 or PLAINTEXT
    max_nonce_log = Column(Integer(), nullable=False)

    def __init__(self, id=None, name=None, is_active=None, username=None, password=None, proto_version=None, sig_method=None,
            max_nonce_log=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.proto_version = proto_version
        self.sig_method = sig_method
        self.max_nonce_log = max_nonce_log
        self.cluster = cluster

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class NTLM(SecurityBase):
    """ Stores NTLM definitions.
    """
    __tablename__ = 'sec_ntlm'
    __mapper_args__ = {'polymorphic_identity': 'ntlm'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)

    def __init__(self, id=None, name=None, is_active=None, username=None, password=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.cluster = cluster

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class APIKeySecurity(SecurityBase):
    """ Stores API keys.
    """
    __tablename__ = 'sec_apikey'
    __mapper_args__ = {'polymorphic_identity': 'apikey'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)

    def __init__(self, id=None, name=None, is_active=None, username=None, password=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.cluster = cluster
        self.header = None # Not used by the DB

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class HTTPSOAP(Base):
    """ An incoming or outgoing HTTP/SOAP connection.
    """
    __tablename__ = 'http_soap'
    __table_args__ = (
        UniqueConstraint('name', 'connection', 'transport', 'cluster_id'),
        Index('path_host_conn_act_clus_idx', 'url_path', 'host', 'connection', 'soap_action', 'cluster_id', unique=False), {})

    id = Column(Integer, Sequence('http_soap_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    connection = Column(String(20), nullable=False)
    transport = Column(String(200), nullable=False)

    host = Column(String(200), nullable=True)
    url_path = Column(String(200), nullable=False)
    method = Column(String(200), nullable=True)
    content_encoding = Column(String(200), nullable=True)

    soap_action = Column(String(200), nullable=False)
    soap_version = Column(String(20), nullable=True)

    data_format = Column(String(20), nullable=True)
    content_type = Column(String(200), nullable=True)

    ping_method = Column(String(60), nullable=True)
    pool_size = Column(Integer, nullable=True)
    serialization_type = Column(String(200), nullable=False, default=HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id)
    timeout = Column(Integer(), nullable=False, default=MISC.DEFAULT_HTTP_TIMEOUT)

    merge_url_params_req = Column(Boolean, nullable=True, default=True)
    url_params_pri = Column(String(200), nullable=True, default=URL_PARAMS_PRIORITY.DEFAULT)
    params_pri = Column(String(200), nullable=True, default=PARAMS_PRIORITY.DEFAULT)

    cache_expiry = Column(Integer, nullable=True, default=0)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)
    security = relationship(SecurityBase, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    cache_id = Column(Integer, ForeignKey('cache.id', ondelete='CASCADE'), nullable=True)
    cache = relationship('Cache', backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    service = relationship('Service', backref=backref('http_soap', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, is_internal=None, connection=None, transport=None, host=None,
            url_path=None, method=None, soap_action=None, soap_version=None, data_format=None, ping_method=None,
            pool_size=None, merge_url_params_req=None, url_params_pri=None, params_pri=None, serialization_type=None,
            timeout=None, service_id=None, service=None, security=None, cluster_id=None,
            cluster=None, service_name=None, security_id=None, security_name=None, content_type=None,
            cache_id=None, cache_type=None, cache_expiry=None, cache_name=None, content_encoding=None, match_slash=None,
            http_accept=None, opaque=None, **kwargs):
        super(HTTPSOAP, self).__init__(**kwargs)
        self.id = id
        self.name = name
        self.is_active = is_active
        self.is_internal = is_internal
        self.connection = connection
        self.transport = transport
        self.host = host
        self.url_path = url_path
        self.method = method
        self.soap_action = soap_action
        self.soap_version = soap_version
        self.data_format = data_format
        self.ping_method = ping_method
        self.pool_size = pool_size
        self.merge_url_params_req = merge_url_params_req
        self.url_params_pri = url_params_pri
        self.params_pri = params_pri
        self.serialization_type = serialization_type
        self.timeout = timeout
        self.service_id = service_id
        self.service = service
        self.security = security
        self.cluster_id = cluster_id
        self.cluster = cluster
        self.service_name = service_name # Not used by the DB
        self.security_id = security_id
        self.security_name = security_name
        self.content_type = content_type
        self.cache_id = cache_id
        self.cache_type = cache_type
        self.cache_expiry = cache_expiry
        self.cache_name = cache_name # Not used by the DB
        self.content_encoding = content_encoding
        self.match_slash = match_slash # Not used by the DB
        self.http_accept = http_accept # Not used by the DB
        self.opaque1 = opaque
        self.is_wrapper = None
        self.wrapper_type = None
        self.password = None
        self.security_groups_count = None
        self.security_groups_member_count = None

# ################################################################################################################################

class SQLConnectionPool(Base):
    """ An SQL connection pool.
    """
    __tablename__ = 'sql_pool'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'), {})

    id = Column(Integer, Sequence('sql_pool_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    db_name = Column(String(200), nullable=False)
    engine = Column(String(200), nullable=False)
    extra = Column(LargeBinary(20000), nullable=True)
    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    pool_size = Column(Integer(), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('sql_pools', order_by=name, cascade='all, delete, delete-orphan'))

    engine_display_name = None # For auto-completion, not used by DB

    def __init__(self, id=None, name=None, is_active=None, db_name=None, username=None, engine=None, extra=None, host=None,
            port=None, pool_size=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.db_name = db_name
        self.username = username
        self.engine = engine
        self.extra = extra
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.cluster = cluster

# ################################################################################################################################

class Service(Base):
    """ A set of basic informations about a service available in a given cluster.
    """
    __tablename__ = 'service'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('service_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    impl_name = Column(String(2000), nullable=False)
    is_internal = Column(Boolean(), nullable=False)
    wsdl = Column(LargeBinary(5000000), nullable=True)
    wsdl_name = Column(String(200), nullable=True)

    slow_threshold = Column(Integer, nullable=False, default=99999)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('services', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, impl_name=None, is_internal=None, cluster=None, wsdl=None,
            wsdl_name=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.impl_name = impl_name
        self.is_internal = is_internal
        self.cluster = cluster
        self.wsdl = wsdl
        self.wsdl_name = wsdl_name
        self.plain_http_channels = [] # Not used by the database
        self.soap_channels = [] # Not used by the database
        self.amqp_channels = [] # Not used by the database
        self.scheduler_jobs = [] # Not used by the database
        self.deployment_info = [] # Not used by the database
        self.source_info = None # Not used by the database
        self.may_be_deleted = False # Not used by the database


# ################################################################################################################################

class DeployedService(Base):
    """ A service living on a given server.
    """
    __tablename__ = 'deployed_service'
    __table_args__ = (UniqueConstraint('server_id', 'service_id'), {})

    deployment_time = Column(DateTime(), nullable=False)
    details = Column(String(2000), nullable=False)
    source = Column(LargeBinary(500000), nullable=True)
    source_path = Column(String(2000), nullable=True)
    source_hash = Column(String(512), nullable=True)
    source_hash_method = Column(String(20), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    server = relationship(Server, backref=backref('deployed_services', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    service = relationship(Service, backref=backref('deployment_data', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    def __init__(self, deployment_time, details, server_id, service_id, source, source_path, source_hash, source_hash_method):
        self.deployment_time = deployment_time
        self.details = details
        self.server_id = server_id
        self.service_id = service_id
        self.source = source
        self.source_path = source_path
        self.source_hash = source_hash
        self.source_hash_method = source_hash_method

# ################################################################################################################################

class Job(Base):
    """ A scheduler's job. Stores all the information needed to execute a job
    if it's a one-time job, otherwise the information is kept in related tables.
    """
    __tablename__ = 'job'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('job_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    job_type = Column(Enum(SCHEDULER.JOB_TYPE.ONE_TIME, SCHEDULER.JOB_TYPE.INTERVAL_BASED,
                           SCHEDULER.JOB_TYPE.CRON_STYLE, name='job_type'), nullable=False)
    start_date = Column(DateTime(), nullable=False)
    extra = Column(LargeBinary(500000), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('jobs', order_by=name, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('jobs', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, job_type=None, start_date=None, extra=None, cluster=None,
            cluster_id=None, service=None, service_id=None, service_name=None, interval_based=None, cron_style=None,
            definition_text=None, job_type_friendly=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.job_type = job_type
        self.start_date = start_date
        self.extra = extra
        self.cluster = cluster
        self.cluster_id = cluster_id
        self.service = service
        self.service_id = service_id
        self.service_name = service_name # Not used by the database
        self.interval_based = interval_based
        self.cron_style = cron_style
        self.definition_text = definition_text # Not used by the database
        self.job_type_friendly = job_type_friendly # Not used by the database

# ################################################################################################################################

class IntervalBasedJob(Base):
    """ A Cron-style scheduler's job.
    """
    __tablename__ = 'job_interval_based'
    __table_args__ = (UniqueConstraint('job_id'), {})

    id = Column(Integer, Sequence('job_intrvl_seq'), primary_key=True)
    job_id = Column(Integer, nullable=False)

    weeks = Column(Integer, nullable=True)
    days = Column(Integer, nullable=True)
    hours = Column(Integer, nullable=True)
    minutes = Column(Integer, nullable=True)
    seconds = Column(Integer, nullable=True)
    repeats = Column(Integer, nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    job_id = Column(Integer, ForeignKey('job.id', ondelete='CASCADE'), nullable=False)
    job = relationship(Job, backref=backref('interval_based', uselist=False, cascade='all, delete, delete-orphan', single_parent=True))

    def __init__(self, id=None, job=None, weeks=None, days=None, hours=None, minutes=None, seconds=None, repeats=None,
            definition_text=None):
        self.id = id
        self.job = job
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.repeats = repeats
        self.definition_text = definition_text # Not used by the database

# ################################################################################################################################

class CronStyleJob(Base):
    """ A Cron-style scheduler's job.
    """
    __tablename__ = 'job_cron_style'
    __table_args__ = (UniqueConstraint('job_id'), {})

    id = Column(Integer, Sequence('job_cron_seq'), primary_key=True)
    cron_definition = Column(String(4000), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    job_id = Column(Integer, ForeignKey('job.id', ondelete='CASCADE'), nullable=False)
    job = relationship(
        Job, backref=backref('cron_style', uselist=False, cascade='all, delete, delete-orphan', single_parent=True))

    def __init__(self, id=None, job=None, cron_definition=None):
        self.id = id
        self.job = job
        self.cron_definition = cron_definition

# ################################################################################################################################

class Cache(Base):
    """ Base class for all cache definitions.
    """
    __tablename__ = 'cache'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})
    __mapper_args__ = {'polymorphic_on': 'cache_type'}

    id = Column(Integer, Sequence('cache_builtin_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_default = Column(Boolean(), nullable=False)
    cache_type = Column(String(45), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('cache_list', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self):
        self.current_size = 0 # Not used by the DB

# ################################################################################################################################

class CacheBuiltin(Cache):
    """ Cache definitions using mechanisms built into Zato.
    """
    __tablename__ = 'cache_builtin'
    __mapper_args__ = {'polymorphic_identity':'builtin'}

    cache_id = Column(Integer, ForeignKey('cache.id'), primary_key=True)
    max_size = Column(Integer(), nullable=False)
    max_item_size = Column(Integer(), nullable=False)
    extend_expiry_on_get = Column(Boolean(), nullable=False)
    extend_expiry_on_set = Column(Boolean(), nullable=False)
    sync_method = Column(String(20), nullable=False)
    persistent_storage = Column(String(40), nullable=False)

    def __init__(self, cluster=None):
        self.cluster = cluster

# ################################################################################################################################

class OutgoingAMQP(Base):
    """ An outgoing AMQP connection.
    """
    __tablename__ = 'out_amqp'
    __table_args__ = (UniqueConstraint('name',), {})

    id = Column(Integer, Sequence('out_amqp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    vhost = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    frame_max = Column(Integer(), nullable=False)
    heartbeat = Column(Integer(), nullable=False)

    delivery_mode = Column(SmallInteger(), nullable=False)
    priority = Column(SmallInteger(), server_default=str(AMQP.DEFAULT.PRIORITY), nullable=False)

    content_type = Column(String(200), nullable=True)
    content_encoding = Column(String(200), nullable=True)
    expiration = Column(Integer(), nullable=True)
    user_id = Column(String(200), nullable=True)
    app_id = Column(String(200), nullable=True)
    pool_size = Column(SmallInteger(), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    def __init__(self, id=None, name=None, is_active=None, delivery_mode=None, priority=None, content_type=None,
            content_encoding=None, expiration=None, user_id=None, app_id=None, delivery_mode_text=None,
            def_name=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.delivery_mode = delivery_mode
        self.priority = priority
        self.content_type = content_type
        self.content_encoding = content_encoding
        self.expiration = expiration
        self.user_id = user_id
        self.app_id = app_id
        self.delivery_mode_text = delivery_mode_text # Not used by the DB
        self.def_name = def_name # Not used by the DB

# ################################################################################################################################

class OutgoingFTP(Base):
    """ An outgoing FTP connection.
    """
    __tablename__ = 'out_ftp'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('out_ftp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(200), nullable=False)
    user = Column(String(200), nullable=True)
    password = Column(String(200), nullable=True)
    acct = Column(String(200), nullable=True)
    timeout = Column(Integer, nullable=True)
    port = Column(Integer, server_default=str(FTP_PORT), nullable=False)
    dircache = Column(Boolean(), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_ftp', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, host=None, user=None, password=None, acct=None, timeout=None,
            port=None, dircache=None, cluster_id=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.host = host
        self.user = user
        self.password = password
        self.acct = acct
        self.timeout = timeout
        self.port = port
        self.dircache = dircache
        self.cluster_id = cluster_id

# ################################################################################################################################

class OutgoingOdoo(Base):
    """ An outgoing Odoo connection.
    """
    __tablename__ = 'out_odoo'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('out_odoo_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False, server_default=str(ODOO.DEFAULT.PORT))
    user = Column(String(200), nullable=False)
    database = Column(String(200), nullable=False)
    protocol = Column(String(200), nullable=False)
    pool_size = Column(Integer(), nullable=False, server_default=str(ODOO.DEFAULT.POOL_SIZE))
    password = Column(String(400), nullable=False)
    client_type = Column(String(40), nullable=False, server_default=str(ODOO.CLIENT_TYPE.OPENERP_CLIENT_LIB))

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_odoo', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, cluster=None):
        self.cluster = cluster
        self.protocol_name = None # Not used by the DB

# ################################################################################################################################

class OutgoingSAP(Base):
    """ An outgoing SAP RFC connection.
    """
    __tablename__ = 'out_sap'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('out_sap_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(200), nullable=False)
    sysnr = Column(String(3), nullable=True, server_default=str(SAP.DEFAULT.INSTANCE))
    user = Column(String(200), nullable=False)
    client = Column(String(4), nullable=False)
    sysid = Column(String(4), nullable=False)
    password = Column(String(400), nullable=False)
    pool_size = Column(Integer(), nullable=False, server_default=str(SAP.DEFAULT.POOL_SIZE))
    router = Column(String(400), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_sap', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, cluster=None):
        self.cluster = cluster

# ################################################################################################################################

class ChannelAMQP(Base):
    """ An incoming AMQP connection.
    """
    __tablename__ = 'channel_amqp'
    __table_args__ = (UniqueConstraint('name',), {})

    id = Column(Integer, Sequence('channel_amqp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    vhost = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    frame_max = Column(Integer(), nullable=False)
    heartbeat = Column(Integer(), nullable=False)

    queue = Column(String(200), nullable=False)
    consumer_tag_prefix = Column(String(200), nullable=False)
    pool_size = Column(Integer, nullable=False)
    ack_mode = Column(String(20), nullable=False)
    prefetch_count = Column(Integer, nullable=False)
    data_format = Column(String(20), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('channels_amqp', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, queue=None, consumer_tag_prefix=None,
            service_name=None, data_format=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.queue = queue
        self.consumer_tag_prefix = consumer_tag_prefix
        self.service_name = service_name # Not used by the DB
        self.data_format = data_format

# ################################################################################################################################

class DeploymentPackage(Base):
    """ A package to be deployed onto a server, either a plain .py/.pyw or
    a Distutils2 archive.
    """
    __tablename__ = 'deployment_package'

    id = Column(Integer, Sequence('depl_package_seq'), primary_key=True)
    deployment_time = Column(DateTime(), nullable=False)
    details = Column(String(2000), nullable=False)

    payload_name = Column(String(200), nullable=False)
    payload = Column(LargeBinary(5000000), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    server = relationship(
        Server, backref=backref('originating_deployment_packages',
            order_by=deployment_time, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, deployment_time=None, details=None, payload_name=None, payload=None):
        self.id = id
        self.deployment_time = deployment_time
        self.details = details
        self.payload_name = payload_name
        self.payload = payload

# ################################################################################################################################

class DeploymentStatus(Base):
    """ Whether a server has already deployed a given package.
    """
    __tablename__ = 'deployment_status'
    __table_args__ = (UniqueConstraint('package_id', 'server_id'), {})

    id = Column(Integer, Sequence('depl_status_seq'), primary_key=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    package_id = Column(
        Integer, ForeignKey('deployment_package.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    package = relationship(
        DeploymentPackage, backref=backref('deployment_status_list', order_by=package_id, cascade='all, delete, delete-orphan'))

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    server = relationship(
        Server, backref=backref('deployment_status_list', order_by=server_id, cascade='all, delete, delete-orphan'))

    # See zato.common.DEPLOYMENT_STATUS
    status = Column(String(20), nullable=False)
    status_change_time = Column(DateTime(), nullable=False)

    def __init__(self, package_id=None, server_id=None, status=None, status_change_time=None):
        self.package_id = package_id
        self.server_id = server_id
        self.status = status
        self.status_change_time = status_change_time

# ################################################################################################################################

class ElasticSearch(Base):
    __tablename__ = 'search_es'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('search_es_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False, default=True)
    hosts = Column(String(400), nullable=False)
    timeout = Column(Integer(), nullable=False)
    body_as = Column(String(45), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('search_es_conns', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class SMTP(Base):
    __tablename__ = 'email_smtp'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('email_smtp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(400), nullable=False)
    port = Column(Integer(), nullable=False)
    timeout = Column(Integer(), nullable=False)
    is_debug = Column(Boolean(), nullable=False)
    username = Column(String(400), nullable=True)
    password = Column(String(400), nullable=True)
    mode = Column(String(20), nullable=False)
    ping_address = Column(String(200), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('smtp_conns', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class IMAP(Base):
    __tablename__ = 'email_imap'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('email_imap_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    host = Column(String(400), nullable=False)
    port = Column(Integer(), nullable=False)
    timeout = Column(Integer(), nullable=False)
    debug_level = Column(Integer(), nullable=False)
    username = Column(String(400), nullable=True)
    password = Column(String(400), nullable=True)
    mode = Column(String(20), nullable=False)
    get_criteria = Column(String(2000), nullable=False)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('imap_conns', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class GenericObject(Base):
    """ A generic data object.
    """
    __tablename__ = 'generic_object'
    __table_args__ = (
        Index('gen_obj_uq_name_type', 'name', 'type_', 'cluster_id', unique=True,
              mysql_length={'name':191, 'type_':191}),
        Index('gen_obj_par_id', 'cluster_id', 'parent_id', 'parent_type', unique=False,
              mysql_length={'parent_id':191, 'parent_type':191}),
        Index('gen_obj_cat_id', 'cluster_id', 'category_id', unique=False,
              mysql_length={'category_id':191}),
        Index('gen_obj_cat_subcat_id', 'cluster_id', 'category_id', 'subcategory_id', unique=False,
              mysql_length={'category_id':191, 'subcategory_id':191}),
        Index('gen_obj_cat_name', 'cluster_id', 'category_name', unique=False,
              mysql_length={'category_name':191}),
        Index('gen_obj_cat_subc_name', 'cluster_id', 'category_name', 'subcategory_name', unique=False,
              mysql_length={'category_name':191, 'subcategory_name':191}),
        Index('gen_obj_par_obj_id', 'cluster_id', 'parent_object_id', unique=False),
    {})

    id = Column(Integer, Sequence('generic_object_seq'), primary_key=True)
    name = Column(Text(191), nullable=False)

    type_ = Column(Text(191), nullable=False)
    subtype = Column(Text(191), nullable=True)

    category_id = Column(Text(191), nullable=True)
    subcategory_id = Column(Text(191), nullable=True)

    creation_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    category_name = Column(Text(191), nullable=True)
    subcategory_name = Column(Text(191), nullable=True)

    # This references back to generic objects
    parent_object_id = Column(Integer, nullable=True)

    # This may reference objects other than the current model
    parent_id = Column(Text(191), nullable=True)
    parent_type = Column(Text(191), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    generic_conn_def_id = Column(Integer, ForeignKey('generic_conn_def.id', ondelete='CASCADE'), nullable=True)
    generic_conn_def_sec_id = Column(Integer, ForeignKey('generic_conn_def_sec.id', ondelete='CASCADE'), nullable=True)
    generic_conn_id = Column(Integer, ForeignKey('generic_conn.id', ondelete='CASCADE'), nullable=True)
    generic_conn_sec_id = Column(Integer, ForeignKey('generic_conn_sec.id', ondelete='CASCADE'), nullable=True)
    generic_conn_client_id = Column(Integer, ForeignKey('generic_conn_client.id', ondelete='CASCADE'), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('generic_object_list', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class GenericConnDef(Base):
    """ Generic connection definitions - with details kept in JSON.
    """
    __tablename__ = 'generic_conn_def'
    __table_args__ = (
        UniqueConstraint('name', 'type_', 'cluster_id'),
    {})

    id = Column(Integer, Sequence('generic_conn_def_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    type_ = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)
    cache_expiry = Column(Integer, nullable=True, default=0)
    address = Column(Text(), nullable=True)
    port = Column(Integer, nullable=True)
    timeout = Column(Integer, nullable=True)
    data_format = Column(String(60), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    # Both are needed because some connections can be duplex
    is_channel = Column(Boolean(), nullable=False)
    is_outconn = Column(Boolean(), nullable=False)

    version = Column(String(200), nullable=True)
    extra = Column(Text(), nullable=True)
    pool_size = Column(Integer(), nullable=False)

    # This can be used if only one security definition should be assigned to the object
    username = Column(String(1000), nullable=True)
    username_type = Column(String(45), nullable=True)
    secret = Column(String(1000), nullable=True)
    secret_type = Column(String(45), nullable=True)

    cache_id = Column(Integer, ForeignKey('cache.id', ondelete='CASCADE'), nullable=True)
    cache = relationship('Cache', backref=backref('generic_conn_def_list', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('generic_conn_def_list', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class GenericConnDefSec(Base):
    """ N:N security mappings for generic connection definitions.
    """
    __tablename__ = 'generic_conn_def_sec'
    __table_args__ = (
        UniqueConstraint('conn_def_id', 'sec_base_id', 'cluster_id'),
    {})

    id = Column(Integer, Sequence('generic_conn_def_sec_seq'), primary_key=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    conn_def_id = Column(Integer, ForeignKey('generic_conn_def.id', ondelete='CASCADE'), nullable=False)
    conn_def = relationship(GenericConnDef, backref=backref('generic_conn_def_sec_list', order_by=id,
        cascade='all, delete, delete-orphan'))

    sec_base_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False)
    sec_base = relationship(SecurityBase, backref=backref('generic_conn_def_sec_list', order_by=id,
        cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('generic_conn_def_sec_list', order_by=id,
        cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class GenericConn(Base):
    """ Generic connections - with details kept in JSON.
    """
    __tablename__ = 'generic_conn'
    __table_args__ = (
        UniqueConstraint('name', 'type_', 'cluster_id'),
    {})

    id = Column(Integer, Sequence('generic_conn_def_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    type_ = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)
    cache_expiry = Column(Integer, nullable=True, default=0)
    address = Column(Text(), nullable=True)
    port = Column(Integer, nullable=True)
    timeout = Column(Integer, nullable=True)
    data_format = Column(String(60), nullable=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    # Both are needed because some connections can be duplex
    is_channel = Column(Boolean(), nullable=False)
    is_outconn = Column(Boolean(), nullable=False)

    version = Column(String(200), nullable=True)
    extra = Column(Text(), nullable=True)
    pool_size = Column(Integer(), nullable=False)

    # This can be used if only one security definition should be assigned to the object
    username = Column(String(1000), nullable=True)
    username_type = Column(String(45), nullable=True)
    secret = Column(String(1000), nullable=True)
    secret_type = Column(String(45), nullable=True)

    # Some connections will have a connection definition assigned
    conn_def_id = Column(Integer, ForeignKey('generic_conn_def.id', ondelete='CASCADE'), nullable=True)
    conn_def = relationship(GenericConnDef, backref=backref('generic_conn_def_list',
        order_by=id, cascade='all, delete, delete-orphan'))

    cache_id = Column(Integer, ForeignKey('cache.id', ondelete='CASCADE'), nullable=True)
    cache = relationship('Cache', backref=backref('generic_conn_list', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('generic_conn_list', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class GenericConnSec(Base):
    """ N:N security mappings for generic connections.
    """
    __tablename__ = 'generic_conn_sec'
    __table_args__ = (
        UniqueConstraint('conn_id', 'sec_base_id', 'cluster_id'),
    {})

    id = Column(Integer, Sequence('generic_conn_sec_seq'), primary_key=True)

    # JSON data is here
    opaque1 = Column(_JSON(), nullable=True)

    conn_id = Column(Integer, ForeignKey('generic_conn.id', ondelete='CASCADE'), nullable=False)
    conn = relationship(GenericConn, backref=backref('generic_conn_list', order_by=id,
        cascade='all, delete, delete-orphan'))

    sec_base_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False)
    sec_base = relationship(SecurityBase, backref=backref('generic_conn_sec_list', order_by=id,
        cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('generic_conn_sec_list', order_by=id,
        cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class GenericConnClient(Base):
    """ A live client connection.
    """
    __tablename__ = 'generic_conn_client'
    __table_args__ = (
        Index('gen_conn_cli_idx', 'cluster_id', 'pub_client_id', unique=False),
        Index('gen_conn_cli_ext_n_idx', 'cluster_id', 'ext_client_name', unique=False),
        Index('gen_conn_cli_ext_i_idx', 'cluster_id', 'ext_client_id', unique=False),
        Index('gen_conn_cli_pr_addr_idx', 'cluster_id', 'peer_address', unique=False),
        Index('gen_conn_cli_pr_fqdn_idx', 'cluster_id', 'peer_fqdn', unique=False),
    {})

    # This ID is for SQL
    id = Column(Integer, Sequence('generic_conn_client_seq'), primary_key=True)

    is_internal = Column(Boolean(), nullable=False)

    # This one is assigned by Zato
    pub_client_id = Column(String(200), nullable=False)

    # These are assigned by clients themselves
    ext_client_id = Column(String(200), nullable=False)
    ext_client_name = Column(String(200), nullable=True)

    local_address = Column(String(400), nullable=False)
    peer_address = Column(String(400), nullable=False)
    peer_fqdn = Column(String(400), nullable=False)

    connection_time = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)

    server_proc_pid = Column(Integer, nullable=True)
    server_name = Column(String(200), nullable=True) # References server.name

    conn_id = Column(Integer, ForeignKey('generic_conn.id', ondelete='CASCADE'), nullable=False)
    conn = relationship(
        GenericConn, backref=backref('clients', order_by=local_address, cascade='all, delete, delete-orphan'))

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=True)
    server = relationship(
        Server, backref=backref('gen_conn_clients', order_by=local_address, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(
        Cluster, backref=backref('gen_conn_clients', order_by=last_seen, cascade='all, delete, delete-orphan'))

# ################################################################################################################################
