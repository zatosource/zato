# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from tempfile import NamedTemporaryFile
from traceback import format_exc

# Bunch
from bunch import bunchify

# sh
from sh import Command, ErrorReturnCode

# Zato
from zato.common import SFTP
from zato.common.sftp import SFTPOutput
from zato.common.util.json_ import dumps
from zato.server.connection.connector.subprocess_.base import BaseConnectionContainer, Response

# ################################################################################################################################
# ################################################################################################################################

class FTPConnection(object):
    """ Wraps access to SFTP commands via command line.
    """

# ################################################################################################################################
# ################################################################################################################################

class FTPConnectionContainer(BaseConnectionContainer):

    connection_class = FTPConnection
    ipc_name = conn_type = logging_file_name = 'ftp'

    remove_id_from_def_msg = False
    remove_name_from_def_msg = False

# ################################################################################################################################

    def _on_CHANNEL_FTP_PING(self, msg):
        return super(FTPConnectionContainer, self).on_definition_ping(msg)

# ################################################################################################################################

    def _on_CHANNEL_FTP_DELETE(self, msg):
        return super(FTPConnectionContainer, self).on_definition_delete(msg)

    _on_GENERIC_CONNECTION_DELETE = _on_CHANNEL_FTP_DELETE

# ################################################################################################################################

    def _on_CHANNEL_FTP_CREATE(self, msg):
        return super(FTPConnectionContainer, self).on_definition_create(msg)

    _on_GENERIC_CONNECTION_CREATE = _on_CHANNEL_FTP_CREATE

# ################################################################################################################################

    def _on_CHANNEL_FTP_EDIT(self, msg):
        return super(FTPConnectionContainer, self).on_definition_edit(msg)

    _on_GENERIC_CONNECTION_EDIT = _on_CHANNEL_FTP_EDIT

# ################################################################################################################################

    def _on_CHANNEL_FTP_CHANGE_PASSWORD(self, msg):
        return super(FTPConnectionContainer, self).on_definition_change_password(msg)

    _on_GENERIC_CONNECTION_CHANGE_PASSWORD = _on_CHANNEL_FTP_CHANGE_PASSWORD

# ################################################################################################################################

    def _on_CHANNEL_FTP_EXECUTE(self, msg, is_reconnect=False, _utcnow=datetime.utcnow):
        zzz

# ################################################################################################################################

if __name__ == '__main__':

    container = FTPConnectionContainer()
    container.run()

# ################################################################################################################################
