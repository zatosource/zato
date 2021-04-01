# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from tempfile import gettempdir
from threading import Thread

# pyftpdlib
from pyftpdlib.authorizers import DummyAuthorizer as _DummyAuthorizer
from pyftpdlib.handlers import FTPHandler as _FTPHandler
from pyftpdlib.servers import FTPServer as _ImplFTPServer

# ################################################################################################################################
# ################################################################################################################################

class config:
    port      = 11021
    username  = '111'
    password  = '222'
    directory = gettempdir()

# ################################################################################################################################
# ################################################################################################################################

def create_ftp_server():
    # type: () -> _ImplFTPServer
    authorizer = _DummyAuthorizer()
    authorizer.add_user(config.username, config.password, config.directory, 'elradfmwMT')

    handler = _FTPHandler
    handler.authorizer = authorizer
    handler.banner = 'Welcome to Zato'
    handler.log_prefix = '[%(username)s]@%(remote_ip)s'

    address = ('', config.port)
    server = _ImplFTPServer(address, handler)

    server.max_cons = 10
    server.max_cons_per_ip = 10

    return server

# ################################################################################################################################
# ################################################################################################################################

class FTPServer(Thread):
    def __init__(self):
        self.impl = create_ftp_server()
        Thread.__init__(self, target=self.impl.serve_forever)
        self.setDaemon(True)

    def stop(self):
        self.impl.close_all()

# ################################################################################################################################
# ################################################################################################################################
