# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime

# Zato
from zato.common.odb.model import KVData
from zato.server.service import Service

# ################################################################################################################################

class AutoCleanUp(Service):
    """ Cleans up expired keys in ODB (KVDB expires them up automatically so it's not needed here).
    """
    def handle(self):
        with closing(self.odb.session()) as session:
            len_deleted = session.query(KVData).\
                filter(KVData.expiry_time <= datetime.utcnow()).\
                delete()
            session.commit()

            if len_deleted:
                suffix = 's' if len_deleted > 1 else ''
                self.logger.info('Deleted %i expired KV key%s from ODB', len_deleted, suffix)

# ################################################################################################################################
