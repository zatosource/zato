# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from ftplib import FTP_PORT
from json import dumps

# dictalchemy
from dictalchemy import make_class_dictable

# SQLAlchemy
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, LargeBinary, Sequence, SmallInteger, String, \
     Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

# Zato
from zato.common import CASSANDRA, CLOUD, HTTP_SOAP_SERIALIZATION_TYPE, INVOCATION_TARGET, MISC, NOTIF, MSG_PATTERN_TYPE, \
     ODOO, PUB_SUB, SCHEDULER, STOMP, PARAMS_PRIORITY, URL_PARAMS_PRIORITY
from zato.common.odb import AMQP_DEFAULT_PRIORITY, WMQ_DEFAULT_PRIORITY

Base = declarative_base()
make_class_dictable(Base)

# ################################################################################################################################

def to_json(model, return_as_dict=False):
    """ Returns a JSON representation of an SQLAlchemy-backed object.
    """
    json = {}
    json['fields'] = {}
    json['pk'] = getattr(model, 'id')

    for col in model._sa_class_manager.mapper.mapped_table.columns:
        json['fields'][col.name] = getattr(model, col.name)

    if return_as_dict:
        return json
    else:
        return dumps([json])

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

    def __init__(self, id=None, version=None, install_time=None, source_host=None,
                 source_user=None):
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

    # It's nullable because TechnicalAccount doesn't use usernames
    username = Column(String(200), nullable=True)

    password = Column(String(64), nullable=True)
    password_type = Column(String(45), nullable=True)
    is_active = Column(Boolean(), nullable=False)
    sec_type = Column(String(45), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('security_list', order_by=name, cascade='all, delete, delete-orphan'))

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

