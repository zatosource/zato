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
from zato.common import ADAPTER_PARAMS
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
    params = {}
    apply_params = ADAPTER_PARAMS.APPLY_AFTER_REQUEST

    def handle(self):
        self.logger.debug(
            '`%s` invoked with `%r` and `%r`, `%r`, `%r`, `%r`, `%r`, `%r`', self.name, self.request.payload,
            self.outconn, self.method, self.params_to_qs, self.load_response, self.params, self.apply_params)

        if self.request.payload.pop('echo', False):
            self.response.payload = self.request.payload

        elif self.request.payload.pop('dry-run', False):
            self.response.payload = self.request.payload

        else:
            conn = self.outgoing.plain_http[self.outconn].conn
            func = getattr(conn, self.method.lower())

            params = {}

            if self.apply_params == ADAPTER_PARAMS.APPLY_AFTER_REQUEST:
                params.update(self.request.payload)
                params.update(self.params)
            else:
                params.update(self.params)
                params.update(self.request.payload)

            if self.params_to_qs:
                func_params = {'params': params}
            else:
                func_params = {'data': params}

            response = func(self.cid, **func_params)

            if self.load_response:
                try:
                    self.response.payload = loads(response.text)
                except ValueError, e:
                    self.logger.error('Cannot load JSON response `%s` for request `%s` to `%s`', 
                        response.text, func_params, self.outconn)
                    raise
            else:
                self.response.payload = response.text

# ################################################################################################################################
