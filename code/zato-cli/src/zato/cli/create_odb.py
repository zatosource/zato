# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from getpass import getuser
from socket import gethostname

# Zato
from zato.cli import common_odb_opts, is_arg_given, ZatoCommand
from zato.common.odb.model import AlembicRevision, Base, ZatoInstallState

LATEST_ALEMBIC_REVISION = '0028_ae3419a9'
VERSION = 1

# ################################################################################################################################
# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates a new Zato ODB (Operational Database)
    """
    opts = common_odb_opts
    opts.append({
        'name':'--skip-if-exists',
        'help':'Return without raising an error if ODB already exists',
        'action':'store_true'
    })

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

# ################################################################################################################################

    def execute(self, args, show_output=True):

        engine = self._get_engine(args)
        session = self._get_session(engine)

        Base.metadata.create_all(engine)

        if show_output:
            if self.verbose:
                self.logger.debug('ODB created successfully')
            else:
                self.logger.info('OK')

# ################################################################################################################################
# ################################################################################################################################
