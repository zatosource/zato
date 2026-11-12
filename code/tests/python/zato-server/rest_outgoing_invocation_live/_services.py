# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class RESTOutgoingLiveInvoke(Service):
    """ Invokes a named outgoing REST connection with the method, the body and the query string of its request
    and reports what came back, including any error raised on the way, so that a test can assert on the invocation
    without reading server logs.
    """
    name = 'test.rest.outgoing.live.invoke'

    def handle(self) -> 'None':

        request = self.request.raw_request

        conn_name = request['conn_name']
        method = request['method']
        data = request['data']
        params = request['params']

        conn = self.out.rest[conn_name].conn

        try:
            if method == 'get':
                response = conn.get(self.cid, params)
            else:
                func = getattr(conn, method)
                response = func(self.cid, data, params)

        except Exception as e:
            self.response.payload = {
                'cid': self.cid,
                'status_code': 0,
                'data': None,
                'text': '',
                'error': str(e),
            }

        else:
            self.response.payload = {
                'cid': self.cid,
                'status_code': response.status_code,
                'data': response.data,
                'text': response.text,
                'error': '',
            }

# ################################################################################################################################
# ################################################################################################################################
