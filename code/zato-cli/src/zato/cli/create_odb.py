# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime
from getpass import getuser
from socket import gethostname

# SQLAlchemy
from sqlalchemy.exc import ProgrammingError

# Zato
from zato.cli import ZatoCommand, common_odb_opts
from zato.common.odb import VERSION
from zato.common.odb.model import Base, ZatoInstallState

class Create(ZatoCommand):
    opts = deepcopy(common_odb_opts)

    def execute(self, args):
        engine = self._get_engine(args)
        session = self._get_session(engine)
        
        if engine.dialect.has_table(engine.connect(), 'install_state'):
            version = session.query(ZatoInstallState.version).one().version
            msg = ('The ODB (v. {}) already exists, not creating it. ' +
                  "Use the 'zato delete odb' command first if you'd like to start afresh and "+
                  'recreate all ODB objects.').format(version)
            self.logger.error(msg)
            
            return self.SYS_ERROR.ODB_EXISTS

        else:
            Base.metadata.create_all(engine)
            state = ZatoInstallState(None, VERSION, datetime.now(), gethostname(), getuser())

            session.add(state)
            session.commit()

            if self.verbose:
                self.logger.debug('Successfully created the ODB')
            else:
                self.logger.info('OK')
