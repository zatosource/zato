# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.cli import ZatoCommand, common_odb_opts

class Delete(ZatoCommand):
    """ Deletes Zato components
    """
    needs_password_confirm = False
    opts = common_odb_opts

    def execute(self, args):

        # Zato
        from zato.common.odb import drop_all

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
