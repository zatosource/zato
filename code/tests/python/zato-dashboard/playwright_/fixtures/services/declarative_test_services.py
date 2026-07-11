# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# Callbacks configured by the declarative invocation tests deliver here and every delivery
# is appended to this file - tests identify their own deliveries by unique markers in the data.
Callback_Store_Path = '/tmp/zato-test-declarative-callback.jsonl'

# ################################################################################################################################
# ################################################################################################################################

class DeclarativeCallbackStore(Service):
    """ A callback target for declarative invocation tests - appends every payload it receives
    to a well-known file that tests read back.
    """

    name = 'test.declarative.callback-store'

    def handle(self):

        data = self.request.payload

        with open(Callback_Store_Path, 'a') as callback_file:
            _ = callback_file.write(dumps(data) + '\n')

        self.logger.info('Callback store received: %s', data)

# ################################################################################################################################
# ################################################################################################################################

class InvokeRESTDeclarativeForTests(Service):
    """ Invokes an outgoing REST connection through its declarative profile on behalf of the
    declarative invocation tests - either self.rest[name].invoke(), optionally with request data,
    or an explicit self.rest[name].post(data) that merges with the profile.
    """

    name = 'test.rest.outconn.declarative-invoke'

    def handle(self):

        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        mode = request['mode']

        # A readiness probe sent while the test waits for this service to deploy ..
        if mode == 'ping':
            out = {'is_ready': True}

        # .. otherwise, run the connection through its declarative profile and report what came back.
        # Errors turn into a field in the reply rather than a 500 - the tests retry
        # while browser-made configuration propagates to the server.
        else:
            try:
                outconn_name = request['outconn_name']
                invoker = self.rest[outconn_name]

                # Tests may pass explicit request data for the connection to send
                if 'data' in request:
                    data = request['data']
                else:
                    data = ''

                # An explicit .post() merges with the declarative profile - the explicit
                # method and body win - while .invoke() runs the profile itself.
                if mode == 'post':
                    response = invoker.post(data)
                else:
                    response = invoker.invoke(data)

                out = {
                    'status_code': response.status_code,
                    'text': response.text,
                }
            except Exception as invoke_error:
                out = {'error': repr(invoke_error)}

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################
