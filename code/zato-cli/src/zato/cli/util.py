# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.client import AnyServiceInvoker
from zato.common import odb
from zato.common.util import get_config, get_crypto_manager_from_server_config, get_odb_session_from_server_config, \
     get_server_client_auth

# ################################################################################################################################

class ZatoClient(AnyServiceInvoker):
    def __init__(self, *args, **kwargs):
        super(ZatoClient, self).__init__(*args, **kwargs)
        self.cluster_id = None
        self.odb_session = None

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
