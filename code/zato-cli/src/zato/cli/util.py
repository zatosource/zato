# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# PyOTP
import pyotp

# Zato
from zato.client import AnyServiceInvoker
from zato.common import odb, TOTP
from zato.common.crypto import CryptoManager
from zato.common.util import get_config, get_crypto_manager_from_server_config, get_odb_session_from_server_config, \
     get_server_client_auth

# ################################################################################################################################

# Type checking
import typing

if typing.TYPE_CHECKING:

    # stdlib
    from argparse import Namespace

    # Python 2/3 compatibility
    from past.builtins import unicode

    # For pyflakes
    Namespace = Namespace
    unicode = unicode

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

        # Configuration check
        self.client.invoke('zato.ping')

# ################################################################################################################################

def get_totp_info_from_args(args, default_key_label=TOTP.default_label):
    """ Returns a key and its label extracted from command line arguments
    or auto-generates a new pair if they are missing in args.
    """
    # type: (Namespace, unicode) -> (unicode, unicode)

    # If there was a key given on input, we need to validate it,
    # this report an erorr if the key cannot be used.
    if args.key:
        totp = pyotp.TOTP(args.key)
        totp.now()

        # If we are here, it means that the key was valid
        key = args.key
    else:
        key = CryptoManager.generate_totp_key()

    return key, args.key_label if args.key_label else default_key_label

# ################################################################################################################################
