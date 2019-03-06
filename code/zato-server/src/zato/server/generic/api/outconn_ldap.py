# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util import spawn_greenlet
from zato.server.connection.queue import Wrapper

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class LDAPClient(object):
    """ A client through which outgoing LDAP messages can be sent.
    """
    def __init__(self, config):
        self.config = config
        self.is_connected = True
        spawn_greenlet(self._init, timeout=2)

    def _init(self):

        return

        _impl_class = ZatoWSXClient if self.config.is_zato else _NonZatoWSXClient
        self.impl = _impl_class(self.config, self.on_connected_cb, self.on_message_cb, self.on_close_cb, self.config.address)

        self.send = self.impl.send
        if _impl_class is ZatoWSXClient:
            self.invoke = self.send

        self.impl.connect()
        self.impl.run_forever()

    def delete(self):
        #self.impl.close()
        pass

# ################################################################################################################################

class OutconnLDAPWrapper(Wrapper):
    """ Wraps a queue of connections to LDAP.
    """
    def __init__(self, config, server):
        config.parent = self
        super(OutconnLDAPWrapper, self).__init__(config, 'outgoing LDAP', server)

# ################################################################################################################################

    def add_client(self):
        try:
            conn = LDAPClient(self.config)
        except Exception:
            logger.warn('LDAP client could not be built `%s`', format_exc())
        else:
            self.client.put_client(conn)

# ################################################################################################################################
