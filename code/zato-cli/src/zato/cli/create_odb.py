# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli import ZatoCommand
from zato.common.odb.model import Base

# ################################################################################################################################
# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates the tables of the Zato ODB (Operational Database) in the Zato database
    """
    opts = [{
        'name':'--skip-if-exists',
        'help':'Return without raising an error if ODB already exists',
        'action':'store_true'
    }]

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

# ################################################################################################################################

    def execute(self, args, show_output=True):

        engine = self._get_engine()

        Base.metadata.create_all(engine)

        if show_output:
            if self.verbose:
                self.logger.debug('ODB created successfully')
            else:
                self.logger.info('OK')

# ################################################################################################################################
# ################################################################################################################################
