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
from zato.common.odb.model import Base, ZatoInstallState

ODB_VERSION = "1.0"

class CreateODB(ZatoCommand):
    command_name = "create odb"

    opts = deepcopy(common_odb_opts)
    description = "Creates a Zato Operational Database (ODB)."

    def execute(self, args):
        engine = self._get_engine(args)
        session = self._get_session(engine)

        try:
            state = session.query(ZatoInstallState).filter_by(version=ODB_VERSION).all()
        except ProgrammingError, e:
            # Can be ignored, it simply means the table doesn't exist yet.
            session.rollback()
            state = False

        if state:
            # TODO: the 'drop_odb' below is incorrect..
            print(("\nODB {version} already exists, not creating it. " +
                  "(Use drop_odb first if you'd like to start afresh and "+
                  "recreate all ODB objects)").format(version=ODB_VERSION))
        else:
            Base.metadata.create_all(engine)
            state = ZatoInstallState(None, ODB_VERSION, datetime.now(), gethostname(), getuser())

            session.add(state)
            session.commit()

            print("\nSuccessfully created the ODB.")

def main():
    CreateODB().run()

if __name__ == "__main__":
    main()