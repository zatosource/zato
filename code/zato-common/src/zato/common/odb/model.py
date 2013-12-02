# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from ftplib import FTP_PORT
from json import dumps

# SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Sequence, \
     Boolean, LargeBinary, UniqueConstraint, Enum, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

# Zato
from zato.common import INVOCATION_TARGET, MISC, MSG_PATTERN_TYPE, SCHEDULER_JOB_TYPE
from zato.common.odb import AMQP_DEFAULT_PRIORITY, WMQ_DEFAULT_PRIORITY

Base = declarative_base()

################################################################################

def to_json(model):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    json = {}
    json['fields'] = {}
    json['pk'] = getattr(model, 'id')

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json['fields'][col.name] = getattr(model, col.name)

    return dumps([json])

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

    def __init__(self, id=None, version=None, install_time=None, source_host=None,
                 source_user=None):
        self.id = id
        self.version = version
        self.install_time = install_time
        self.source_host = source_host
        self.source_user = source_user

class Cluster(Base):
    """ Represents a Zato cluster.
    """
    __tablename__ = 'cluster'

    id = Column(Integer, Sequence('cluster_id_seq'), primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    odb_type = Column(String(30), nullable=False)
    odb_host = Column(String(200), nullable=False)
    odb_port = Column(Integer(), nullable=False)
    odb_user = Column(String(200), nullable=False)
    odb_db_name = Column(String(200), nullable=False)
    odb_schema = Column(String(200), nullable=True)
    broker_host = Column(String(200), nullable=False)
    broker_port = Column(Integer(), nullable=False)
    lb_host = Column(String(200), nullable=False)
    lb_port = Column(Integer(), nullable=False)
    lb_agent_port = Column(Integer(), nullable=False)
    cw_srv_id = Column(Integer(), nullable=True)
    cw_srv_keep_alive_dt = Column(DateTime(), nullable=True)

    def __init__(self, id=None, name=None, description=None, odb_type=None,
                 odb_host=None, odb_port=None, odb_user=None, odb_db_name=None,
                 odb_schema=None, broker_host=None,
                 broker_port=None, lb_host=None, lb_port=None,
                 lb_agent_port=None, cw_srv_id=None, cw_srv_keep_alive_dt=None):
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
        self.lb_host = lb_host
        self.lb_agent_port = lb_agent_port
        self.lb_port = lb_port
        self.cw_srv_id = cw_srv_id
        self.cw_srv_keep_alive_dt = cw_srv_keep_alive_dt

    def to_json(self):
        return to_json(self)

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

    # If the server's request to join a cluster has been accepted, and for now
    # it will always be.
    last_join_status = Column(String(40), nullable=True)
    last_join_mod_date = Column(DateTime(), nullable=True)
    last_join_mod_by = Column(String(200), nullable=True)

    # Whether the server's up or not
    up_status = Column(String(40), nullable=True)
    up_mod_date = Column(DateTime(), nullable=True)

    token = Column(String(32), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('servers', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, cluster=None, token=None,
                 last_join_status=None, last_join_mod_date=None, last_join_mod_by=None):
        self.id = id
        self.name = name
        self.cluster = cluster
        self.token = token
        self.last_join_status = last_join_status
        self.last_join_mod_date = last_join_mod_date
        self.last_join_mod_by = last_join_mod_by
        self.has_lb_config = False # Not used by the database
        self.in_lb = False # Not used by the database
        self.lb_state = None # Not used by the database
        self.lb_address = None # Not used by the database
        self.may_be_deleted = None # Not used by the database
        self.up_mod_date_user = None # Not used by the database

################################################################################

class SecurityBase(Base):
    """ A base class for all the security definitions.
    """
    __tablename__ = 'sec_base'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'),
        UniqueConstraint('cluster_id', 'username', 'sec_type'), {})
    __mapper_args__ = {'polymorphic_on': 'sec_type'}

    id = Column(Integer, Sequence('sec_base_seq'), primary_key=True)
    name = Column(String(200), nullable=False)

    # It's nullable because TechnicalAccount doesn't use usernames
    username = Column(String(200), nullable=True)

    password = Column(String(64), nullable=True)
    password_type = Column(String(45), nullable=True)
    is_active = Column(Boolean(), nullable=False)
    sec_type = Column(String(45), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('http_basic_auth_list', order_by=name, cascade='all, delete, delete-orphan'))

class HTTPBasicAuth(SecurityBase):
    """ An HTTP Basic Auth definition.
    """
    __tablename__ = 'sec_basic_auth'
    __mapper_args__ = {'polymorphic_identity': 'basic_auth'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    realm = Column(String(200), nullable=False)

    def __init__(self, id=None, name=None, is_active=None, username=None,
                 realm=None, password=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.realm = realm
        self.password = password
        self.cluster = cluster

class WSSDefinition(SecurityBase):
    """ A WS-Security definition.
    """
    __tablename__ = 'sec_wss_def'
    __mapper_args__ = {'polymorphic_identity':'wss'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    reject_empty_nonce_creat = Column(Boolean(), nullable=False)
    reject_stale_tokens = Column(Boolean(), nullable=True)
    reject_expiry_limit = Column(Integer(), nullable=False)
    nonce_freshness_time = Column(Integer(), nullable=True)

    def __init__(self, id=None, name=None, is_active=None, username=None,
                 password=None, password_type=None, reject_empty_nonce_creat=None,
                 reject_stale_tokens=None, reject_expiry_limit=None,
                 nonce_freshness_time=None, cluster=None, password_type_raw=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.password_type = password_type
        self.reject_empty_nonce_creat = reject_empty_nonce_creat
        self.reject_stale_tokens = reject_stale_tokens
        self.reject_expiry_limit = reject_expiry_limit
        self.nonce_freshness_time = nonce_freshness_time
        self.cluster = cluster
        self.password_type_raw = password_type_raw

class TechnicalAccount(SecurityBase):
    """ Stores information about technical accounts, used for instance by Zato
    itself for securing access to its API.
    """
    __tablename__ = 'sec_tech_acc'
    __mapper_args__ = {'polymorphic_identity':'tech_acc'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    salt = Column(String(32), nullable=False)

    def __init__(self, id=None, name=None, is_active=None, password=None, salt=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.password = password
        self.salt = salt
        self.cluster = cluster

    def to_json(self):
        return to_json(self)

class OAuth(SecurityBase):
    """ New in 1.2: Stores OAuth credentials.
    """
    __tablename__ = 'sec_oauth'
    __mapper_args__ = {'polymorphic_identity':'oauth'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    proto_version = Column(String(32), nullable=False)
    sig_method = Column(String(32), nullable=False) # HMAC-SHA1 or PLAINTEXT
    max_nonce_log = Column(Integer(), nullable=False)

    def __init__(self, id=None, name=None, is_active=None, username=None,
                 password=None, proto_version=None, sig_method=None,
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

################################################################################

class HTTPSOAP(Base):
    """ An incoming or outgoing HTTP/SOAP connection.
    """
    __tablename__ = 'http_soap'
    __table_args__ = (UniqueConstraint('name', 'connection', 'transport', 'cluster_id'),
                      UniqueConstraint('url_path', 'connection', 'soap_action', 'cluster_id'), {})

    id = Column(Integer, Sequence('http_soap_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    connection = Column(Enum('channel', 'outgoing', name='http_soap_connection'), nullable=False)
    transport = Column(Enum('plain_http', 'soap', name='http_soap_transport'), nullable=False)

    host = Column(String(200), nullable=True)
    url_path = Column(String(200), nullable=False)
    method = Column(String(200), nullable=True)

    soap_action = Column(String(200), nullable=False)
    soap_version = Column(String(20), nullable=True)

    data_format = Column(String(20), nullable=True)

    # New in 1.2
    ping_method = Column(String(60), nullable=True)

    # New in 1.2
    pool_size = Column(Integer, nullable=True)

    # New in 1.2
    merge_url_params_req = Column(Boolean, nullable=True, default=True)

    # New in 1.2
    url_params_pri = Column(String(200), nullable=True, default='path-over-qs')

    # New in 1.2
    params_pri = Column(String(200), nullable=True, default='channel-params-over-msg')
    
    # New in 1.2
    audit_enabled = Column(Boolean, nullable=False, default=False)
    
    # New in 1.2
    audit_back_log = Column(Integer, nullable=False, default=MISC.DEFAULT_AUDIT_BACK_LOG)
    
    # New in 1.2
    audit_max_payload = Column(Integer, nullable=False, default=MISC.DEFAULT_AUDIT_MAX_PAYLOAD)
    
    # New in 1.2
    audit_repl_patt_type = Column(String(), nullable=False, default=MSG_PATTERN_TYPE.ELEM_PATH.id)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    service = relationship('Service', backref=backref('http_soap', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)
    security = relationship(SecurityBase, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, is_internal=None,
                 connection=None, transport=None, host=None, url_path=None, method=None,
                 soap_action=None, soap_version=None, data_format=None, ping_method=None,
                 pool_size=None, merge_url_params_req=None, url_params_pri=None,
                 params_pri=None, service_id=None, service=None, security=None, cluster_id=None,
                 cluster=None, service_name=None, security_id=None, security_name=None):
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
        self.service_id = service_id
        self.service = service
        self.security = security
        self.cluster_id = cluster_id
        self.cluster = cluster
        self.service_name = service_name # Not used by the DB
        self.security_id = security_id
        self.security_name = security_name

################################################################################

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

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('sql_pools', order_by=name, cascade='all, delete, delete-orphan'))

    engine_text = None # For auto-completion, not used by the DB

    def __init__(self, id=None, name=None, is_active=None, db_name=None,
                 username=None, engine=None, extra=None, host=None, port=None,
                 pool_size=None, cluster=None):
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

################################################################################

class Service(Base):
    """ A set of basic informations about a service available in a given cluster.
    """
    __tablename__ = 'service'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('service_id_seq'), primary_key=True)
    name = Column(String(300), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    impl_name = Column(String(2000), nullable=False)
    is_internal = Column(Boolean(), nullable=False)
    wsdl = Column(LargeBinary(5000000), nullable=True)
    wsdl_name = Column(String(200), nullable=True)

    slow_threshold = Column(Integer, nullable=False, default=99999)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('services', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, impl_name=None,
                 is_internal=None, cluster=None, wsdl=None, wsdl_name=None):
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
        self.wmq_channels = [] # Not used by the database
        self.zmq_channels = [] # Not used by the database
        self.scheduler_jobs = [] # Not used by the database
        self.deployment_info = [] # Not used by the database
        self.source_info = None # Not used by the database
        self.may_be_deleted = False # Not used by the database

        self.sample_cid = None # Not used by the database
        self.sample_req_timestamp = None # Not used by the database
        self.sample_resp_timestamp = None # Not used by the database
        self.sample_req = None # Not used by the database
        self.sample_resp = None # Not used by the database
        self.sample_req_resp_freq = None # Not used by the database
        self.sample_req_html = None # Not used by the database
        self.sample_resp_html = None # Not used by the database

        self.usage = None # Not used by the database
        self.time_last = None # Not used by the database

        self.time_min_all_time = None # Not used by the database
        self.time_max_all_time = None # Not used by the database
        self.time_mean_all_time = None # Not used by the database

        self.time_usage_1h = None # Not used by the database
        self.time_min_1h = None # Not used by the database
        self.time_max_1h = None # Not used by the database
        self.time_trend_mean_1h = None # Not used by the database
        self.time_trend_rate_1h = None # Not used by the database

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

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    server = relationship(Server, backref=backref('deployed_services', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    service = relationship(Service, backref=backref('deployment_data', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    def __init__(self, deployment_time, details, server, service, source, source_path,
                 source_hash, source_hash_method):
        self.deployment_time = deployment_time
        self.details = details
        self.server = server
        self.service = service
        self.source = source
        self.source_path = source_path
        self.source_hash = source_hash
        self.source_hash_method = source_hash_method

################################################################################

class Job(Base):
    """ A scheduler's job. Stores all the information needed to execute a job
    if it's a one-time job, otherwise the information is kept in related tables.
    """
    __tablename__ = 'job'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('job_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    job_type = Column(Enum(SCHEDULER_JOB_TYPE.ONE_TIME, SCHEDULER_JOB_TYPE.INTERVAL_BASED,
                           SCHEDULER_JOB_TYPE.CRON_STYLE, name='job_type'), nullable=False)
    start_date = Column(DateTime(), nullable=False)
    extra = Column(LargeBinary(500000), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('jobs', order_by=name, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('jobs', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, job_type=None,
                 start_date=None, extra=None, cluster=None, cluster_id=None,
                 service=None, service_id=None, service_name=None, interval_based=None,
                 cron_style=None, definition_text=None, job_type_friendly=None):
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

    job_id = Column(Integer, ForeignKey('job.id', ondelete='CASCADE'), nullable=False)
    job = relationship(Job, backref=backref('interval_based', uselist=False, cascade='all, delete, delete-orphan', single_parent=True))

    def __init__(self, id=None, job=None, weeks=None, days=None, hours=None,
                 minutes=None, seconds=None, repeats=None, definition_text=None):
        self.id = id
        self.job = job
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.repeats = repeats
        self.definition_text = definition_text # Not used by the database

class CronStyleJob(Base):
    """ A Cron-style scheduler's job.
    """
    __tablename__ = 'job_cron_style'
    __table_args__ = (UniqueConstraint('job_id'), {})

    id = Column(Integer, Sequence('job_cron_seq'), primary_key=True)
    cron_definition = Column(String(4000), nullable=False)

    job_id = Column(Integer, ForeignKey('job.id', ondelete='CASCADE'), nullable=False)
    job = relationship(Job, backref=backref('cron_style', uselist=False, cascade='all, delete, delete-orphan', single_parent=True))

    def __init__(self, id=None, job=None, cron_definition=None):
        self.id = id
        self.job = job
        self.cron_definition = cron_definition

################################################################################

class ConnDefAMQP(Base):
    """ An AMQP connection definition.
    """
    __tablename__ = 'conn_def_amqp'
    __table_args__ = (UniqueConstraint('name', 'cluster_id', 'def_type'), {})

    id = Column(Integer, Sequence('conn_def_amqp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    # TODO is_active = Column(Boolean(), nullable=False)

    def_type = Column(String(10), nullable=False)
    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    vhost = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    frame_max = Column(Integer(), nullable=False)
    heartbeat = Column(Integer(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('amqp_conn_defs', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, def_type=None, host=None, port=None,
                 vhost=None, username=None, password=None, frame_max=None,
                 heartbeat=None, cluster_id=None):
        self.id = id
        self.name = name
        self.def_type = def_type
        self.host = host
        self.port = port
        self.vhost = vhost
        self.username = username
        self.password = password
        self.frame_max = frame_max
        self.heartbeat = heartbeat
        self.cluster_id = cluster_id

class ConnDefWMQ(Base):
    """ A WebSphere MQ connection definition.
    """
    __tablename__ = 'conn_def_wmq'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('conn_def_wmq_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    # TODO is_active = Column(Boolean(), nullable=False)

    host = Column(String(200), nullable=False)
    port = Column(Integer, nullable=False)
    queue_manager = Column(String(200), nullable=False)
    channel = Column(String(200), nullable=False)
    cache_open_send_queues = Column(Boolean(), nullable=False)
    cache_open_receive_queues = Column(Boolean(), nullable=False)
    use_shared_connections = Column(Boolean(), nullable=False)
    dynamic_queue_template = Column(String(200), nullable=False, server_default='SYSTEM.DEFAULT.MODEL.QUEUE') # We're not actually using it yet
    ssl = Column(Boolean(), nullable=False)
    ssl_cipher_spec = Column(String(200))
    ssl_key_repository = Column(String(200))
    needs_mcd = Column(Boolean(), nullable=False)
    max_chars_printed = Column(Integer, nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('wmq_conn_defs', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, host=None, port=None,
                 queue_manager=None, channel=None, cache_open_send_queues=None,
                 cache_open_receive_queues=None, use_shared_connections=None, ssl=None,
                 ssl_cipher_spec=None, ssl_key_repository=None, needs_mcd=None,
                 max_chars_printed=None, cluster_id=None):
        self.id = id
        self.name = name
        self.host = host
        self.queue_manager = queue_manager
        self.channel = channel
        self.port = port
        self.cache_open_receive_queues = cache_open_receive_queues
        self.cache_open_send_queues = cache_open_send_queues
        self.use_shared_connections = use_shared_connections
        self.ssl = ssl
        self.ssl_cipher_spec = ssl_cipher_spec
        self.ssl_key_repository = ssl_key_repository
        self.needs_mcd = needs_mcd
        self.max_chars_printed = max_chars_printed
        self.cluster_id = cluster_id

################################################################################

class OutgoingAMQP(Base):
    """ An outgoing AMQP connection.
    """
    __tablename__ = 'out_amqp'
    __table_args__ = (UniqueConstraint('name', 'def_id'), {})

    id = Column(Integer, Sequence('out_amqp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    delivery_mode = Column(SmallInteger(), nullable=False)
    priority = Column(SmallInteger(), server_default=str(AMQP_DEFAULT_PRIORITY), nullable=False)

    content_type = Column(String(200), nullable=True)
    content_encoding = Column(String(200), nullable=True)
    expiration = Column(String(20), nullable=True)
    user_id = Column(String(200), nullable=True)
    app_id = Column(String(200), nullable=True)

    def_id = Column(Integer, ForeignKey('conn_def_amqp.id', ondelete='CASCADE'), nullable=False)
    def_ = relationship(ConnDefAMQP, backref=backref('out_conns_amqp', cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, delivery_mode=None,
                 priority=None, content_type=None, content_encoding=None,
                 expiration=None, user_id=None, app_id=None, def_id=None,
                 delivery_mode_text=None, def_name=None):
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
        self.def_id = def_id
        self.delivery_mode_text = delivery_mode_text # Not used by the DB
        self.def_name = def_name # Not used by the DB

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

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_ftp', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, host=None, user=None,
                 password=None, acct=None, timeout=None, port=None, dircache=None,
                 cluster_id=None):
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

class OutgoingWMQ(Base):
    """ An outgoing WebSphere MQ connection.
    """
    __tablename__ = 'out_wmq'
    __table_args__ = (UniqueConstraint('name', 'def_id'), {})

    id = Column(Integer, Sequence('out_wmq_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    delivery_mode = Column(SmallInteger(), nullable=False)
    priority = Column(SmallInteger(), server_default=str(WMQ_DEFAULT_PRIORITY), nullable=False)
    expiration = Column(String(20), nullable=True)

    def_id = Column(Integer, ForeignKey('conn_def_wmq.id', ondelete='CASCADE'), nullable=False)
    def_ = relationship(ConnDefWMQ, backref=backref('out_conns_wmq', cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, delivery_mode=None,
                 priority=None, expiration=None, def_id=None, delivery_mode_text=None,
                 def_name=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.delivery_mode = delivery_mode
        self.priority = priority
        self.expiration = expiration
        self.def_id = def_id
        self.delivery_mode_text = delivery_mode_text # Not used by the DB
        self.def_name = def_name # Not used by the DB

class OutgoingZMQ(Base):
    """ An outgoing Zero MQ connection.
    """
    __tablename__ = 'out_zmq'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('out_zmq_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    address = Column(String(200), nullable=False)
    socket_type = Column(String(20), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_zmq', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, address=None,
                 socket_type=None, cluster_id=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.socket_type = socket_type
        self.address = address
        self.cluster_id = cluster_id

################################################################################

class ChannelAMQP(Base):
    """ An incoming AMQP connection.
    """
    __tablename__ = 'channel_amqp'
    __table_args__ = (UniqueConstraint('name', 'def_id'), {})

    id = Column(Integer, Sequence('channel_amqp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    queue = Column(String(200), nullable=False)
    consumer_tag_prefix = Column(String(200), nullable=False)
    data_format = Column(String(20), nullable=True)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('channels_amqp', order_by=name, cascade='all, delete, delete-orphan'))

    def_id = Column(Integer, ForeignKey('conn_def_amqp.id', ondelete='CASCADE'), nullable=False)
    def_ = relationship(ConnDefAMQP, backref=backref('channels_amqp', cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, queue=None,
                 consumer_tag_prefix=None, def_id=None, def_name=None,
                 service_name=None, data_format=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.queue = queue
        self.consumer_tag_prefix = consumer_tag_prefix
        self.def_id = def_id
        self.def_name = def_name # Not used by the DB
        self.service_name = service_name # Not used by the DB
        self.data_format = data_format

class ChannelWMQ(Base):
    """ An incoming WebSphere MQ connection.
    """
    __tablename__ = 'channel_wmq'
    __table_args__ = (UniqueConstraint('name', 'def_id'), {})

    id = Column(Integer, Sequence('channel_wmq_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    queue = Column(String(200), nullable=False)
    data_format = Column(String(20), nullable=True)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('channels_wmq', order_by=name, cascade='all, delete, delete-orphan'))

    def_id = Column(Integer, ForeignKey('conn_def_wmq.id', ondelete='CASCADE'), nullable=False)
    def_ = relationship(ConnDefWMQ, backref=backref('channels_wmq', cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, queue=None,
                 def_id=None, def_name=None, service_name=None, data_format=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.queue = queue
        self.def_id = def_id
        self.def_name = def_name # Not used by the DB
        self.service_name = service_name # Not used by the DB
        self.data_format = data_format

class ChannelZMQ(Base):
    """ An incoming Zero MQ connection.
    """
    __tablename__ = 'channel_zmq'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('channel_zmq_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    address = Column(String(200), nullable=False)
    socket_type = Column(String(20), nullable=False)
    sub_key = Column(String(200), nullable=True)
    data_format = Column(String(20), nullable=True)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('channels_zmq', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('channels_zmq', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, address=None,
                 socket_type=None, sub_key=None, service_name=None, data_format=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.address = address
        self.socket_type = socket_type
        self.sub_key = sub_key
        self.service_name = service_name # Not used by the DB
        self.data_format = data_format

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

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    server = relationship(Server, backref=backref('originating_deployment_packages', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, deployment_time=None, details=None, payload_name=None, payload=None):
        self.id = id
        self.deployment_time = deployment_time
        self.details = details
        self.payload_name = payload_name
        self.payload = payload

class DeploymentStatus(Base):
    """ Whether a server has already deployed a given package.
    """
    __tablename__ = 'deployment_status'
    __table_args__ = (UniqueConstraint('package_id', 'server_id'), {})

    id = Column(Integer, Sequence('depl_status_seq'), primary_key=True)

    package_id = Column(Integer, ForeignKey('deployment_package.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    package = relationship(DeploymentPackage, backref=backref('deployment_status_list', order_by=package_id, cascade='all, delete, delete-orphan'))

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    server = relationship(Server, backref=backref('deployment_status_list', order_by=server_id, cascade='all, delete, delete-orphan'))

    # See zato.common.DEPLOYMENT_STATUS
    status = Column(String(20), nullable=False)
    status_change_time = Column(DateTime(), nullable=False)

    def __init__(self, package_id=None, server_id=None, status=None, status_change_time=None):
        self.package_id = package_id
        self.server_id = server_id
        self.status = status
        self.status_change_time = status_change_time

################################################################################

class DeliveryDefinitionBase(Base):
    """ A guaranteed delivery's definition (base class).
    """
    __tablename__ = 'delivery_def_base'
    __mapper_args__ = {'polymorphic_on': 'target_type'}

    id = Column(Integer, Sequence('deliv_def_seq'), primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    short_def = Column(String(200), nullable=False)
    last_used = Column(DateTime(), nullable=True)

    target_type = Column(String(200), nullable=False)
    callback_list = Column(LargeBinary(10000), nullable=True)

    expire_after = Column(Integer, nullable=False)
    expire_arch_succ_after = Column(Integer, nullable=False)
    expire_arch_fail_after = Column(Integer, nullable=False)
    check_after = Column(Integer, nullable=False)
    retry_repeats = Column(Integer, nullable=False)
    retry_seconds = Column(Integer, nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('delivery_list', order_by=name, cascade='all, delete, delete-orphan'))

class DeliveryDefinitionOutconnWMQ(DeliveryDefinitionBase):
    """ A guaranteed delivery's definition (outgoing WebSphere MQ connections).
    """
    __tablename__ = 'delivery_def_out_wmq'
    __mapper_args__ = {'polymorphic_identity': INVOCATION_TARGET.OUTCONN_WMQ}

    id = Column(Integer, ForeignKey('delivery_def_base.id'), primary_key=True)
    target_id = Column(Integer, ForeignKey('out_wmq.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    target = relationship(OutgoingWMQ, backref=backref('delivery_def_list', order_by=target_id, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, target_id=None):
        self.id = id
        self.target_id = target_id

class Delivery(Base):
    """ A guaranteed delivery.
    """
    __tablename__ = 'delivery'

    id = Column(Integer, Sequence('deliv_seq'), primary_key=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)

    name = Column(String(200), nullable=False)
    creation_time = Column(DateTime(), nullable=False)

    args = Column(LargeBinary(1000000), nullable=True)
    kwargs = Column(LargeBinary(1000000), nullable=True)

    last_used = Column(DateTime(), nullable=True)
    resubmit_count = Column(Integer, nullable=False, default=0)

    state = Column(String(200), nullable=False, index=True)

    source_count = Column(Integer, nullable=False, default=1)
    target_count = Column(Integer, nullable=False, default=0)

    definition_id = Column(Integer, ForeignKey('delivery_def_base.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    definition = relationship(DeliveryDefinitionBase, backref=backref('delivery_list', order_by=creation_time, cascade='all, delete, delete-orphan'))

class DeliveryPayload(Base):
    """ A guaranteed delivery's payload.
    """
    __tablename__ = 'delivery_payload'

    id = Column(Integer, Sequence('deliv_payl_seq'), primary_key=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)

    creation_time = Column(DateTime(), nullable=False)
    payload = Column(LargeBinary(5000000), nullable=False)

    delivery_id = Column(Integer, ForeignKey('delivery.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    delivery = relationship(Delivery, backref=backref('payload', uselist=False, cascade='all, delete, delete-orphan', single_parent=True))

class DeliveryHistory(Base):
    """ A guaranteed delivery's history.
    """
    __tablename__ = 'delivery_history'

    id = Column(Integer, Sequence('deliv_payl_seq'), primary_key=True)
    task_id = Column(String(64), nullable=False, index=True)

    entry_type = Column(String(64), nullable=False)
    entry_time = Column(DateTime(), nullable=False, index=True)
    entry_ctx = Column(LargeBinary(6000000), nullable=False)
    resubmit_count = Column(Integer, nullable=False, default=0) # Copy of delivery.resubmit_count so it's known for each history entry

    delivery_id = Column(Integer, ForeignKey('delivery.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    delivery = relationship(Delivery, backref=backref('history_list', order_by=entry_time, cascade='all, delete, delete-orphan'))

# ##############################################################################

class MsgNamespace(Base):
    """ A message namespace, used in XPath, for instance.
    """
    __tablename__ = 'msg_ns'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('msg_ns_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(String(500), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('namespaces', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, value=None, cluster_id=None):
        self.id = id
        self.name = name
        self.value = value
        self.cluster_id = cluster_id

class XPath(Base):
    """ An XPath expression to run against XML messages.
    """
    __tablename__ = 'msg_xpath'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('msg_xpath_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(String(1500), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('xpaths', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, value=None, cluster_id=None):
        self.id = id
        self.name = name
        self.value = value
        self.cluster_id = cluster_id

class ElemPath(Base):
    """ An XPath-list expression to run against JSON messages.
    """
    __tablename__ = 'msg_elem_path'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('msg_elem_path_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(String(1500), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('elem_paths', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, value=None, cluster_id=None):
        self.id = id
        self.name = name
        self.value = value
        self.cluster_id = cluster_id

# ##############################################################################

class HTTSOAPAudit(Base):
    """ An audit log for HTTP/SOAP channels and outgoing connections.
    """
    __tablename__ = 'http_soap_audit'

    id = Column(Integer, Sequence('http_soap_audit_seq'), primary_key=True)
    name = Column(String(), nullable=False, index=True)
    cid = Column(String(), nullable=False, index=True)
    
    transport = Column(String(), nullable=False, index=True)
    connection = Column(String(), nullable=False, index=True)
    
    req_time = Column(DateTime(), nullable=False)
    resp_time = Column(DateTime(), nullable=True)
    
    user_token = Column(String(), nullable=True, index=True)
    invoke_ok = Column(Boolean(), nullable=True)
    auth_ok = Column(Boolean(), nullable=True)
    remote_addr = Column(String(), nullable=False, index=True)
    
    req_headers = Column(String(), nullable=True)
    req_payload = Column(String(), nullable=True)
    resp_headers = Column(String(), nullable=True)
    resp_payload = Column(String(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    conn_id = Column(Integer, ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, id=None, name=None, cid=None, transport=None, 
            connection=None, req_time=None, resp_time=None, user_token=None, 
            invoke_ok=None, auth_ok=None, remote_addr=None, req_headers=None,
            req_payload=None, resp_headers=None, resp_payload=None):
        
        self.id = id
        self.name = name
        self.cid = cid
        
        self.transport = transport
        self.connection = connection
        
        self.req_time = req_time
        self.resp_time = resp_time
        
        self.user_token = user_token
        self.invoke_ok = invoke_ok
        self.auth_ok = auth_ok
        self.remote_addr = remote_addr
        
        self.req_headers = req_headers
        self.req_payload = req_payload
        self.resp_headers = resp_headers
        self.resp_payload = resp_payload

class HTTSOAPAuditReplacePatternsElemPath(Base):
    """ ElemPath replace patterns for HTTP/SOAP connections.
    """
    __tablename__ = 'http_soap_au_rpl_p_ep'
    __table_args__ = (UniqueConstraint('conn_id', 'pattern_id'), {})
    
    id = Column(Integer, Sequence('htp_sp_ad_rpl_p_ep_seq'), primary_key=True)
    conn_id = Column(Integer, ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False)
    pattern_id = Column(Integer, ForeignKey('msg_elem_path.id', ondelete='CASCADE'), nullable=False)
    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    
    replace_patterns_elem_path = relationship(HTTPSOAP, 
        backref=backref('replace_patterns_elem_path', order_by=id, cascade='all, delete, delete-orphan'))

    pattern = relationship(ElemPath)
    
class HTTSOAPAuditReplacePatternsXPath(Base):
    """ XPath replace patterns for HTTP/SOAP connections.
    """
    __tablename__ = 'http_soap_au_rpl_p_xp'
    __table_args__ = (UniqueConstraint('conn_id', 'pattern_id'), {})
    
    id = Column(Integer, Sequence('htp_sp_ad_rpl_p_xp_seq'), primary_key=True)
    conn_id = Column(Integer, ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False)
    pattern_id = Column(Integer, ForeignKey('msg_xpath.id', ondelete='CASCADE'), nullable=False)
    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    
    replace_patterns_xpath = relationship(HTTPSOAP, 
        backref=backref('replace_patterns_xpath', order_by=id, cascade='all, delete, delete-orphan'))

    pattern = relationship(XPath)

# ##############################################################################
