# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util.api import ping_sap
from zato.common.const import SECRETS
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################


class SAPWrapper(Wrapper):
    """ Wraps a queue of connections to SAP RFC.
    """
    def __init__(self, config, server):

        # Imported here because not everyone will be using SAP
        import pyrfc
        self.pyrfc = pyrfc
        config.username = config.user  # Make Wrapper happy.
        if not hasattr(config, 'is_active'):  # On update passwd, we get AttributeError on is_active
            config.is_active = False

        config.auth_url = 'rfc://{user}@{host}:{sysnr}/{client}'.format(**config)
        super(SAPWrapper, self).__init__(config, 'SAP', server)
        self.logger.info('config: %r', config)

    def add_client(self):
        # Decrypt the password if it is encrypted.
        if self.config.password.startswith(SECRETS.PREFIX):
            self.config.password = self.server.decrypt(self.config.password)
        conn = self.pyrfc.Connection(user=self.config.user, passwd=self.config.password,
            ashost=self.config.host, sysnr=self.config.sysnr, client=self.config.client)

        try:
            ping_sap(conn)
        except Exception:
            self.logger.warning('Could not ping SAP (%s), e:`%s`', self.config.name, format_exc())

        self.client.put_client(conn)

# ################################################################################################################################
