# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.soap.message import SOAPMessage
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# What the service returns once the connection was invoked
_result_invoked = 'outconn-tls-invoked'

# What an error that the invocation raised begins with
_result_error_prefix = 'outconn-tls-error: '

# The operation that SOAP connections invoke - the test endpoint answers any operation
_soap_operation = 'checkStatus'

# ################################################################################################################################
# ################################################################################################################################

class OutconnTLSCheck(Service):
    """ Invokes one outgoing REST or SOAP connection and reports whether the invocation succeeded.
    """
    name = 'test.outconn-tls.local-docker.check'

    # I/O definition
    input = 'conn_type', 'conn_name'
    output = 'result'

    def handle(self):

        conn_type = self.request.input.conn_type
        conn_name = self.request.input.conn_name

        # Errors are returned rather than raised, because the caller retries while
        # the connections that were just imported are still being configured.
        try:
            if conn_type == 'rest':
                _ = self.rest[conn_name].get()
            else:
                _ = self.soap[conn_name].invoke(_soap_operation, SOAPMessage())

        except Exception:
            self.response.payload.result = _result_error_prefix + format_exc()

        else:
            self.response.payload.result = _result_invoked

# ################################################################################################################################
# ################################################################################################################################
