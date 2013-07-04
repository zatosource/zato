# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from getpass import getuser
from socket import gethostname

# Zato
from zato.cli import ZatoCommand, common_odb_opts
from zato.common.odb import VERSION
from zato.common.odb.model import Base, ZatoInstallState

class Create(ZatoCommand):
    """ Creates a new Zato ODB (Operational Database)
    """
    opts = common_odb_opts

    def execute(self, args, show_output=True):
        engine = self._get_engine(args)
        session = self._get_session(engine)
        
        if engine.dialect.has_table(engine.connect(), 'install_state'):
            if show_output:
                version = session.query(ZatoInstallState.version).one().version
                msg = (
                    'The ODB (v. {}) already exists, not creating it. ' +
                    "Use the 'zato delete odb' command first if you'd like to start afresh and " +
                    'recreate all ODB objects.').format(version)
                self.logger.error(msg)
            
            return self.SYS_ERROR.ODB_EXISTS

        else:
            Base.metadata.create_all(engine)
            state = ZatoInstallState(None, VERSION, datetime.now(), gethostname(), getuser())

            session.add(state)
            session.commit()

            if show_output:
                if self.verbose:
                    self.logger.debug('Successfully created the ODB')
                else:
                    self.logger.info('OK')
