# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import ssl
from logging import getLogger

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.api import GENERIC, URL_TYPE
from zato.common.defaults import default_cluster_id
from zato.common.odb.api import WritableTupleQuery
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericConnSec, HTTPSOAP, PubSubSubscription, \
    SecurityBase, Service
from zato.common.odb.query import http_soap_list
from zato.common.util.api import as_bool
from zato.common.util.sql import elems_with_opaque

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ssl import SSLContext
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm import Session as SASession
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strtuple

    # Dummy assignments to satisfy type checkers
    Engine = Engine
    SASession = SASession
    SSLContext = SSLContext

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Environment variables selecting and configuring the external AS2/AS4 database
    Env_Type     = 'Zato_Ext_DB_Type'
    Env_Host     = 'Zato_Ext_DB_Host'
    Env_Port     = 'Zato_Ext_DB_Port'
    Env_Username = 'Zato_Ext_DB_Username'
    Env_Password = 'Zato_Ext_DB_Password'
    Env_Name     = 'Zato_Ext_DB_Name'

    # Environment variables configuring SSL/TLS for the external AS2/AS4 database
    Env_SSL           = 'Zato_Ext_DB_SSL'
    Env_SSL_CA_File   = 'Zato_Ext_DB_SSL_CA_File'
    Env_SSL_Cert_File = 'Zato_Ext_DB_SSL_Cert_File'
    Env_SSL_Key_File  = 'Zato_Ext_DB_SSL_Key_File'
    Env_SSL_Verify    = 'Zato_Ext_DB_SSL_Verify'

    # Recognized database types
    Type_MySQL      = 'mysql'
    Type_PostgreSQL = 'postgresql'

    # SSL is off unless requested explicitly
    Default_SSL = False

    # When SSL is on, the server certificate is verified unless turned off explicitly
    Default_SSL_Verify = True

    # Ids of objects from the external database receive this offset
    # so they can never collide with ids of objects from the main ODB.
    ID_Offset = 1_000_000_000

    # The name of the cluster row seeded into the external database
    Cluster_Name = 'zato-ext-db'

# ################################################################################################################################
# ################################################################################################################################

# Object types whose configuration lives in the external database when one is configured -
# HTTP transports first, the generic connection type last.
ext_db_object_types = (URL_TYPE.AS2, URL_TYPE.AS4, GENERIC.CONNECTION.TYPE.OUTCONN_AS2)

# SQLAlchemy dialects for each database type
_dialects = {
    ModuleCtx.Type_MySQL:      'mysql+pymysql',
    ModuleCtx.Type_PostgreSQL: 'postgresql+pg8000',
}

# Default ports for each database type
_default_ports = {
    ModuleCtx.Type_MySQL:      3306,
    ModuleCtx.Type_PostgreSQL: 5432,
}

# ################################################################################################################################
# ################################################################################################################################

def is_ext_db_configured() -> 'bool':
    """ Tells whether an external AS2/AS4 database is configured through environment variables.
    """
    out = bool(os.environ.get(ModuleCtx.Env_Type, ''))
    return out

# ################################################################################################################################

def needs_ext_db(object_type:'str') -> 'bool':
    """ Tells whether configuration objects of this type - an HTTP transport or a generic connection type -
    belong to the external AS2/AS4 database.
    """
    if not is_ext_db_configured():
        return False

    out = object_type in ext_db_object_types
    return out

# ################################################################################################################################

def is_ext_object_id(object_id:'int') -> 'bool':
    """ Tells whether this id points to an object stored in the external AS2/AS4 database.
    """
    if not is_ext_db_configured():
        return False

    out = object_id >= ModuleCtx.ID_Offset
    return out

# ################################################################################################################################

def to_public_id(object_id:'int') -> 'int':
    """ Maps an id local to the external database to the id the object is known under everywhere else.
    """
    out = object_id + ModuleCtx.ID_Offset
    return out

# ################################################################################################################################

def to_local_id(object_id:'int') -> 'int':
    """ Maps a public id of an external-database object back to the id it has in that database.
    """
    out = object_id - ModuleCtx.ID_Offset
    return out

# ################################################################################################################################

