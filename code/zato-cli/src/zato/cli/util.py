# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.const import ServiceConst

# ################################################################################################################################
# ################################################################################################################################

if 0:

    from argparse import Namespace
    from zato.common.py23_.past.builtins import unicode
    from zato.common.typing_ import any_, anydict

    Namespace = Namespace
    unicode = unicode

# ################################################################################################################################
class Util:
    def __init__(self, server_path):
        self.server_path = server_path
        self.client = None

    def __repr__(self):
        return '<{} at {} for `{}`>'.format(self.__class__.__name__, hex(id(self)), self.server_path)

    def set_zato_client(self):

        # stdlib
        import os

        # Zato
        from zato.client import AnyServiceInvoker
        from zato.common.api import odb
        from zato.common.util.api import get_config, get_crypto_manager_from_server_config, get_odb_session_from_server_config, \
             get_server_client_auth

        class ZatoClient(AnyServiceInvoker):
            def __init__(self, *args, **kwargs):
                super(ZatoClient, self).__init__(*args, **kwargs)
                self.cluster_id = None
                self.odb_session = None

        repo_dir = os.path.join(os.path.abspath(os.path.join(self.server_path)), 'config', 'repo')
        config = get_config(repo_dir, 'server.conf')

        self.client = ZatoClient('http://{}'.format(config.main.gunicorn_bind),
            ServiceConst.API_Admin_Invoke_Url_Path, get_server_client_auth(config, repo_dir), max_response_repr=15000)

        session = get_odb_session_from_server_config(
            config, get_crypto_manager_from_server_config(config, repo_dir))

        self.client.cluster_id = session.query(odb.model.Server).\
            filter(odb.model.Server.token == config.main.token).\
            one().cluster_id

        self.client.odb_session = session

        # Configuration check
        self.client.invoke('zato.ping')

# ################################################################################################################################

def get_totp_info_from_args(args, default_key_label=None):
    """ Returns a key and its label extracted from command line arguments
    or auto-generates a new pair if they are missing in args.
    """
    # type: (Namespace, unicode) -> (unicode, unicode)

    # PyOTP
    import pyotp

    # Zato
    from zato.common.crypto.totp_ import TOTPManager
    from zato.common.api import TOTP

    default_key_label = default_key_label or TOTP.default_label

    # If there was a key given on input, we need to validate it,
    # this report an erorr if the key cannot be used.
    if args.key:
        totp = pyotp.TOTP(args.key)
        totp.now()

        # If we are here, it means that the key was valid
        key = args.key
    else:
        key = TOTPManager.generate_totp_key()

    return key, args.key_label if args.key_label else default_key_label

# ################################################################################################################################

def run_cli_command(command_class:'any_', config:'anydict', path:'any_') -> 'None':

    # stdlib
    import os

    # Bunch
    from bunch import Bunch

    args = Bunch()
    args.verbose = True
    args.store_log = False
    args.store_config = False
    args.path = path or os.environ['ZATO_SERVER_BASE_DIR']
    args.password = None
    args.skip_stdout = False
    args.update(config)

    command = command_class(args)
    command.execute(args)

# ################################################################################################################################
