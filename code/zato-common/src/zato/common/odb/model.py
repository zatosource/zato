# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps

# SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, \
     ForeignKey, Sequence, Boolean, LargeBinary, UniqueConstraint, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

# Zato
from zato.common.util import make_repr, object_attrs

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
    will create a new one, and so on.
    """
    __tablename__ = 'install_state'

    id = Column(Integer,  Sequence('install_state_seq'), primary_key=True)
    version = Column(String(200), unique=True, nullable=False)
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

    id = Column(Integer,  Sequence('cluster_id_seq'), primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    odb_type = Column(String(30), nullable=False)
    odb_host = Column(String(200), nullable=False)
    odb_port = Column(Integer(), nullable=False)
    odb_user = Column(String(200), nullable=False)
    odb_db_name = Column(String(200), nullable=False)
    odb_schema = Column(String(200), nullable=True)
    zeromq_host = Column(String(200), nullable=False)
    zeromq_port = Column(Integer(), nullable=False)
    lb_host = Column(String(200), nullable=False)
    lb_agent_port = Column(Integer(), nullable=False)
    sec_server_host = Column(String(200), nullable=False)
    sec_server_port = Column(Integer(), nullable=False)

    def __init__(self, id=None, name=None, description=None, odb_type=None,
                 odb_host=None, odb_port=None, odb_user=None, odb_db_name=None,
                 odb_schema=None, zeromq_host=None, zeromq_port=None,
                 lb_host=None, lb_agent_port=None,
                 sec_server_host=None, sec_server_port=None):
        self.id = id
        self.name = name
        self.description = description
        self.odb_type = odb_type
        self.odb_host = odb_host
        self.odb_port = odb_port
        self.odb_user = odb_user
        self.odb_db_name = odb_db_name
        self.odb_schema = odb_schema
        self.zeromq_host = zeromq_host
        self.zeromq_port = zeromq_port
        self.lb_host = lb_host
        self.lb_agent_port = lb_agent_port
        self.sec_server_host = sec_server_host
        self.sec_server_port = sec_server_port

    def __repr__(self):
        return make_repr(self)

    def to_json(self):
        return to_json(self)

class Server(Base):
    """ Represents a Zato server.
    """
    __tablename__ = 'server'
    __table_args__ = (UniqueConstraint('name', 'cluster_id'), {})

    id = Column(Integer,  Sequence('server_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    
    last_join_status = Column(String(40), nullable=True)
    last_join_mod_date = Column(DateTime(timezone=True), nullable=True)
    last_join_mod_by = Column(String(200), nullable=True)
    
    odb_token = Column(String(32), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('servers', order_by=name))

    def __init__(self, id=None, name=None, cluster=None, odb_token=None,
                 last_join_status=None, last_join_mod_date=None, last_join_mod_by=None):
        self.id = id
        self.name = name
        self.cluster = cluster
        self.odb_token = odb_token
        self.last_join_status = last_join_status
        self.last_join_mod_date = last_join_mod_date
        self.last_join_mod_by = last_join_mod_by

    def __repr__(self):
        return make_repr(self)
    
################################################################################

class ChannelURLSecurity(Base):
    """ An association table for the many-to-many mapping bettween channel URL
        definitions and security definitions.
    """
    __tablename__ = 'channel_url_security'
    
    id = Column(Integer, primary_key=True)
    
    channel_url_def_id = Column(Integer, ForeignKey('channel_url_def.id'))
    channel_url_def = relationship('ChannelURLDefinition', 
                        backref=backref('channel_url_security', uselist=False))
    
    security_def_id = Column(Integer, ForeignKey('security_def.id'), nullable=False)
    security_def = relationship('SecurityDefinition', 
                    backref=backref('channel_url_security_defs', order_by=id))
    
    def __init__(self, channel_url_def, security_def):
        self.channel_url_def = channel_url_def
        self.security_def = security_def
    
################################################################################

class SecurityDefinition(Base):
    """ A security definition
    """
    __tablename__ = 'security_def'
    
    id = Column(Integer,  Sequence('security_def_id_seq'), primary_key=True)
    security_def_type = Column(String(45), nullable=False)
    
    def __init__(self, id=None, security_def_type=None):
        self.id = id
        self.security_def_type = security_def_type
        
    def __repr__(self):
        return make_repr(self)

################################################################################

class ChannelURLDefinition(Base):
    """ A channel's URL definition.
    """
    __tablename__ = 'channel_url_def'
    __table_args__ = (UniqueConstraint('cluster_id', 'url_pattern'), {})

    id = Column(Integer,  Sequence('channel_url_def_id_seq'), primary_key=True)
    url_pattern = Column(String(400), nullable=False)
    url_type = Column(String(45), nullable=False)
    is_internal = Column(Boolean(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('channel_url_defs', order_by=url_pattern))
    
    def __init__(self, id=None, url_pattern=None, url_type=None, is_internal=None,
                 cluster=None):
        self.id = id
        self.url_pattern = url_pattern
        self.url_type = url_type
        self.is_internal = is_internal
        self.cluster = cluster

    def __repr__(self):
        return make_repr(self)

################################################################################

class WSSDefinition(Base):
    """ A WS-Security definition.
    """
    __tablename__ = 'wss_def'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'), {})

    id = Column(Integer,  Sequence('wss_def_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    password_type = Column(String(45), nullable=False)
    reject_empty_nonce_ts = Column(Boolean(), nullable=False)
    reject_stale_username = Column(Boolean(), nullable=True)
    expiry_limit = Column(Integer(), nullable=False)
    nonce_freshness = Column(Integer(), nullable=True)
    
    is_active = Column(Boolean(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('wss_defs', order_by=name))
    
    security_def_id = Column(Integer, ForeignKey('security_def.id'), 
                             nullable=True)
    security_def = relationship(SecurityDefinition, backref=backref('wss_def', 
                                                    order_by=name, uselist=False))

    def __init__(self, id=None, name=None, is_active=None, username=None, 
                 password=None, password_type=None, reject_empty_nonce_ts=None, 
                 reject_stale_username=None, expiry_limit=None, 
                 nonce_freshness=None, cluster=None, password_type_raw=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.password = password
        self.password_type = password_type
        self.reject_empty_nonce_ts = reject_empty_nonce_ts
        self.reject_stale_username = reject_stale_username
        self.expiry_limit = expiry_limit
        self.nonce_freshness = nonce_freshness
        self.cluster = cluster
        self.password_type_raw = password_type_raw

    def __repr__(self):
        return make_repr(self)
    
class HTTPBasicAuth(Base):
    """ An HTTP Basic Auth definition.
    """
    __tablename__ = 'http_basic_auth_def'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'), {})

    id = Column(Integer,  Sequence('http_b_auth_def_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    domain = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    
    is_active = Column(Boolean(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('http_basic_auth_defs', order_by=name))
    
    security_def_id = Column(Integer, ForeignKey('security_def.id'), 
                             nullable=True)
    security_def = relationship(SecurityDefinition, backref=backref('http_basic_auth_def', 
                                                    order_by=name, uselist=False))

    def __init__(self, id=None, name=None, is_active=None, username=None, 
                 domain=None, password=None, cluster=None):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.username = username
        self.domain = domain
        self.password = password
        self.cluster = cluster

    def __repr__(self):
        return make_repr(self)
    
class SSLAuth(Base):
    """ An SSL/TLS-based auth definition.
    """
    __tablename__ = 'ssl_auth_def'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'), {})

    id = Column(Integer,  Sequence('ssl_def_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('ssl_defs', order_by=name))
    
    security_def_id = Column(Integer, ForeignKey('security_def.id'), 
                             nullable=True)
    security_def = relationship(SecurityDefinition, backref=backref('ssl_auth_def', 
                                    order_by=name, uselist=False))

    def __init__(self, id=None, name=None, is_active=None, cluster=None,
                 definition_text=''):
        self.id = id
        self.name = name
        self.is_active = is_active
        self.cluster = cluster
        self.definition_text = definition_text # Not used by the database

    def __repr__(self):
        return make_repr(self)
    
class SSLAuthItem(Base):
    """ A particular key/value pair of a given SSL/TLS-based auth definition.
    """
    __tablename__ = 'ssl_auth_def_item'
    __table_args__ = (UniqueConstraint('def_id', 'field', 'value'), {})
    
    id = Column(Integer,  Sequence('ssl_def_item_id_seq'), primary_key=True)
    field = Column(String(200), nullable=False)
    operator = Column(String(20), nullable=False)
    value = Column(String(200), nullable=False)
    
    def_id = Column(Integer, ForeignKey('ssl_auth_def.id', ondelete='CASCADE'),
                    nullable=False)
    def_ = relationship(SSLAuth, backref=backref('items', order_by=field,
                    cascade='all, delete, delete-orphan', single_parent=True))
    
    def __init__(self, id=None, field=None, operator=None, value=None, def_=None):
        self.id = id
        self.field = field
        self.operator = operator
        self.value = value
        self.def_ = def_

################################################################################

class TechnicalAccount(Base):
    """ Stores information about technical accounts, used for instance by Zato
    itself for securing access to its API.
    """
    __tablename__ = 'tech_account'
    __table_args__ = (UniqueConstraint('name'), {})
    
    id = Column(Integer,  Sequence('tech_account_id_seq'), primary_key=True)
    name = Column(String(45), nullable=False)
    password = Column(String(64), nullable=False)
    salt = Column(String(32), nullable=False)
    is_active = Column(Boolean(), nullable=False)
    
    security_def_id = Column(Integer, ForeignKey('security_def.id'), 
                             nullable=True)
    security_def = relationship(SecurityDefinition, 
                backref=backref('tech_account', order_by=id, uselist=False))
    
    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('tech_accounts', order_by=name))
    
    def __init__(self, id=None, name=None, password=None, salt=None, 
                 is_active=None, security_def=None, expected_password=None,
                 cluster=None):
        self.id = id
        self.name = name
        self.password = password
        self.salt = salt
        self.is_active = is_active
        self.security_def = security_def
        self.expected_password = expected_password
        self.cluster = cluster
        
    def to_json(self):
        return to_json(self)

################################################################################

class Service(Base):
    """ A Zato service.
    """
    __tablename__ = 'service'
    __table_args__ = (UniqueConstraint('name'), UniqueConstraint('impl_name'), {})
    
    id = Column(Integer,  Sequence('service_id_seq'), primary_key=True)
    name = Column(String(2000), nullable=False)
    impl_name = Column(String(2000), nullable=False)
    usage_count = Column(Integer(), server_default='0', nullable=False)
    is_internal = Column(Boolean(), nullable=False)
        
################################################################################

class SQLConnectionPool(Base):
    """ An SQL connection pool.
    """
    __tablename__ = 'sql_pool'
    __table_args__ = (UniqueConstraint('cluster_id', 'name'), {})

    id = Column(Integer,  Sequence('sql_pool_id_seq'), primary_key=True)
    name = Column(String(200), nullable=False)
    user = Column(String(200), nullable=False)
    db_name = Column(String(200), nullable=False)
    engine = Column(String(200), nullable=False)
    extra = Column(LargeBinary(200000), nullable=True)
    host = Column(String(200), nullable=False)
    port = Column(Integer(), nullable=False)
    pool_size = Column(Integer(), nullable=False)

    cluster_id = Column(Integer, ForeignKey('cluster.id'), nullable=False)
    cluster = relationship(Cluster, backref=backref('sql_pools', order_by=name))

    def __init__(self, id=None, name=None, db_name=None, user=None, engine=None,
                 extra=None, host=None, port=None, pool_size=None, cluster=None):
        self.id = id
        self.name = name
        self.db_name = db_name
        self.user = user
        self.engine = engine
        self.extra = extra
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.cluster = cluster

    def __repr__(self):
        return make_repr(self)

class SQLConnectionPoolPassword(Base):
    """ An SQL connection pool's passwords.
    """
    __tablename__ = 'sql_pool_passwd'

    id = Column(Integer,  Sequence('sql_pool_id_seq'), primary_key=True)
    password = Column(LargeBinary(200000), server_default='not-set-yet', nullable=False)
    server_key_hash = Column(LargeBinary(200000), server_default='not-set-yet', nullable=False)

    server_id = Column(Integer, ForeignKey('server.id'), nullable=False)
    server = relationship(Server, backref=backref('sql_pool_passwords', order_by=id))

    sql_pool_id = Column(Integer, ForeignKey('sql_pool.id'), nullable=False)
    sql_pool = relationship(SQLConnectionPool, backref=backref('sql_pool_passwords', order_by=id))

    def __init__(self, id=None, password=None, server_key_hash=None, server_id=None,
                 server=None, sql_pool_id=None, sql_pool=None):
        self.id = id
        self.password = password
        self.server_key_hash = server_key_hash
        self.server_id = server_id
        self.server = server
        self.sql_pool_id = sql_pool_id
        self.sql_pool = sql_pool

    def __repr__(self):
        return make_repr(self)