def _build_ssl_context() -> 'SSLContext':
    """ Builds an SSL context out of the Zato_Ext_DB_SSL_* environment variables.
    """
    ca_file   = os.environ.get(ModuleCtx.Env_SSL_CA_File, '')
    cert_file = os.environ.get(ModuleCtx.Env_SSL_Cert_File, '')
    key_file  = os.environ.get(ModuleCtx.Env_SSL_Key_File, '')

    # The server certificate is verified by default when SSL is on ..
    if verify := os.environ.get(ModuleCtx.Env_SSL_Verify, ''):
        needs_verify = as_bool(verify)
    else:
        needs_verify = ModuleCtx.Default_SSL_Verify

    # .. verify against the given CA or, if none was given, against the system store ..
    if ca_file:
        out = ssl.create_default_context(cafile=ca_file)
    else:
        out = ssl.create_default_context()

    # .. a client certificate is only needed for mutual TLS ..
    if cert_file:
        out.load_cert_chain(cert_file, key_file)

    # .. and verification can be turned off explicitly.
    if not needs_verify:
        out.check_hostname = False
        out.verify_mode = ssl.CERT_NONE

    return out

# ################################################################################################################################

def _get_connect_args() -> 'stranydict':
    """ Returns driver-specific connection arguments, including SSL ones if SSL is enabled.
    """

    # Our response to produce
    out:'stranydict' = {}

    # SSL is off unless requested explicitly ..
    if ssl_enabled := os.environ.get(ModuleCtx.Env_SSL, ''):
        needs_ssl = as_bool(ssl_enabled)
    else:
        needs_ssl = ModuleCtx.Default_SSL

    if not needs_ssl:
        return out

    # .. PyMySQL and pg8000 both accept an SSL context under the same keyword.
    out['ssl'] = _build_ssl_context()

    return out

# ################################################################################################################################

def _get_engine_url(db_type:'str') -> 'str':
    """ Builds the SQLAlchemy URL for the external AS2/AS4 database out of environment variables.
    """
    dialect  = _dialects[db_type]
    host     = os.environ[ModuleCtx.Env_Host]
    username = os.environ[ModuleCtx.Env_Username]
    password = os.environ[ModuleCtx.Env_Password]
    db_name  = os.environ[ModuleCtx.Env_Name]

    if port := os.environ.get(ModuleCtx.Env_Port, ''):
        port = int(port)
    else:
        port = _default_ports[db_type]

    out = f'{dialect}://{username}:{password}@{host}:{port}/{db_name}'
    return out

# ################################################################################################################################

def init_ext_db_schema(engine:'Engine') -> 'None':
    """ Creates the AS2/AS4 tables in the external database and seeds the cluster row - both steps are idempotent.
    """

    # Only the AS2/AS4 tables plus their foreign key targets are needed in the external database.
    # The pub/sub subscription table stays empty but it must exist because deleting an http_soap row
    # makes the ORM inspect it through the table's cascading relationship to http_soap.
    tables = [
        Cluster.__table__,
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        GenericConnSec.__table__,
        PubSubSubscription.__table__,
    ]

    Base.metadata.create_all(engine, tables=tables)

    cluster_table = Cluster.__table__

    with engine.begin() as connection:

        # All the AS2/AS4 objects point to this row through their cluster_id foreign keys ..
        select_cluster = cluster_table.select().where(cluster_table.c.id == default_cluster_id)
        existing = connection.execute(select_cluster).first()

        # .. so it is seeded once, on the first connection to a given database.
        if not existing:
            db_type = os.environ[ModuleCtx.Env_Type]
            insert_cluster = cluster_table.insert().values(
                id=default_cluster_id,
                name=ModuleCtx.Cluster_Name,
                odb_type=db_type,
            )
            _ = connection.execute(insert_cluster)

# ################################################################################################################################

# Engines are cached per configuration so all the users in a process share one pool
_engine_cache:'anydict' = {}

# Session makers are cached alongside their engines
_session_maker_cache:'anydict' = {}

def _get_cache_key() -> 'strtuple':
    """ Returns a cache key covering all the environment variables that influence the engine.
    """
    values = []

    for name in (
        ModuleCtx.Env_Type,
        ModuleCtx.Env_Host,
        ModuleCtx.Env_Port,
        ModuleCtx.Env_Username,
        ModuleCtx.Env_Password,
        ModuleCtx.Env_Name,
        ModuleCtx.Env_SSL,
        ModuleCtx.Env_SSL_CA_File,
        ModuleCtx.Env_SSL_Cert_File,
        ModuleCtx.Env_SSL_Key_File,
        ModuleCtx.Env_SSL_Verify,
    ):
        value = os.environ.get(name, '')
        values.append(value)

    out = tuple(values)
    return out

# ################################################################################################################################

