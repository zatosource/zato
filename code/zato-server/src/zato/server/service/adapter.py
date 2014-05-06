# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import loads
from uuid import uuid4

# Zato
from zato.server.service import Service

# ################################################################################################################################

class JSONAdapter(Service):
    """ Invokes HTTP resources with JSON or query strings. In echo mode, returns request into response. In dry-run mode,
    returns in response the request that would have been sent to an external resource.
    """
    outconn = 'not-configured-{}'.format(uuid4().hex)
    method = 'not-configured-{}'.format(uuid4().hex)
    params_to_qs = False
    load_response = True

    def handle(self):
        if self.request.payload.pop('echo', False):
            self.response.payload = self.request.payload

        elif self.request.payload.pop('dry-run', False):
            self.response.payload = self.request.payload

        else:
            conn = self.outgoing.plain_http[self.outconn].conn
            func = getattr(conn, self.method.lower())

            if self.params_to_qs:
                func_params = {'params': self.request.payload}
            else:
                func_params = {'data': self.request.payload}

            response = func(self.cid, **func_params)

            if self.load_response:
                try:
                    self.response.payload = loads(response.text)
                except ValueError, e:
                    self.logger.error('Cannot load JSON response `%s` for request `%s` to `%s`', 
                        response.text, self.request.payload, self.outconn)
                    raise
            else:
                self.response.payload = response.text

# ################################################################################################################################
