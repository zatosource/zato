# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.dialects.mysql.pymysql import MySQLDialect_pymysql
from sqlalchemy.dialects.oracle.cx_oracle import OracleDialect_cx_oracle
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite
from sqlalchemy.pool import Pool

# Zato
from zato.common import engine_def, engine_def_sqlite, ping_queries, ZATO_NOT_GIVEN

logger = getLogger(__name__)

django_sa_mappings = {
    'NAME': 'sqlite_path',
    'HOST': 'host',
    'PORT': 'port',
    'USER': 'username',
    'PASSWORD': 'password',
    'odb_type': 'engine',
    'db_type': 'engine',
}

cli_sa_mappings = {
    'odb_db_name': 'db_name',
    'odb_host': 'host',
    'odb_port': 'port',
    'odb_user': 'username',
    'odb_password': 'password',
    'odb_type': 'engine',
}

def get_engine_url(args):
    attrs = {}
    is_sqlite = False
    is_django = 'NAME' in args
    has_get = getattr(args, 'get', False)

    odb_type = getattr(args, 'odb_type', None)
    if odb_type:
        is_sqlite = odb_type == 'sqlite'
    else:
        is_sqlite = args.get('engine') == 'sqlite' or args.get('db_type') == 'sqlite'

    names = ('engine', 'username', 'password', 'host', 'port', 'name', 'db_name', 'db_type', 'sqlite_path', 'odb_type',
             'odb_user', 'odb_password', 'odb_host', 'odb_port', 'odb_db_name', 'odb_type', 'ENGINE', 'NAME', 'HOST', 'USER',
             'PASSWORD', 'PORT')

    for name in names:
        if has_get:
            attrs[name] = args.get(name, '')
        else:
            attrs[name] = getattr(args, name, '')

    # Re-map Django params into SQLAlchemy params
    if is_django:
        for name in django_sa_mappings:
            value = attrs.get(name, ZATO_NOT_GIVEN)
            if value != ZATO_NOT_GIVEN:
                if not value and (name in 'db_type', 'odb_type'):
                    continue
                attrs[django_sa_mappings[name]] = value

    # Zato CLI to SQLAlchemy
    if not attrs.get('engine'):
        for name in cli_sa_mappings:
            value = attrs.get(name, ZATO_NOT_GIVEN)
            if value != ZATO_NOT_GIVEN:
                attrs[cli_sa_mappings[name]] = value

    # Re-map server ODB params into SQLAlchemy params
    if attrs['engine'] == 'sqlite':
        db_name = attrs.get('db_name')
        sqlite_path = attrs.get('sqlite_path')

        if db_name:
            attrs['sqlite_path'] = db_name

        if sqlite_path:
            attrs['db_name'] = sqlite_path

    return (engine_def_sqlite if is_sqlite else engine_def).format(**attrs)


# Taken from http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html#disconnect-handling-pessimistic
def ensure_sql_connections_exist():

    dialects_sa_mappings = {
        MySQLDialect_pymysql: 'mysql+pymysql',
        OracleDialect_cx_oracle: 'oracle',
        PGDialect_psycopg2: 'postgresql',
        SQLiteDialect_pysqlite: 'sqlite',
    }

    _ping_queries = ping_queries

    @event.listens_for(Pool, 'checkout')
    def impl(dbapi_connection, connection_record, connection_proxy):

        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(
                _ping_queries[dialects_sa_mappings[connection_proxy._pool._dialect.__class__]])
        except:
            raise exc.DisconnectionError()
        cursor.close()
