# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing

# Zato
from zato.cli import ManageCommand
from zato.common.const import SECRETS
from zato.common.util.api import get_odb_session_from_server_dir

# ################################################################################################################################
# ################################################################################################################################

class SetIDEPassword(ManageCommand):
    """ Sets password of the default API user used by IDEs to connect to Zato.
    """
    opts = [
        {'name':'--password', 'help':'Password to set for the IDE user', 'default':''},
        {'name':'--skip-stdout', 'help':'Should the password be printed to studout', 'action':'store_true'},
    ]

    def is_password_required(self):
        return False

# ################################################################################################################################

    def execute(self, args):

        # stdlib
        import sys

        # Zato
        from zato.common.api import IDEDeploy
        from zato.common.crypto.api import CryptoManager, ServerCryptoManager
        from zato.common.odb.model import HTTPBasicAuth
        from zato.common.util.cli import CommandLineServiceInvoker

        password = self.args.password or CryptoManager.generate_password()
        password = password if isinstance(password, str) else password.decode('utf8')
        password = password.replace('-', '').replace('_', '').replace('=', '')

        path = args.path
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        if not os.path.exists(path):
            self.logger.warning('Path not found: %s', path)
            sys.exit(self.SYS_ERROR.NOT_A_ZATO_SERVER)

        encrypted = self._encrypt(ServerCryptoManager, self.args, password, False)
        encrypted = SECRETS.PREFIX + encrypted.decode('utf8')

        session = None
        security_id = None

        # Obtain an SQL session to the configuration database ..
        with closing(get_odb_session_from_server_dir(args.path)) as session:

            # .. get our IDE invoker's security definition ..
            security = session.query(HTTPBasicAuth).\
                filter(HTTPBasicAuth.username == IDEDeploy.Username).\
                one() # type: HTTPBasicAuth

            # .. extract the ID needed to change the password ..
            security_id = security.id

        # .. and invoke the service that changes the password ..
        invoker = CommandLineServiceInvoker(check_stdout=False, server_location=path)
        invoker.invoke('zato.security.basic-auth.change-password', {
            'id': security_id,
            'password1': password,
            'password2': password,
        })

        if not args.skip_stdout:
            sys.stdout.write(password)
            sys.stdout.write('\n')
            sys.stdout.flush()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # Zato
    from zato.cli.util import run_cli_command

    run_cli_command(SetIDEPassword, {
        'password':    None,
        'skip_stdout': False
    })

# ################################################################################################################################
# ################################################################################################################################
