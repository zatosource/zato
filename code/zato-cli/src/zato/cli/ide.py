# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ZatoCommand

# ################################################################################################################################

class SetIDEPassword(ZatoCommand):
    """ Sets password of the default API user used by IDEs to connect to Zato.
    """
    opts = [
        {'name':'--password', 'help':'Password to set for the IDE user', 'default':''},
        {'name':'--to-stdout', 'help':'Should the password be printed to studout', 'action':'store_true'},
    ]

# ################################################################################################################################

    def is_password_required(self):
        return False

# ################################################################################################################################

    def execute(self, args):

        # Zato
        from zato.common.crypto.api import CryptoManager

        password = self.args.password or CryptoManager.generate_password()
        password = password if isinstance(password, str) else password.decode('utf8')
        password = password.replace('-', '').replace('_', '').replace('=', '')

        if self.args.to_stdout:
            # stdlib
            import sys

            sys.stdout.write(password)
            sys.stdout.write('\n')
            sys.stdout.flush()

# ################################################################################################################################