class JWT(SecurityBase):
    """ A set of JavaScript Web Token (JWT) credentials.
    """
    __tablename__ = 'sec_jwt'
    __mapper_args__ = {'polymorphic_identity': 'jwt'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    ttl = Column(Integer, nullable=False)

# ################################################################################################################################

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

# ################################################################################################################################

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

class AWSSecurity(SecurityBase):
    """ Stores Amazon credentials.
    """
    __tablename__ = 'sec_aws'
    __mapper_args__ = {'polymorphic_identity': 'aws'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)

    def __init__(self, id=None, name=None, is_active=None, username=None, password=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.cluster = cluster

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class OpenStackSecurity(SecurityBase):
    """ Stores OpenStack credentials..
    """
    __tablename__ = 'sec_openstack'
    __mapper_args__ = {'polymorphic_identity': 'openstack'}

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

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class XPathSecurity(SecurityBase):
    """ Stores XPath-based credentials.
    """
    __tablename__ = 'sec_xpath'
    __mapper_args__ = {'polymorphic_identity':'xpath_sec'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    username_expr = Column(String(200), nullable=False)
    password_expr = Column(String(200), nullable=True)

    def __init__(self, id=None, name=None, is_active=None, username=None, password=None, username_expr=None, password_expr=None,
                 cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.username_expr = username_expr
        self.password_expr = password_expr
        self.cluster = cluster

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class TLSKeyCertSecurity(SecurityBase):
    """ Stores information regarding TLS key/cert pairs used in outgoing connections.
    """
    __tablename__ = 'sec_tls_key_cert'
    __mapper_args__ = {'polymorphic_identity':'tls_key_cert'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    info = Column(LargeBinary(200000), nullable=False)
    value = Column(LargeBinary(200000), nullable=False)

# ################################################################################################################################

class TLSChannelSecurity(SecurityBase):
    """ Stores information regarding TLS client certificate-based security definitions.
    """
    __tablename__ = 'sec_tls_channel'
    __mapper_args__ = {'polymorphic_identity':'tls_channel_sec'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    value = Column(LargeBinary(200000), nullable=False)

# ################################################################################################################################

class TLSCACert(Base):
    """ Stores information regarding CA certs.
    """
    __tablename__ = 'sec_tls_ca_cert'

    id = Column(Integer, Sequence('sec_tls_ca_cert_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(LargeBinary(200000), nullable=False)
    info = Column(LargeBinary(200000), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('ca_cert_list', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class HTTPSOAP(Base):
    """ An incoming or outgoing HTTP/SOAP connection.
    """
    __tablename__ = 'http_soap'
    __table_args__ = (UniqueConstraint('name', 'connection', 'transport', 'cluster_id'),
                      UniqueConstraint('url_path', 'host', 'connection', 'soap_action', 'cluster_id'), {})

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
    content_type = Column(String(200), nullable=True)

    ping_method = Column(String(60), nullable=True)
    pool_size = Column(Integer, nullable=True)
    serialization_type = Column(String(200), nullable=False, default=HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id)
    timeout = Column(Integer(), nullable=False, default=MISC.DEFAULT_HTTP_TIMEOUT)

    merge_url_params_req = Column(Boolean, nullable=True, default=True)
    url_params_pri = Column(String(200), nullable=True, default=URL_PARAMS_PRIORITY.DEFAULT)
    params_pri = Column(String(200), nullable=True, default=PARAMS_PRIORITY.DEFAULT)

    audit_enabled = Column(Boolean, nullable=False, default=False)
    audit_back_log = Column(Integer, nullable=False, default=MISC.DEFAULT_AUDIT_BACK_LOG)
    audit_max_payload = Column(Integer, nullable=False, default=MISC.DEFAULT_AUDIT_MAX_PAYLOAD)
    audit_repl_patt_type = Column(String(200), nullable=False, default=MSG_PATTERN_TYPE.JSON_POINTER.id)

    sec_tls_ca_cert_id = Column(Integer, ForeignKey('sec_tls_ca_cert.id', ondelete='CASCADE'), nullable=True)
    sec_tls_ca_cert = relationship('TLSCACert', backref=backref('http_soap', order_by=name, cascade='all, delete, delete-orphan'))
    has_rbac = Column(Boolean, nullable=False, default=False)
    sec_use_rbac = Column(Boolean(), nullable=False, default=False)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    service = relationship('Service', backref=backref('http_soap', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)
    security = relationship(SecurityBase, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, is_internal=None, connection=None, transport=None, host=None,
                 url_path=None, method=None, soap_action=None, soap_version=None, data_format=None, ping_method=None,
                 pool_size=None, merge_url_params_req=None, url_params_pri=None, params_pri=None, serialization_type=None,
                 timeout=None, sec_tls_ca_cert_id=None, service_id=None, service=None, security=None, cluster_id=None,
                 cluster=None, service_name=None, security_id=None, has_rbac=None, security_name=None, content_type=None):
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
        self.sec_tls_ca_cert_id = sec_tls_ca_cert_id
        self.service_id = service_id
        self.service = service
        self.security = security
        self.cluster_id = cluster_id
        self.cluster = cluster
        self.service_name = service_name # Not used by the DB
        self.security_id = security_id
        self.has_rbac = has_rbac
        self.security_name = security_name
        self.content_type = content_type

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

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    server = relationship(Server, backref=backref('deployed_services', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False, primary_key=True)
    service = relationship(Service, backref=backref('deployment_data', order_by=deployment_time, cascade='all, delete, delete-orphan'))

    def __init__(self, deployment_time, details, server_id, service, source, source_path,
                 source_hash, source_hash_method):
        self.deployment_time = deployment_time
        self.details = details
        self.server_id = server_id
        self.service = service
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

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

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

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_odoo', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self):
        self.protocol_name = None # Not used by the DB

# ################################################################################################################################

class OutgoingSTOMP(Base):
    """ An outgoing STOMP connection.
    """
    __tablename__ = 'out_stomp'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('out_stomp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    username = Column(String(200), nullable=True, server_default=STOMP.DEFAULT.USERNAME)
    password = Column(String(200), nullable=True)

    address = Column(String(200), nullable=False, server_default=STOMP.DEFAULT.ADDRESS)
    proto_version = Column(String(20), nullable=False, server_default=STOMP.DEFAULT.PROTOCOL)
    timeout = Column(Integer(), nullable=False, server_default=str(STOMP.DEFAULT.TIMEOUT))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('out_conns_stomp', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

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

# ################################################################################################################################

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
    socket_method = Column(String(20), nullable=False)

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

# ################################################################################################################################

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

# ################################################################################################################################

class ChannelSTOMP(Base):
    """ An incoming STOMP connection.
    """
    __tablename__ = 'channel_stomp'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('channel_stomp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    username = Column(String(200), nullable=True, server_default=STOMP.DEFAULT.USERNAME)
    password = Column(String(200), nullable=True)

    address = Column(String(200), nullable=False, server_default=STOMP.DEFAULT.ADDRESS)
    proto_version = Column(String(20), nullable=False, server_default=STOMP.DEFAULT.PROTOCOL)
    timeout = Column(Integer(), nullable=False, server_default=str(STOMP.DEFAULT.TIMEOUT))
    sub_to = Column(Text, nullable=False)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('channels_stomp', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('channels_stomp', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

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

# ################################################################################################################################

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
    socket_method = Column(String(20), nullable=False)
    pool_strategy = Column(String(20), nullable=False)
    service_source = Column(String(20), nullable=False)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('channels_zmq', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('channels_zmq', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, address=None, socket_type=None, socket_type_text=None, sub_key=None,
                 service_name=None, data_format=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.address = address
        self.socket_type = socket_type
        self.socket_type_text = socket_type_text # Not used by the DB
        self.sub_key = sub_key
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

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    server = relationship(Server, backref=backref('originating_deployment_packages', order_by=deployment_time, cascade='all, delete, delete-orphan'))

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

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

class DeliveryHistory(Base):
    """ A guaranteed delivery's history.
    """
    __tablename__ = 'delivery_history'

    id = Column(Integer, Sequence('deliv_payl_seq'), primary_key=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)

    entry_type = Column(String(64), nullable=False)
    entry_time = Column(DateTime(), nullable=False, index=True)
    entry_ctx = Column(LargeBinary(6000000), nullable=False)
    resubmit_count = Column(Integer, nullable=False, default=0) # Copy of delivery.resubmit_count so it's known for each history entry

    delivery_id = Column(Integer, ForeignKey('delivery.id', ondelete='CASCADE'), nullable=False, primary_key=False)
    delivery = relationship(Delivery, backref=backref('history_list', order_by=entry_time, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

class JSONPointer(Base):
    """ An XPath-list expression to run against JSON messages.
    """
    __tablename__ = 'msg_json_pointer'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('msg_json_pointer_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    value = Column(String(1500), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('json_pointers', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, value=None, cluster_id=None):
        self.id = id
        self.name = name
        self.value = value
        self.cluster_id = cluster_id

# ################################################################################################################################

class HTTSOAPAudit(Base):
    """ An audit log for HTTP/SOAP channels and outgoing connections.
    """
    __tablename__ = 'http_soap_audit'

    id = Column(Integer, Sequence('http_soap_audit_seq'), primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    cid = Column(String(200), nullable=False, index=True)

    transport = Column(String(200), nullable=False, index=True)
    connection = Column(String(200), nullable=False, index=True)

    req_time = Column(DateTime(), nullable=False)
    resp_time = Column(DateTime(), nullable=True)

    user_token = Column(String(200), nullable=True, index=True)
    invoke_ok = Column(Boolean(), nullable=True)
    auth_ok = Column(Boolean(), nullable=True)
    remote_addr = Column(String(200), nullable=False, index=True)

    req_headers = Column(LargeBinary(), nullable=True)
    req_payload = Column(LargeBinary(), nullable=True)
    resp_headers = Column(LargeBinary(), nullable=True)
    resp_payload = Column(LargeBinary(), nullable=True)

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

# ################################################################################################################################

class HTTSOAPAuditReplacePatternsJSONPointer(Base):
    """ JSONPointer replace patterns for HTTP/SOAP connections.
    """
    __tablename__ = 'http_soap_au_rpl_p_jp'
    __table_args__ = (UniqueConstraint('conn_id', 'pattern_id'), {})

    id = Column(Integer, Sequence('htp_sp_ad_rpl_p_jp_seq'), primary_key=True)
    conn_id = Column(Integer, ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False)
    pattern_id = Column(Integer, ForeignKey('msg_json_pointer.id', ondelete='CASCADE'), nullable=False)
    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)

    replace_patterns_json_pointer = relationship(HTTPSOAP,
        backref=backref('replace_patterns_json_pointer', order_by=id, cascade='all, delete, delete-orphan'))

    pattern = relationship(JSONPointer)

# ################################################################################################################################

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

# ################################################################################################################################

class PubSubTopic(Base):
    """ A definition of a topic in pub/sub.
    """
    __tablename__ = 'pub_sub_topic'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('pub_sub_topic_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    max_depth = Column(Integer, nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pub_sub_topics', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, max_depth=None, cluster_id=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.max_depth = max_depth
        self.cluster_id = cluster_id
        self.last_pub_time = None # Not used by the database
        self.cur_depth = None # Not used by the database
        self.cur_consumers = None # Not used by the database
        self.cur_producers = None # Not used by the database

# ################################################################################################################################

class PubSubConsumer(Base):
    """ All consumers of a given topic, including ones that are not currently connected.
    """
    __tablename__ = 'pub_sub_consumer'
    __table_args__ = (UniqueConstraint('sec_def_id', 'topic_id', 'cluster_id'), {})

    id = Column(Integer, Sequence('pub_sub_cons_seq'), primary_key=True)
    is_active = Column(Boolean(), nullable=False)
    sub_key = Column(String(200), nullable=False)
    max_depth = Column(Integer, nullable=False)
    delivery_mode = Column(String(200), nullable=False)

    # Our only callback type right now is an HTTP outconn but more will come with time.
    callback_id = Column(Integer, ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=True)
    callback_type = Column(String(20), nullable=True, default=PUB_SUB.CALLBACK_TYPE.OUTCONN_PLAIN_HTTP)

    topic_id = Column(Integer, ForeignKey('pub_sub_topic.id', ondelete='CASCADE'), nullable=False)
    topic = relationship(PubSubTopic, backref=backref('consumers', order_by=max_depth, cascade='all, delete, delete-orphan'))

    sec_def_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False)
    sec_def = relationship(SecurityBase, backref=backref('pub_sub_consumers', order_by=max_depth, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pub_sub_consumers', order_by=max_depth, cascade='all, delete, delete-orphan'))

    http_soap = relationship(SecurityBase, backref=backref('pubsub_consumers', order_by=max_depth, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, is_active=None, sub_key=None, max_depth=None, delivery_mode=None, callback_id=None,
                callback_type=None, topic_id=None, sec_def_id=None, cluster_id=None):
        self.id = id
        self.is_active = is_active
        self.sub_key = sub_key
        self.max_depth = max_depth
        self.delivery_mode = delivery_mode
        self.callback_id = callback_id
        self.callback_type = callback_type
        self.topic_id = topic_id
        self.sec_def_id = sec_def_id
        self.cluster_id = cluster_id
        self.last_seen = None # Not used by the DB

# ################################################################################################################################

class PubSubProducer(Base):
    """ All producers allowed to publish to a given topic.
    """
    __tablename__ = 'pub_sub_producer'
    __table_args__ = (UniqueConstraint('sec_def_id', 'topic_id', 'cluster_id'), {})

    id = Column(Integer, Sequence('pub_sub_cons_seq'), primary_key=True)
    is_active = Column(Boolean(), nullable=False)

    topic_id = Column(Integer, ForeignKey('pub_sub_topic.id', ondelete='CASCADE'), nullable=False)
    topic = relationship(PubSubTopic, backref=backref('producers', order_by=is_active, cascade='all, delete, delete-orphan'))

    sec_def_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False)
    sec_def = relationship(SecurityBase, backref=backref('pub_sub_producers', order_by=is_active, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pub_sub_producers', order_by=is_active, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, is_active=None, topic_id=None, sec_def_id=None, cluster_id=None):
        self.id = id
        self.is_active = is_active
        self.topic_id = topic_id
        self.sec_def_id = sec_def_id
        self.cluster_id = cluster_id
        self.last_seen = None # Not used by the DB

# ################################################################################################################################

class OpenStackSwift(Base):
    """ A connection to OpenStack's Swift.
    """
    __tablename__ = 'os_swift'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('os_swift_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    pool_size = Column(Integer, nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.POOL_SIZE)

    auth_url = Column(String(200), nullable=False)
    auth_version = Column(String(200), nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.AUTH_VERSION)
    user = Column(String(200), nullable=True)
    key = Column(String(200), nullable=True)
    retries = Column(Integer, nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.RETRIES)
    is_snet = Column(Boolean(), nullable=False)
    starting_backoff = Column(Integer, nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.BACKOFF_STARTING)
    max_backoff = Column(Integer, nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.BACKOFF_MAX)
    tenant_name = Column(String(200), nullable=True)
    should_validate_cert = Column(Boolean(), nullable=False)
    cacert = Column(String(200), nullable=True)
    should_retr_ratelimit = Column(Boolean(), nullable=False)
    needs_tls_compr = Column(Boolean(), nullable=False)
    custom_options = Column(String(2000), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('openstack_swift_conns', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, auth_url=None, auth_version=None, user=None, key=None, retries=None,
            is_snet=None, starting_backoff=None, max_backoff=None, tenant_name=None, should_validate_cert=None,
            cacert=None, should_retr_ratelimit=None, needs_tls_compr=None, custom_options=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.auth_url = auth_url
        self.auth_version = auth_version
        self.user = user
        self.key = key
        self.retries = retries
        self.is_snet = is_snet
        self.starting_backoff = starting_backoff
        self.max_backoff = max_backoff
        self.tenant_name = tenant_name
        self.should_validate_cert = should_validate_cert
        self.cacert = cacert
        self.should_retr_ratelimit = should_retr_ratelimit
        self.needs_tls_compr = needs_tls_compr
        self.custom_options = custom_options

# ################################################################################################################################

class AWSS3(Base):
    """ An outgoing connection to AWS S3.
    """
    __tablename__ = 'aws_s3'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('aws_s3_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    pool_size = Column(Integer, nullable=False, default=CLOUD.AWS.S3.DEFAULTS.POOL_SIZE)

    address = Column(String(200), nullable=False, default=CLOUD.AWS.S3.DEFAULTS.ADDRESS)
    debug_level = Column(Integer, nullable=False, default=CLOUD.AWS.S3.DEFAULTS.DEBUG_LEVEL)
    suppr_cons_slashes = Column(Boolean(), nullable=False, default=True)
    content_type = Column(String(200), nullable=False, default=CLOUD.AWS.S3.DEFAULTS.CONTENT_TYPE)
    metadata_ = Column(String(2000), nullable=True) # Can't be 'metadata' because this is reserved to SQLAlchemy
    bucket = Column(String(2000), nullable=True)
    encrypt_at_rest = Column(Boolean(), nullable=False, default=False)
    storage_class = Column(String(200), nullable=False, default=CLOUD.AWS.S3.STORAGE_CLASS.DEFAULT)

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False)
    security = relationship(SecurityBase, backref=backref('aws_s3_conns', order_by=is_active, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('aws_s3_conns', order_by=name, cascade='all, delete, delete-orphan'))

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class Notification(Base):
    """ A base class for all notifications, be it cloud, FTP-based or others.
    """
    __tablename__ = 'notif'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})
    __mapper_args__ = {'polymorphic_on': 'notif_type'}

    id = Column(Integer, Sequence('sec_base_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False, default=True)
    notif_type = Column(String(45), nullable=False)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    interval = Column(Integer, nullable=False, default=NOTIF.DEFAULT.CHECK_INTERVAL)
    name_pattern = Column(String(2000), nullable=True, default=NOTIF.DEFAULT.NAME_PATTERN)
    name_pattern_neg = Column(Boolean(), nullable=True, default=False)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    get_data = Column(Boolean(), nullable=True, default=False)
    get_data_patt = Column(String(2000), nullable=True, default=NOTIF.DEFAULT.GET_DATA_PATTERN)
    get_data_patt_neg = Column(Boolean(), nullable=True, default=False)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship(Service, backref=backref('notification_list', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('notification_list', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class NotificationOpenStackSwift(Notification):
    """ Stores OpenStack Swift notifications.
    """
    __tablename__ = 'notif_os_swift'
    __mapper_args__ = {'polymorphic_identity': 'openstack_swift'}

    id = Column(Integer, ForeignKey('notif.id'), primary_key=True)

    containers = Column(String(20000), nullable=False)

    def_id = Column(Integer, ForeignKey('os_swift.id'), primary_key=True)
    definition = relationship(OpenStackSwift, backref=backref('notif_oss_list', order_by=id, cascade='all, delete, delete-orphan'))

    def to_json(self):
        return to_json(self)

# ################################################################################################################################

class NotificationSQL(Notification):
    """ Stores SQL notifications.
    """
    __tablename__ = 'notif_sql'
    __mapper_args__ = {'polymorphic_identity': 'sql'}

    id = Column(Integer, ForeignKey('notif.id'), primary_key=True)

    query = Column(Text, nullable=False)

    def_id = Column(Integer, ForeignKey('sql_pool.id'), primary_key=True)
    definition = relationship(SQLConnectionPool, backref=backref('notif_sql_list', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class CassandraConn(Base):
    """ Connections to Cassandra.
    """
    __tablename__ = 'conn_def_cassandra'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('conn_def_cassandra_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    contact_points = Column(String(400), nullable=False, default=CASSANDRA.DEFAULT.CONTACT_POINTS.value)
    port = Column(Integer, nullable=False, default=CASSANDRA.DEFAULT.PORT.value)
    exec_size = Column(Integer, nullable=False, default=CASSANDRA.DEFAULT.EXEC_SIZE.value)
    proto_version = Column(Integer, nullable=False, default=CASSANDRA.DEFAULT.PROTOCOL_VERSION.value)
    cql_version = Column(Integer, nullable=True)
    default_keyspace = Column(String(400), nullable=False)
    username = Column(String(200), nullable=True)
    password = Column(String(200), nullable=True)
    tls_ca_certs = Column(String(200), nullable=True)
    tls_client_cert = Column(String(200), nullable=True)
    tls_client_priv_key = Column(String(200), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('cassandra_conn_list', order_by=name, cascade='all, delete, delete-orphan'))

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

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('search_es_conns', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class Solr(Base):
    __tablename__ = 'search_solr'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('search_solr_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False, default=True)
    address = Column(String(400), nullable=False)
    timeout = Column(Integer(), nullable=False)
    ping_path = Column(String(40), nullable=False)
    options = Column(String(800), nullable=True)
    pool_size = Column(Integer(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('search_solr_conns', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class CassandraQuery(Base):
    """ Cassandra query templates.
    """
    __tablename__ = 'query_cassandra'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('query_cassandra_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    value = Column(LargeBinary(40000), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('cassandra_queries', order_by=name, cascade='all, delete, delete-orphan'))

    def_id = Column(Integer, ForeignKey('conn_def_cassandra.id', ondelete='CASCADE'), nullable=False)
    def_ = relationship(CassandraConn, backref=backref('cassandra_queries', cascade='all, delete, delete-orphan'))

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

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('imap_conns', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class RBACRole(Base):
    """ All the roles known within a particular cluster.
    """
    __tablename__ = 'rbac_role'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('rbac_role_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey('rbac_role.id', ondelete='CASCADE'), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('rbac_roles', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class RBACPermission(Base):
    """ Permissions defined in a given cluster.
    """
    __tablename__ = 'rbac_perm'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('rbac_perm_seq'), primary_key=True)
    name = Column(String(200), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('rbac_permissions', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class RBACClientRole(Base):
    """ Mappings between clients and roles they have.
    """
    __tablename__ = 'rbac_client_role'
    __table_args__ = (UniqueConstraint('client_def', 'role_id', 'cluster_id'), {})

    id = Column(Integer, Sequence('rbac_cli_rol_seq'), primary_key=True)
    name = Column(String(400), nullable=False)
    client_def = Column(String(200), nullable=False)

    role_id = Column(Integer, ForeignKey('rbac_role.id', ondelete='CASCADE'), nullable=False)
    role = relationship(RBACRole, backref=backref('rbac_client_roles', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('rbac_client_roles', order_by=client_def, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class RBACRolePermission(Base):
    """ Mappings between roles and permissions they have on given services.
    """
    __tablename__ = 'rbac_role_perm'
    __table_args__ = (UniqueConstraint('role_id', 'perm_id', 'service_id', 'cluster_id'), {})

    id = Column(Integer, Sequence('rbac_role_perm_seq'), primary_key=True)

    role_id = Column(Integer, ForeignKey('rbac_role.id', ondelete='CASCADE'), nullable=False)
    role = relationship(RBACRole, backref=backref('rbac_role_perms', order_by=id, cascade='all, delete, delete-orphan'))

    perm_id = Column(Integer, ForeignKey('rbac_perm.id', ondelete='CASCADE'), nullable=False)
    perm = relationship(RBACPermission, backref=backref('rbac_role_perms', order_by=id, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = relationship('Service', backref=backref('role_perm', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('rbac_role_permissions', order_by=id, cascade='all, delete, delete-orphan'))

    def get_name(self):
        return '{}/{}/{}/{}'.format(self.id, self.role_id, self.perm_id, self.service_id)

# ################################################################################################################################

class KVData(Base):
    """ Key/value data table.
    """
    __tablename__ = 'kv_data'
    __table_args__ = (Index('key_clust_id_idx', 'key', 'cluster_id', unique=True, mysql_length={'key':767}),)

    id = Column(Integer, Sequence('kv_data_id_seq'), primary_key=True)
    key = Column(LargeBinary(), nullable=False)
    value = Column(LargeBinary(), nullable=True)
    data_type = Column(String(200), nullable=False, default='text')
    creation_time = Column(DateTime(), nullable=False)
    expiry_time = Column(DateTime(), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=True)
    cluster = relationship(Cluster, backref=backref('kv_data', order_by=key, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class ChannelWebSocket(Base):
    """ A WebSocket connection definition.
    """
    __tablename__ = 'channel_web_socket'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'),
                      UniqueConstraint('address', 'cluster_id'), {})

    id = Column(Integer, Sequence('web_socket_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    address = Column(String(200), nullable=False)
    data_format = Column(String(20), nullable=True)
    new_token_wait_time = Column(Integer(), nullable=False)
    token_ttl = Column(Integer(), nullable=False)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)

# ################################################################################################################################
