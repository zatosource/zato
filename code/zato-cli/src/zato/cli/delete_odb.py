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

# Zato
from zato.cli import ZatoCommand, common_odb_opts
from zato.common.odb import drop_all

class Delete(ZatoCommand):
    """ Deletes Zato components
    """
    needs_password_confirm = False
    opts = common_odb_opts

    def execute(self, args):
        engine = self._get_engine(args)
        
        if engine.dialect.has_table(engine.connect(), 'install_state'):
            drop_all(engine)
            
            if self.verbose:
                self.logger.debug('Successfully deleted the ODB')
            else:
                self.logger.info('OK')
        else:
            self.logger.error('No ODB found')
            return self.SYS_ERROR.NO_ODB_FOUND
