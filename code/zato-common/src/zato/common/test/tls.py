# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import socket, ssl
from tempfile import NamedTemporaryFile
from threading import Thread
from time import sleep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Zato
from zato.common.test.tls_material import ca_cert, server1_cert, server1_key

TLS_PORT = 37443

class _TLSServer(HTTPServer):
    def __init__(self, cert_reqs, ca_cert):
        HTTPServer.__init__(self, ('0.0.0.0', TLS_PORT), BaseHTTPRequestHandler)
        self.cert_reqs = cert_reqs
        self.ca_cert=None

    def server_bind(self):

        with NamedTemporaryFile(prefix='zato-tls', delete=False) as server1_key_tf:
            server1_key_tf.write(server1_key)
            server1_key_tf.flush()

            with NamedTemporaryFile(prefix='zato-tls', delete=False) as server1_cert_tf:
                server1_cert_tf.write(server1_cert)
                server1_cert_tf.flush()

                with NamedTemporaryFile(prefix='zato-tls', delete=False) as ca_cert_tf:
                    ca_cert_tf.write(ca_cert)
                    ca_cert_tf.flush()

                    self.socket = ssl.wrap_socket(
                        self.socket, server1_key_tf.name, server1_cert_tf.name, True, ca_certs=ca_cert_tf.name)

                    if self.allow_reuse_address:
                        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.socket.bind(self.server_address)
                    self.server_address = self.socket.getsockname()

class TLSServer(Thread):
    def __init__(self, cert_reqs=ssl.CERT_NONE, ca_cert=None):
        Thread.__init__(self)
        self.setDaemon(True)

        self.server = None
        self.cert_reqs = cert_reqs
        self.ca_cert=None

    def run(self):
        self.server = _TLSServer(self.cert_reqs, self.ca_cert)
        self.server.serve_forever()
