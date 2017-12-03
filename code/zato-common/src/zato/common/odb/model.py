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
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, LargeBinary, Sequence, \
     SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

# Zato
from zato.common import AMQP, CASSANDRA, CLOUD, CONNECTION, DATA_FORMAT, HTTP_SOAP_SERIALIZATION_TYPE, MISC, NOTIF, \
     MSG_PATTERN_TYPE, ODOO, PUBSUB, SCHEDULER, STOMP, PARAMS_PRIORITY, URL_PARAMS_PRIORITY, URL_TYPE
from zato.common.odb import WMQ_DEFAULT_PRIORITY

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

    # It's nullable because some children classes do not use usernames
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

    def __init__(self, id=None, name=None, is_active=None, username=None, password=None, ttl=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.ttl = ttl
        self.cluster = cluster

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

class VaultConnection(SecurityBase):
    """ Stores information on how to connect to Vault and how to authenticate against it by default.
    """
    __tablename__ = 'sec_vault_conn'
    __mapper_args__ = {'polymorphic_identity':'vault_conn_sec'}

    id = Column(Integer, ForeignKey('sec_base.id'), primary_key=True)
    url = Column(String(200), nullable=False)
    token = Column(String(200), nullable=True)
    default_auth_method = Column(String(200), nullable=True)
    timeout = Column(Integer, nullable=False)
    allow_redirects = Column(Boolean(), nullable=False)
    tls_verify = Column(Boolean(), nullable=False)

    tls_key_cert_id = Column(Integer, ForeignKey('sec_tls_key_cert.id', ondelete='CASCADE'), nullable=True)
    tls_ca_cert_id = Column(Integer, ForeignKey('sec_tls_ca_cert.id', ondelete='CASCADE'), nullable=True)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    service = relationship('Service', backref=backref('vault_conn_list', order_by=id, cascade='all, delete, delete-orphan'))

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
    __table_args__ = (
        UniqueConstraint('name', 'connection', 'transport', 'cluster_id'),
        Index('path_host_conn_act_clus_idx', 'url_path', 'host', 'connection', 'soap_action', 'cluster_id', unique=True), {})

    id = Column(Integer, Sequence('http_soap_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    connection = Column(Enum(CONNECTION.CHANNEL, CONNECTION.OUTGOING, name='http_soap_connection'), nullable=False)
    transport = Column(Enum(URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP, name='http_soap_transport'), nullable=False)

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

    has_rbac = Column(Boolean, nullable=False, default=False)
    sec_use_rbac = Column(Boolean(), nullable=False, default=False)

    cache_expiry = Column(Integer, nullable=True, default=0)

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)
    security = relationship(SecurityBase, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    sec_tls_ca_cert_id = Column(Integer, ForeignKey('sec_tls_ca_cert.id', ondelete='CASCADE'), nullable=True)
    sec_tls_ca_cert = relationship('TLSCACert', backref=backref('http_soap', order_by=name, cascade='all, delete, delete-orphan'))

    cache_id = Column(Integer, ForeignKey('cache.id', ondelete='CASCADE'), nullable=True)
    cache = relationship('Cache', backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    service = relationship('Service', backref=backref('http_soap', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('http_soap_list', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, is_internal=None, connection=None, transport=None, host=None,
                 url_path=None, method=None, soap_action=None, soap_version=None, data_format=None, ping_method=None,
                 pool_size=None, merge_url_params_req=None, url_params_pri=None, params_pri=None, serialization_type=None,
                 timeout=None, sec_tls_ca_cert_id=None, service_id=None, service=None, security=None, cluster_id=None,
                 cluster=None, service_name=None, security_id=None, has_rbac=None, security_name=None, content_type=None,
                 cache_id=None, cache_type=None, cache_expiry=None, cache_name=None):
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
        self.cache_id = cache_id
        self.cache_type = cache_type
        self.cache_expiry = cache_expiry
        self.cache_name = cache_name # Not used by the DB

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

        self.docs_summary = None # Not used by the database
        self.docs_description = None # Not used by the database
        self.invokes = None # Not used by the database
        self.invoked_by = None # Not used by the database

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

# ################################################################################################################################

class CacheMemcached(Cache):
    """ Cache definitions using Memcached.
    """
    __tablename__ = 'cache_memcached'
    __mapper_args__ = {'polymorphic_identity':'memcached'}

    cache_id = Column(Integer, ForeignKey('cache.id'), primary_key=True)
    servers = Column(Text, nullable=False)
    is_debug = Column(Boolean(), nullable=False)
    extra = Column(LargeBinary(20000), nullable=True)

# ################################################################################################################################

class ConnDefAMQP(Base):
    """ An AMQP connection definition.
    """
    __tablename__ = 'conn_def_amqp'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer, Sequence('conn_def_amqp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)

    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    vhost = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    frame_max = Column(Integer(), nullable=False)
    heartbeat = Column(Integer(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('amqp_conn_defs', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, host=None, port=None, vhost=None, username=None, password=None, frame_max=None,
            heartbeat=None, cluster_id=None):
        self.id = id
        self.name = name
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
    priority = Column(SmallInteger(), server_default=str(AMQP.DEFAULT.PRIORITY), nullable=False)

    content_type = Column(String(200), nullable=True)
    content_encoding = Column(String(200), nullable=True)
    expiration = Column(Integer(), nullable=True)
    user_id = Column(String(200), nullable=True)
    app_id = Column(String(200), nullable=True)
    pool_size = Column(SmallInteger(), nullable=False)

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
    pool_size = Column(Integer, nullable=False)
    ack_mode = Column(String(20), nullable=False)
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

    id = Column(Integer, Sequence('web_socket_chan_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    address = Column(String(200), nullable=False)
    data_format = Column(String(20), nullable=False)
    new_token_wait_time = Column(Integer(), nullable=False)
    token_ttl = Column(Integer(), nullable=False)

    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)
    service = relationship('Service', backref=backref('web_socket', order_by=name, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('web_socket_list', order_by=name, cascade='all, delete, delete-orphan'))

    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)
    security = relationship(SecurityBase, backref=backref('web_socket_list', order_by=name, cascade='all, delete, delete-orphan'))

    def __init__(self, id=None, name=None, is_active=None, is_internal=None, address=None, data_format=None,
            new_token_wait_time=None, token_ttl=None, service_id=None, service=None, cluster_id=None, cluster=None,
            security_id=None, security=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.is_internal = is_internal
        self.address = address
        self.data_format = data_format
        self.new_token_wait_time = new_token_wait_time
        self.token_ttl = token_ttl
        self.service_id = service_id
        self.service = service
        self.cluster_id = cluster_id
        self.cluster = cluster
        self.security_id = security_id
        self.security = security
        self.service_name = None # Not used by DB
        self.sec_type = None # Not used by DB

# ################################################################################################################################

class WebSocketClient(Base):
    """ An active WebSocket client - currently connected to a Zato server process.
    """
    __tablename__ = 'web_socket_client'
    __table_args__ = (
        Index('wscl_pub_client_idx', 'cluster_id', 'pub_client_id', unique=True),
        Index('wscl_cli_ext_n_idx', 'cluster_id', 'ext_client_name', unique=False),
        Index('wscl_cli_ext_i_idx', 'cluster_id', 'ext_client_id', unique=False),
        Index('wscl_pr_addr_idx', 'cluster_id', 'peer_address', unique=False),
        Index('wscl_pr_fqdn_idx', 'cluster_id', 'peer_fqdn', unique=False),
    {})

    # This ID is for SQL
    id = Column(Integer, Sequence('web_socket_cli_seq'), primary_key=True)

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

    server_proc_pid = Column(Integer, nullable=False)
    server_name = Column(String(200), nullable=False) # References server.name

    channel_id = Column(Integer, ForeignKey('channel_web_socket.id', ondelete='CASCADE'), nullable=False)
    channel = relationship(
        ChannelWebSocket, backref=backref('clients', order_by=local_address, cascade='all, delete, delete-orphan'))

    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=False)
    server = relationship(
        Server, backref=backref('server_web_socket_clients', order_by=local_address, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(
        Cluster, backref=backref('web_socket_client_list', order_by=last_seen, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class WebSocketClientPubSubKeys(Base):
    """ Associates currently active WebSocket clients with subscription keys.
    """
    __tablename__ = 'web_socket_cli_ps_keys'
    __table_args__ = (
        Index('wscl_psk_cli', 'cluster_id', 'client_id', unique=False),
        Index('wscl_psk_sk', 'cluster_id', 'sub_key', unique=False),
    {})

    id = Column(Integer, Sequence('web_socket_cli_ps_seq'), primary_key=True)

    # The same as in web_socket_sub.sub_key
    sub_key = Column(Text, nullable=False)

    client_id = Column(Integer, ForeignKey('web_socket_client.id', ondelete='CASCADE'), nullable=False)
    client = relationship(
        WebSocketClient, backref=backref('web_socket_cli_ps_keys', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref(
        'web_socket_cli_ps_keys', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class WebSocketSubscription(Base):
    """ Persistent subscriptions pertaining to a given long-running, possibly restartable, WebSocket connection.
    """
    __tablename__ = 'web_socket_sub'
    __table_args__ = (
        Index('wssub_channel_idx', 'cluster_id', 'channel_id', unique=False),
        Index('wssub_subkey_idx', 'cluster_id', 'sub_key', unique=True),
        Index('wssub_extcli_idx', 'cluster_id', 'ext_client_id', unique=True),
        Index('wssub_subkey_chan_idx', 'cluster_id', 'sub_key', 'channel_id', unique=True),
    {})

    id = Column(Integer, Sequence('web_socket_sub_seq'), primary_key=True)
    is_internal = Column(Boolean(), nullable=False)
    sub_key = Column(Text, nullable=False)
    ext_client_id = Column(Text(), nullable=False)

    channel_id = Column(Integer, ForeignKey('channel_web_socket.id', ondelete='CASCADE'), nullable=True)
    channel = relationship(
        ChannelWebSocket, backref=backref('web_socket_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('web_socket_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class PubSubEndpoint(Base):
    """ An individual endpoint participating in publish/subscribe scenarios.
    """
    __tablename__ = 'pubsub_endpoint'
    __table_args__ = (
        Index('pubsb_endp_clust_idx', 'cluster_id', unique=False),
        Index('pubsb_endp_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_endp_name_idx', 'cluster_id', 'name', unique=True),
        UniqueConstraint('cluster_id', 'name'),
        UniqueConstraint('cluster_id', 'security_id'),
        UniqueConstraint('cluster_id', 'service_id'),
        UniqueConstraint('cluster_id', 'ws_channel_id'),
    {})

    id = Column(Integer, Sequence('pubsub_endp_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)
    is_active = Column(Boolean(), nullable=False, default=True) # Unusued for now
    endpoint_type = Column(String(40), nullable=False) # WSX, REST, AMQP and other types

    last_seen = Column(BigInteger(), nullable=True)
    last_pub_time = Column(BigInteger(), nullable=True)
    last_sub_time = Column(BigInteger(), nullable=True)
    last_deliv_time = Column(BigInteger(), nullable=True)

    # Endpoint's role, e.g. publisher, subscriber or both
    role = Column(String(40), nullable=False)

    # Tags describing this endpoint
    tags = Column(Text, nullable=True) # Unusued for now

    # Patterns for topics that this endpoint may subscribe to
    topic_patterns = Column(Text, nullable=True)

    # Patterns for tags of publishers
    pub_tag_patterns = Column(Text, nullable=True) # Unused for now

    # Patterns for tags of messages
    message_tag_patterns = Column(Text, nullable=True) # Unused for now

    # Endpoint is a service
    service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)

    # Identifies the endpoint through its security definition, e.g. a username/password combination.
    security_id = Column(Integer, ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=True)
    security = relationship(SecurityBase, backref=backref('pubsub_endpoints', order_by=id, cascade='all, delete, delete-orphan'))

    # Identifies the endpoint through a long-running WebSockets channel
    ws_channel_id = Column(Integer, ForeignKey('channel_web_socket.id', ondelete='CASCADE'), nullable=True)
    ws_channel = relationship(
        ChannelWebSocket, backref=backref('pubsub_endpoints', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pubsub_endpoints', order_by=id, cascade='all, delete, delete-orphan'))

    sec_type = None          # Not used by DB
    sec_name = None          # Not used by DB
    ws_channel_name = None   # Not used by DB
    service_name = None      # Not used by DB

# ################################################################################################################################

class PubSubTopic(Base):
    """ A topic in pub/sub.
    """
    __tablename__ = 'pubsub_topic'
    __table_args__ = (
        Index('pubsb_tp_clust_idx', 'cluster_id', unique=False),
        Index('pubsb_tp_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_tp_name_idx', 'cluster_id', 'name', unique=True),
    {})

    id = Column(Integer, Sequence('pubsub_topic_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)
    last_pub_time = Column(BigInteger(), nullable=True)
    max_depth_gd = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.TOPIC_MAX_DEPTH_GD)
    max_depth_non_gd = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.TOPIC_MAX_DEPTH_NON_GD)
    current_depth_gd = Column(Integer(), nullable=False, default=0)
    gd_depth_check_freq = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.GD_DEPTH_CHECK_FREQ)
    has_gd = Column(Boolean(), nullable=False) # Guaranteed delivery
    is_api_sub_allowed = Column(Boolean(), nullable=False)

    # A hook service invoked during publications to this specific topic
    hook_service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pubsub_topics', order_by=name, cascade='all, delete, delete-orphan'))

    ext_client_id = None # Not used by DB

# ################################################################################################################################

class PubSubEndpointTopic(Base):
    """ A list of topics to which a given endpoint has ever published along with metadata about the latest publication.
    There is one row for each existing publisher and topic ever in use.
    """
    __tablename__ = 'pubsub_endp_topic'
    __table_args__ = (
        Index('pubsb_endpt_clust_idx', 'cluster_id', unique=False),
        Index('pubsb_endpt_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_endpt_msgid_idx', 'cluster_id', 'pub_msg_id', unique=True),
        Index('pubsb_endpt_clsendtp_idx', 'cluster_id', 'endpoint_id', 'topic_id', unique=True),
    {})

    id = Column(Integer, Sequence('pubsub_endpt_seq'), primary_key=True)

    pattern_matched = Column(Text, nullable=False)
    last_pub_time = Column(BigInteger(), nullable=False)
    pub_msg_id = Column(String(200), nullable=False)
    pub_correl_id = Column(String(200), nullable=True)
    in_reply_to = Column(String(200), nullable=True)
    ext_client_id = Column(Text(), nullable=True)

    endpoint_id = Column(Integer, ForeignKey('pubsub_endpoint.id', ondelete='CASCADE'), nullable=True)
    endpoint = relationship(
        PubSubEndpoint, backref=backref('pubsub_endpoint_topics', order_by=endpoint_id, cascade='all, delete, delete-orphan'))

    topic_id = Column(Integer, ForeignKey('pubsub_topic.id', ondelete='CASCADE'), nullable=False)
    topic = relationship(
        PubSubTopic, backref=backref('pubsub_endpoint_topics', order_by=topic_id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pubsub_endpoint_topics', order_by=cluster_id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class PubSubMessage(Base):
    """ An individual message published to a topic.
    """
    __tablename__ = 'pubsub_message'
    __table_args__ = (
        Index('pubsb_msg_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_msg_pubmsg_id_idx', 'cluster_id', 'pub_msg_id', unique=True),
        Index('pubsb_msg_inreplyto_id_idx', 'cluster_id', 'in_reply_to', unique=False),
    {})

    # For SQL joins
    id = Column(Integer, Sequence('pubsub_msg_seq'), primary_key=True)

    # Publicly visible message identifier
    pub_msg_id = Column(String(200), nullable=False)

    # Publicly visible correlation ID
    pub_correl_id = Column(String(200), nullable=True)

    # Publicly visible ID of the message current message is a response to
    in_reply_to = Column(String(200), nullable=True)

    # ID of an external client on whose behalf the endpoint published the message
    ext_client_id = Column(Text(), nullable=True)

    # Will group messages belonging logically to the same group, useful if multiple
    # messages are published with the same timestamp by the same client but they still
    # need to be correctly ordered.
    group_id = Column(Text(), nullable=True)
    position_in_group = Column(Integer, nullable=True)

    # What matching pattern allowed an endpoint to publish this message
    pattern_matched = Column(Text, nullable=False)

    pub_time = Column(BigInteger(), nullable=False) # When the row was created
    ext_pub_time = Column(BigInteger(), nullable=True) # When the message was created by publisher
    expiration_time = Column(BigInteger(), nullable=True)
    last_updated = Column(BigInteger(), nullable=True)

    data = Column(Text(), nullable=False)
    data_prefix = Column(Text(), nullable=False)
    data_prefix_short = Column(String(200), nullable=False)
    data_format = Column(String(200), nullable=False, default=PUBSUB.DEFAULT.DATA_FORMAT)
    mime_type = Column(String(200), nullable=False)
    size = Column(Integer, nullable=False)
    priority = Column(Integer, nullable=False)
    expiration = Column(Integer, nullable=False, default=0)
    has_gd = Column(Boolean(), nullable=False) # Guaranteed delivery

    published_by_id = Column(Integer, ForeignKey('pubsub_endpoint.id', ondelete='CASCADE'), nullable=False)
    published_by = relationship(
        PubSubEndpoint, backref=backref('pubsub_msg_list', order_by=id, cascade='all, delete, delete-orphan'))

    topic_id = Column(Integer, ForeignKey('pubsub_topic.id', ondelete='CASCADE'), nullable=True)
    topic = relationship(
        PubSubTopic, backref=backref('pubsub_msg_list', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pubsub_messages', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class PubSubSubscription(Base):
    """ Stores high-level information about topics an endpoint subscribes to.
    """
    __tablename__ = 'pubsub_sub'
    __table_args__ = (
        Index('pubsb_sub_clust_idx', 'cluster_id', unique=False),
        Index('pubsb_sub_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_sub_clust_endpt_idx', 'cluster_id', 'endpoint_id', 'topic_id', unique=False),
        Index('pubsb_sub_clust_subk', 'cluster_id', 'sub_key', unique=True),
    {})

    id = Column(Integer, Sequence('pubsub_sub_seq'), primary_key=True)
    is_internal = Column(Boolean(), nullable=False, default=False)

    creation_time = Column(BigInteger(), nullable=False)
    sub_key = Column(String(200), nullable=False) # Externally visible ID of this subscription
    pattern_matched = Column(Text, nullable=False)
    deliver_by = Column(Text, nullable=True) # Delivery order, e.g. by priority, date etc.
    ext_client_id = Column(Text, nullable=True) # Subscriber's ID as it is stored by that external system

    is_durable = Column(Boolean(), nullable=False, default=True) # For now always True = survives cluster restarts
    has_gd = Column(Boolean(), nullable=False) # Guaranteed delivery

    active_status = Column(String(200), nullable=False)
    is_staging_enabled = Column(Boolean(), nullable=False, default=False)

    delivery_method = Column(String(200), nullable=False, default=PUBSUB.DELIVERY_METHOD.NOTIFY.id)
    delivery_data_format = Column(String(200), nullable=False, default=DATA_FORMAT.JSON)
    delivery_endpoint = Column(Text, nullable=True)

    last_interaction_time = Column(BigInteger(), nullable=True)
    last_interaction_type = Column(String(200), nullable=True)
    last_interaction_details = Column(Text, nullable=True)

    # How many messages to deliver in a single batch for that endpoint
    delivery_batch_size = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.DELIVERY_BATCH_SIZE)

    # If delivery_batch_size is 1, whether such a single message delivered to endpoint
    # should be sent as-is or wrapped in a single-element list.
    wrap_one_msg_in_list = Column(Boolean(), nullable=False)

    # How many bytes to send at most in a single delivery
    delivery_max_size = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.DELIVERY_MAX_SIZE) # Unused for now

    # How many times to retry delivery for a single message
    delivery_max_retry = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.DELIVERY_MAX_RETRY)

    # Should a failed delivery of a single message block the entire delivery queue
    # until that particular message has been successfully delivered.
    delivery_err_should_block = Column(Boolean(), nullable=False)

    # How many seconds to wait on a TCP socket error
    wait_sock_err = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.WAIT_TIME_SOCKET_ERROR)

    # How many seconds to wait on an error other than a TCP socket one
    wait_non_sock_err = Column(Integer(), nullable=False, default=PUBSUB.DEFAULT.WAIT_TIME_NON_SOCKET_ERROR)

    # A hook service invoked before messages are delivered for this specific subscription
    hook_service_id = Column(Integer, ForeignKey('service.id', ondelete='CASCADE'), nullable=True)

    # AMQP
    amqp_exchange = Column(Text, nullable=True)
    amqp_routing_key = Column(Text, nullable=True)

    # Flat files
    files_directory_list = Column(Text, nullable=True)

    # FTP
    ftp_directory_list = Column(Text, nullable=True)

    # SMS - Twilio
    sms_twilio_from = Column(Text, nullable=True)
    sms_twilio_to_list = Column(Text, nullable=True)

    # SMTP
    smtp_subject = Column(Text, nullable=True)
    smtp_from = Column(Text, nullable=True)
    smtp_to_list = Column(Text, nullable=True)
    smtp_body = Column(Text, nullable=True)
    smtp_is_html = Column(Boolean(), nullable=True)

    topic_id = Column(Integer, ForeignKey('pubsub_topic.id', ondelete='CASCADE'), nullable=False)
    topic = relationship(
        PubSubTopic, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    endpoint_id = Column(Integer, ForeignKey('pubsub_endpoint.id', ondelete='CASCADE'), nullable=True)
    endpoint = relationship(
        PubSubEndpoint, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    out_job_id = Column(Integer, ForeignKey('job.id', ondelete='CASCADE'), nullable=True)
    out_job = relationship(
        Job, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    out_http_soap_id = Column(Integer, ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=True)
    out_http_soap = relationship(
        HTTPSOAP, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    out_smtp_id = Column(Integer, ForeignKey('email_smtp.id', ondelete='CASCADE'), nullable=True)
    out_smtp = relationship(
        SMTP, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    out_amqp_id = Column(Integer, ForeignKey('out_amqp.id', ondelete='CASCADE'), nullable=True)
    out_amqp = relationship(
        OutgoingAMQP, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    ws_sub_id = Column(Integer, ForeignKey('web_socket_sub.id', ondelete='CASCADE'), nullable=True)
    ws_sub = relationship(
        WebSocketSubscription, backref=backref('pubsub_ws_subs', order_by=id, cascade='all, delete, delete-orphan'))

    ws_channel_id = Column(Integer, ForeignKey('channel_web_socket.id', ondelete='CASCADE'), nullable=True)
    ws_channel = relationship(
        ChannelWebSocket, backref=backref('pubsub_ws_subs', order_by=id, cascade='all, delete, delete-orphan'))

    # Server that will run the delivery task for this subscription
    server_id = Column(Integer, ForeignKey('server.id', ondelete='CASCADE'), nullable=True)
    server = relationship(
        Server, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=True)
    cluster = relationship(
        Cluster, backref=backref('pubsub_sub_list', order_by=id, cascade='all, delete, delete-orphan'))

    topic_name = None # Not used by DB

# ################################################################################################################################

class PubSubEndpointEnqueuedMessage(Base):
    """ A queue of messages for an individual endpoint subscribed to a topic.
    """
    __tablename__ = 'pubsub_endp_msg_queue'
    __table_args__ = (
        Index('pubsb_enms_q_pubmid_idx', 'cluster_id', 'pub_msg_id', unique=True),
        Index('pubsb_enms_q_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_enms_q_endp_idx', 'cluster_id', 'endpoint_id', unique=False),
        Index('pubsb_enms_q_subs_idx', 'cluster_id', 'subscription_id', unique=False),
        Index('pubsb_enms_q_endptp_idx', 'cluster_id', 'endpoint_id', 'topic_id', unique=False),
    {})

    id = Column(Integer, Sequence('pubsub_msg_seq'), primary_key=True)
    creation_time = Column(BigInteger(), nullable=False) # When was the message enqueued

    delivery_count = Column(Integer, nullable=False)
    last_delivery_time = Column(BigInteger(), nullable=True)

    has_gd = Column(Boolean(), nullable=False) # Guaranteed delivery
    is_in_staging = Column(Boolean(), nullable=False, default=False)

    # A flag indicating whether this message is deliverable at all - will be set to False
    # after delivery_count reaches max retries for subscription or if a hook services decides so.
    is_deliverable = Column(Boolean(), nullable=False, default=True)

    delivery_status = Column(Text, nullable=False)
    delivery_time = Column(BigInteger(), nullable=True)

    pub_msg_id = Column(String(200), ForeignKey('pubsub_message.pub_msg_id', ondelete='CASCADE'), nullable=False)

    endpoint_id = Column(Integer, ForeignKey('pubsub_endpoint.id', ondelete='CASCADE'), nullable=True)
    endpoint = relationship(PubSubEndpoint,
        backref=backref('pubsub_endp_q_list', order_by=id, cascade='all, delete, delete-orphan'))

    topic_id = Column(Integer, ForeignKey('pubsub_topic.id', ondelete='CASCADE'), nullable=False)
    topic = relationship(PubSubTopic, backref=backref('pubsub_endp_q_list', order_by=id, cascade='all, delete, delete-orphan'))

    subscription_id = Column(Integer, ForeignKey('pubsub_sub.id', ondelete='CASCADE'), nullable=True)
    subscription = relationship(PubSubSubscription,
        backref=backref('pubsub_endp_q_list', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('pubsub_endpoint_queues', order_by=id, cascade='all, delete, delete-orphan'))

    queue_name = None # Not used by DB

# ################################################################################################################################

class PubSubEndpointQueueInteraction(Base):
    """ A series of interactions with a message queue's endpoint.
    """
    __tablename__ = 'pubsub_endp_msg_q_inter'
    __table_args__ = (
        Index('pubsb_enms_qi_id_idx', 'cluster_id', 'id', unique=True),
        Index('pubsb_enms_qi_endptp_idx', 'cluster_id', 'queue_id', unique=False),
    {})

    id = Column(Integer, Sequence('pubsub_msg_seq'), primary_key=True)
    entry_timestamp = Column(BigInteger(), nullable=False) # When the row was created

    inter_type = Column(String(200), nullable=False)
    inter_details = Column(Text, nullable=True)

    queue_id = Column(Integer, ForeignKey('pubsub_endp_msg_queue.id', ondelete='CASCADE'), nullable=False)
    queue = relationship(
        PubSubEndpointEnqueuedMessage, backref=backref(
            'pubsub_endpoint_queue_interactions', order_by=id, cascade='all, delete, delete-orphan'))

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(
        Cluster, backref=backref('pubsub_endpoint_queue_interactions', order_by=id, cascade='all, delete, delete-orphan'))

# ################################################################################################################################

class SMSTwilio(Base):
    """ Outgoing SMS connections with Twilio.
    """
    __tablename__ = 'sms_twilio'
    __table_args__ = (
        UniqueConstraint('name', 'cluster_id'),
    {})

    id = Column(Integer, Sequence('sms_twilio_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    is_internal = Column(Boolean(), nullable=False, default=False)

    account_sid = Column(String(200), nullable=False)
    auth_token = Column(String(200), nullable=False)

    default_from = Column(String(200), nullable=True)
    default_to = Column(String(200), nullable=True)

    cluster_id = Column(Integer, ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False)
    cluster = relationship(Cluster, backref=backref('sms_twilio_list', order_by=name, cascade='all, delete, delete-orphan'))

# ################################################################################################################################
