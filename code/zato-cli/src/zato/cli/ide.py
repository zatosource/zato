# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ZatoCommand
from zato.common.const import SECRETS
from zato.common.util.api import get_odb_session_from_server_dir

# ################################################################################################################################

class SetIDEPassword(ZatoCommand):
    """ Sets password of the default API user used by IDEs to connect to Zato.
    """
    opts = [
        {'name':'--password', 'help':'Password to set for the IDE user', 'default':''},
        {'name':'--skip-stdout', 'help':'Should the password be printed to studout', 'action':'store_true'},
    ]

# ################################################################################################################################

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

        password = self.args.password or CryptoManager.generate_password()
        password = password if isinstance(password, str) else password.decode('utf8')
        password = password.replace('-', '').replace('_', '').replace('=', '')

        encrypted = self._encrypt(ServerCryptoManager, self.args, password, False)
        encrypted = SECRETS.PREFIX + encrypted.decode('utf8')

        session = None

        try:
            session = get_odb_session_from_server_dir(args.path)

            security = session.query(HTTPBasicAuth).\
                filter(HTTPBasicAuth.username == IDEDeploy.Username).\
                one() # type: HTTPBasicAuth

            security.password = encrypted

            session.add(security)
            session.commit()

        except Exception:
            raise

        finally:
            if session:
                session.close()

        if not args.skip_stdout:
            sys.stdout.write(password)
            sys.stdout.write('\n')
            sys.stdout.flush()

# ################################################################################################################################
