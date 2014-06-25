# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from contextlib import closing

# Bunch
from bunch import Bunch

# SQLAlchemy
import sqlalchemy
from sqlalchemy import orm

# Zato
from zato.client import AnyServiceInvoker
from zato.common import odb
from zato.common.crypto import CryptoManager
from zato.common.odb.util import get_engine_url
from zato.common.util import get_config

# ################################################################################################################################

class ZatoClient(AnyServiceInvoker):
    def __init__(self, *args, **kwargs):
        super(ZatoClient, self).__init__(*args, **kwargs)
        self.cluster_id = None
        self.odb_session = None

# ################################################################################################################################

def get_engine(args):
    return sqlalchemy.create_engine(get_engine_url(args))

def get_session(engine):
    session = orm.sessionmaker() # noqa
    session.configure(bind=engine)
    return session()

# ################################################################################################################################

def get_crypto_manager_from_server_config(config, repo_dir):

    priv_key_location = os.path.abspath(os.path.join(repo_dir, config.crypto.priv_key_location))

    cm = CryptoManager(priv_key_location=priv_key_location)
    cm.load_keys()

    return cm

# ################################################################################################################################

def get_odb_session_from_server_config(config, cm):

    engine_args = Bunch()
    engine_args.odb_type = config.odb.engine
    engine_args.odb_user = config.odb.username
    engine_args.odb_password = cm.decrypt(config.odb.password) if config.odb.password else ''
    engine_args.odb_host = config.odb.host
    engine_args.odb_port = config.odb.port
    engine_args.odb_db_name = config.odb.db_name

    return get_session(get_engine(engine_args))

# ################################################################################################################################

def get_server_client_auth(config, repo_dir):
    """ Returns credentials to authenticate with against Zato's own /zato/admin/invoke channel.
    """
    session = get_odb_session_from_server_config(config, get_crypto_manager_from_server_config(config, repo_dir))

    with closing(session) as session:
        cluster = session.query(odb.model.Server).\
            filter(odb.model.Server.token == config.main.token).\
            one().cluster

        channel = session.query(odb.model.HTTPSOAP).\
            filter(odb.model.HTTPSOAP.cluster_id == cluster.id).\
            filter(odb.model.HTTPSOAP.url_path == '/zato/admin/invoke').\
            filter(odb.model.HTTPSOAP.connection== 'channel').\
            one()

        if channel.security_id:
            security = session.query(odb.model.HTTPBasicAuth).\
                filter(odb.model.HTTPBasicAuth.id == channel.security_id).\
                first()

            if security:
                return (security.username, security.password)

# ################################################################################################################################

class Util(object):
    def __init__(self, server_path):
        self.server_path = server_path
        self.client = None

    def __repr__(self):
        return '<{} at {} for `{}`>'.format(self.__class__.__name__, hex(id(self)), self.server_path)

    def set_zato_client(self):

        repo_dir = os.path.join(os.path.abspath(os.path.join(self.server_path)), 'config', 'repo')
        config = get_config(repo_dir, 'server.conf')

        self.client = ZatoClient('http://{}'.format(config.main.gunicorn_bind),
            '/zato/admin/invoke', get_server_client_auth(config, repo_dir), max_response_repr=15000)

        session = get_odb_session_from_server_config(
            config, get_crypto_manager_from_server_config(config, repo_dir))

        self.client.cluster_id = session.query(odb.model.Server).\
            filter(odb.model.Server.token == config.main.token).\
            one().cluster_id

        self.client.odb_session = session

        # Sanity check
        self.client.invoke('zato.ping')

# ################################################################################################################################