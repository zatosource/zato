# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
   Copyright 2006-2008 SpringSource (http://springsource.com), All Rights Reserved

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# stdlib
import logging
from logging import DEBUG
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_ACCEPTABLE, OK, responses, SERVICE_UNAVAILABLE
from time import sleep
from traceback import format_exc

# Python 2/3 compatibility
from zato.common.py23_ import start_new_thread

# Zato
from zato.common.util.json_ import dumps
from zato.server.connection.jms_wmq.jms import WebSphereMQException, NoMessageAvailableException
from zato.server.connection.jms_wmq.jms.connection import WebSphereMQConnection
from zato.server.connection.jms_wmq.jms.core import TextMessage
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnection(object):

    def __init__(self, logger, **config):
        self.logger = logger
        self.config = config # type: dict

    def connect(self):
        pass # This is a no-op added for API completeness

    def ping(self):
        self.logger.warn('QQQ %s', self.config)

# ################################################################################################################################
# ################################################################################################################################

class SFTPConnectionContainer(BaseConnectionContainer):

    connection_class = SFTPConnection
    ipc_name = conn_type = logging_file_name = 'sftp'

# ################################################################################################################################

    def _on_OUTGOING_SFTP_PING(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_ping(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_DELETE(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_delete(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_CREATE(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_create(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_EDIT(self, msg):
        return super(SFTPConnectionContainer, self).on_definition_edit(msg)

# ################################################################################################################################

    def _on_OUTGOING_SFTP_SEND(self, msg, is_reconnect=False):
        pass

# ################################################################################################################################

if __name__ == '__main__':

    container = SFTPConnectionContainer()
    container.run()

# ################################################################################################################################