def get_ext_db_engine() -> 'Engine':
    """ Returns an SQLAlchemy engine for the external AS2/AS4 database, creating the schema if needed.
    Which database is used comes from the Zato_Ext_DB_* environment variables.
    """

    # Reuse a previously built engine if the configuration has not changed ..
    cache_key = _get_cache_key()

    if engine := _engine_cache.get(cache_key):
        out = engine
        return out

    # .. build the engine itself ..
    db_type      = os.environ[ModuleCtx.Env_Type]
    engine_url   = _get_engine_url(db_type)
    connect_args = _get_connect_args()
    out          = create_engine(engine_url, connect_args=connect_args, pool_pre_ping=True)

    # .. make sure the schema and the seed cluster row exist before anyone uses the engine ..
    init_ext_db_schema(out)

    # .. and cache the engine for all future callers.
    _engine_cache[cache_key] = out

    return out

# ################################################################################################################################

def get_ext_db_session() -> 'SASession':
    """ Returns a new SQLAlchemy session to the external AS2/AS4 database.
    The session uses the same writable query class as the main ODB so query results can be processed the same way.
    """
    cache_key = _get_cache_key()

    if session_maker := _session_maker_cache.get(cache_key):
        pass
    else:
        engine = get_ext_db_engine()
        session_maker = sessionmaker(bind=engine, query_cls=WritableTupleQuery)
        _session_maker_cache[cache_key] = session_maker

    out = session_maker()
    return out

# ################################################################################################################################

def get_ext_http_soap_list(cluster_id:'int', connection:'str'='', transport:'str'='') -> 'anylist':
    """ Returns HTTP objects - AS2/AS4 channels and outgoing connections - from the external database.
    Each row is a Bunch with its opaque attributes merged in and its id already offset.
    """
    session = get_ext_db_session()

    # The query prefetches all its rows so the session can be closed as soon as they are read
    try:
        result = http_soap_list(session, cluster_id, connection or None, transport or None, True, None, False)
        items = elems_with_opaque(result)
    finally:
        session.close()

    # Our response to produce
    out:'anylist' = []

    for item in items:
        item.id = to_public_id(item.id)
        out.append(item)

    return out

# ################################################################################################################################

def merge_ext_config_entries(target:'anydict', source:'anydict') -> 'None':
    """ Merges config entries read from the external database into the main config dict impl.
    The external database wins on name conflicts and its ids receive the offset.
    """
    for name, entry in source.items():
        entry['config']['id'] = to_public_id(entry['config']['id'])
        target[name] = entry

# ################################################################################################################################

def merge_ext_channel_items(target:'anylist', ext_items:'anylist') -> 'None':
    """ Merges HTTP rows from the external database into the list read from the main ODB.
    The external database wins when both have a row of the same name, connection and transport.
    Ids of the external rows are already offset.
    """

    # Collect the identity of everything the external database holds ..
    ext_keys = set()

    for item in ext_items:
        key = (item.name, item.connection, item.transport)
        ext_keys.add(key)

    # .. drop the main ODB's rows that the external database overrides ..
    to_keep:'anylist' = []

    for item in target:
        key = (item.name, item.connection, item.transport)
        if key not in ext_keys:
            to_keep.append(item)

    # .. and rebuild the list in place so the caller's reference remains valid.
    target[:] = to_keep
    target.extend(ext_items)

# ################################################################################################################################

def ensure_service_copy(session:'SASession', name:'str', impl_name:'str', cluster_id:'int') -> 'Service':
    """ Returns the external database's copy of a service row, creating it first if needed -
    http_soap rows in that database need it as their foreign key target.
    """
    service = session.query(Service).\
        filter(Service.name == name).\
        filter(Service.cluster_id == cluster_id).\
        first()

    if service:
        out = service
        return out

    cluster = session.query(Cluster).filter(Cluster.id == cluster_id).one()

    out = Service(None, name, True, impl_name, True, cluster)
    session.add(out)
    session.flush()

    return out

# ################################################################################################################################

def ensure_security_copy(session:'SASession', sec_def:'any_', cluster_id:'int') -> 'None':
    """ Mirrors a security definition row in the external database so http_soap rows there
    can point to it by id - the definition itself always lives in the main ODB.
    """
    existing = session.query(SecurityBase.id).filter(SecurityBase.id == sec_def.id).first()

    if existing:
        return

    # The copy keeps the main ODB's id so both databases refer to the definition the same way
    sec_base_table = SecurityBase.__table__

    insert_sec = sec_base_table.insert().values(
        id=sec_def.id,
        name=sec_def.name,
        username=sec_def.username,
        password=sec_def.password,
        password_type=sec_def.password_type,
        is_active=sec_def.is_active,
        sec_type=sec_def.sec_type,
        cluster_id=cluster_id,
    )

    _ = session.execute(insert_sec)
    session.flush()

# ################################################################################################################################
# ################################################################################################################################
