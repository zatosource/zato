# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Python 2/3 compatibility
from six import PY2

# ################################################################################################################################
# ################################################################################################################################

"""
   Copyright 2006-2011 SpringSource (http://springsource.com), All Rights Reserved

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


# ################################################################################################################################
# ################################################################################################################################

# stdlib
import http.client as http_client
import socket
import ssl

class CAValidatingHTTPSConnection(http_client.HTTPConnection):
    """ This class allows communication via SSL/TLS and takes Certificate Authorities
    into account.
    """

    def __init__(self, host, port=None, ca_certs=None, keyfile=None, certfile=None,
                 cert_reqs=None, strict=None, ssl_version=None,
                 timeout=None):
        http_client.HTTPConnection.__init__(self, host, port, strict, timeout)

        self.ca_certs = ca_certs
        self.keyfile = keyfile
        self.certfile = certfile
        self.cert_reqs = cert_reqs
        self.ssl_version = ssl_version

    def connect(self):
        """ Connect to a host on a given (SSL/TLS) port.
        """
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = self.wrap_socket(sock)

    def wrap_socket(self, sock):
        """ Gets a socket object and wraps it into an SSL/TLS-aware one. May be
        overridden in subclasses if the wrapping process needs to be customized.
        """
        return ssl.wrap_socket(sock, self.keyfile, self.certfile,
                                    ca_certs=self.ca_certs, cert_reqs=self.cert_reqs,
                                    ssl_version=self.ssl_version)

class CAValidatingHTTPS(http_client.HTTPConnection):
    """ A subclass of http.client.HTTPConnection which is aware of Certificate Authorities
    used in SSL/TLS transactions.
    """
    _connection_class = CAValidatingHTTPSConnection

    def __init__(self, host=None, port=None, strict=None, ca_certs=None, keyfile=None, certfile=None,
                 cert_reqs=None, ssl_version=None, timeout=None):
        self._setup(self._connection_class(host, port, ca_certs, keyfile, certfile,
                                           cert_reqs, strict, ssl_version, timeout))

# ################################################################################################################################
# ################################################################################################################################

"""
   Copyright 2006-2011 SpringSource (http://springsource.com), All Rights Reserved

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
import sys
import traceback

if PY2:
    from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
    from xmlrpclib import ServerProxy, Transport
else:
    from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
    from xmlrpc.client import ServerProxy, Transport

class VerificationException(Exception):
    """ Raised when the verification of a certificate's fields fails.
    """

# ##############################################################################
# Server
# ##############################################################################

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/", "/RPC2",)

    def setup(self):
        self.connection = self.request # for doPOST
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

class SSLServer(SimpleXMLRPCServer):
    def __init__(self, host=None, port=None, keyfile=None, certfile=None,
                 ca_certs=None, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_TLSv1,
                 do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None,
                 log_requests=True, **kwargs):

        if PY2:
            SimpleXMLRPCServer.__init__(self, (host, port), requestHandler=RequestHandler)
        else:
            SimpleXMLRPCServer.__init__(self, (host, port))

        self.keyfile = keyfile
        self.certfile = certfile
        self.ca_certs = ca_certs
        self.cert_reqs = cert_reqs
        self.ssl_version = ssl_version
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs
        self.ciphers = ciphers

        # Looks awkward to use camelCase here but that's what SimpleXMLRPCRequestHandler
        # expects.
        self.logRequests = log_requests

        # 'verify_fields' is taken from kwargs to allow for adding more keywords
        # in future versions.
        self.verify_fields = kwargs.get("verify_fields")

    def get_request(self):
        """ Overridden from SocketServer.TCPServer.get_request, wraps the socket in
        an SSL context.
        """
        sock, from_addr = self.socket.accept()

        # 'ciphers' argument is new in 2.7 and we must support 2.6 so add it
        # to kwargs conditionally, depending on the Python version.

        kwargs = {"keyfile":self.keyfile, "certfile":self.certfile,
                    "server_side":True, "cert_reqs":self.cert_reqs, "ssl_version":self.ssl_version,
                    "ca_certs":self.ca_certs, "do_handshake_on_connect":self.do_handshake_on_connect,
                    "suppress_ragged_eofs":self.suppress_ragged_eofs}

        if sys.version_info >= (2, 7):
            kwargs["ciphers"] = self.ciphers

        sock  = ssl.wrap_socket(sock, **kwargs)

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("get_request cert='%s', from_addr='%s'" % (sock.getpeercert(), from_addr))

        return sock, from_addr

    def verify_request(self, sock, from_addr):
        """ Overridden from SocketServer.TCPServer.verify_request, adds validation of the
        other side's certificate fields.
        """
        try:
            if self.verify_fields:

                cert = sock.getpeercert()
                if not cert:
                    msg = "Couldn't verify fields, peer didn't send the certificate, from_addr='%s'" % (from_addr,)
                    raise VerificationException(msg)

                allow_peer, reason = self.verify_peer(cert, from_addr)
                if not allow_peer:
                    self.logger.error(reason)
                    sock.close()
                    return False

        except Exception:

            # It was either an error on our side or the client didn't send the
            # certificate even though self.cert_reqs was CERT_OPTIONAL (it couldn't
            # have been CERT_REQUIRED because we wouldn't have got so far, the
            # session would've been terminated much earlier in ssl.wrap_socket call).
            # Regardless of the reason we cannot accept the client in that case.

            msg = "Verification error='%s', cert='%s', from_addr='%s'" % (
                traceback.format_exc(), sock.getpeercert(), from_addr)
            self.logger.error(msg)

            sock.close()
            return False

        return True

    def verify_peer(self, cert, from_addr):
        """ Verifies the other side's certificate. May be overridden in subclasses
        if the verification process needs to be customized.
        """

        subject = cert.get("subject")
        if not subject:
            msg = "Peer certificate doesn't have the 'subject' field, cert='%s'" % cert
            raise VerificationException(msg)

        subject = dict(elem[0] for elem in subject)

        for verify_field in self.verify_fields:

            expected_value = self.verify_fields[verify_field]
            cert_value = subject.get(verify_field, None)

            if not cert_value:
                reason = "Peer didn't send the '%s' field, subject fields received '%s'" % (
                    verify_field, subject)
                return False, reason

            if expected_value != cert_value:
                reason = "Expected the subject field '%s' to have value '%s' instead of '%s', subject='%s'" % (
                    verify_field, expected_value, cert_value, subject)
                return False, reason

        return True, None

    def register_functions(self):
        raise NotImplementedError("Must be overridden by subclasses")

# ##############################################################################
# Client
# ##############################################################################

class SSLClientTransport(Transport):
    """ Handles an HTTPS transaction to an XML-RPC server.
    """

    user_agent = "SSL XML-RPC Client (by http://springpython.webfactional.com)"

    def __init__(self, ca_certs=None, keyfile=None, certfile=None, cert_reqs=None,
                 ssl_version=None, timeout=None, strict=None):

        self.ca_certs = ca_certs
        self.keyfile = keyfile
        self.certfile = certfile
        self.cert_reqs = cert_reqs
        self.ssl_version = ssl_version
        self.timeout = timeout
        self.strict = strict

        Transport.__init__(self)

    def make_connection(self, host):
        return CAValidatingHTTPS(host, strict=self.strict, ca_certs=self.ca_certs,
                keyfile=self.keyfile, certfile=self.certfile, cert_reqs=self.cert_reqs,
                ssl_version=self.ssl_version, timeout=self.timeout)

class SSLClient(ServerProxy):
    def __init__(self, uri=None, ca_certs=None, keyfile=None, certfile=None,
                 cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1,
                 transport=None, encoding=None, verbose=0, allow_none=0, use_datetime=0,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT, strict=None):

        if not transport:
            _transport=SSLClientTransport(ca_certs, keyfile, certfile, cert_reqs,
                                         ssl_version, timeout, strict)
        else:
            _transport=transport(ca_certs, keyfile, certfile, cert_reqs, ssl_version, timeout, strict)

        ServerProxy.__init__(self, uri, _transport, encoding, verbose, allow_none, use_datetime)
        self.logger = logging.getLogger(self.__class__.__name__)

# ################################################################################################################################
# ################################################################################################################################
