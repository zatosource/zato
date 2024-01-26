# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from uuid import uuid4

# Zato
from zato.common.api import ADAPTER_PARAMS, HTTPException
from zato.common.json_internal import dumps, loads
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
    force_in_qs = []
    apply_params = ADAPTER_PARAMS.APPLY_AFTER_REQUEST
    raise_error_on = ['4', '5'] # Any HTTP code starting with these prefixes will mean an exception

    def get_call_params(self):
        call_params = {'params':{}}
        dyn_params = {}

        for name in self.force_in_qs:
            call_params['params'][name] = self.environ['zato.request_payload'].pop(name, '')

        if self.apply_params == ADAPTER_PARAMS.APPLY_AFTER_REQUEST:
            dyn_params.update(self.environ['zato.request_payload'])
            dyn_params.update(self.params)
        else:
            dyn_params.update(self.params)
            dyn_params.update(self.environ['zato.request_payload'])

        if self.params_to_qs:
            call_params['params'].update(dyn_params)
        else:
            call_params['data'] = dumps(dyn_params)

        return call_params

    def handle(self):
        self.logger.debug(
            '`%s` invoked with `%r` and `%r`, `%r`, `%r`, `%r`, `%r`, `%r`', self.name, self.request.payload,
            self.outconn, self.method, self.params_to_qs, self.load_response, self.params, self.apply_params)

        # Only return what was received
        if self.request.payload:
            if isinstance(self.request.payload, dict):
                if self.request.payload.get('echo', False):
                    self.response.payload = self.request.payload
                    return

        # It is possible that we are being invoked from self.patterns.invoke_retry and at the same
        # time our self.force_in_qs is not empty. In such a case we want to operate on a deep copy
        # of our request. The reason is that if self.force_in_qs is not empty then self.get_call_params
        # will modify the request in place. If the call to the external resource fails and invoke_retry
        # attempts to invoke us again, the already modified request will not have parameters removed
        # during the initial self.get_call_params call and this will likely result in an exception.
        # But since this applies to cases with non-empty self.force_in_qs, we do not create
        # such a deep copy each time so as not to introduce additional overhead.
        if self.force_in_qs:
            self.environ['zato.request_payload'] = deepcopy(self.request.payload)
        else:
            self.environ['zato.request_payload'] = self.request.payload

        # Parameters to invoke the remote resource with
        call_params = self.get_call_params()

        # Build a request but don't actually call it
        if call_params.pop('dry-run', False):
            self.response.payload = call_params
            return

        conn = self.outgoing.plain_http[self.outconn].conn
        func = getattr(conn, self.method.lower())

        response = func(self.cid, **call_params)

        for item in self.raise_error_on:
            if str(response.status_code).startswith(item):
                raise HTTPException(self.cid, response.text, response.status_code)

        if self.load_response:
            try:
                self.response.payload = loads(response.text)
            except ValueError:
                self.logger.error('Cannot load JSON response `%s` for request `%s` to `%s`',
                    response.text, call_params, self.outconn)
                raise
        else:
            self.response.payload = response.text

# ################################################################################################################################
