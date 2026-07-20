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

class InvokeLLMOutconnForTests(Service):
    """ Invokes an outgoing LLM connection on behalf of outgoing LLM connection tests.
    """

    name = 'test.llm.outconn.invoke'

    def handle(self):

        # The IDE invoker delivers the payload as a raw JSON string.
        request = self.request.payload
        if isinstance(request, str):
            request = loads(request)

        mode = request['mode']

        # A readiness probe sent while the test waits for this service to deploy ..
        if mode == 'ping':
            out = {'is_ready': True}

        # .. otherwise, call the outgoing connection and report what came back.
        # Errors turn into a field in the reply rather than a 500 - the tests retry
        # while browser-made configuration propagates to the server and these
        # transient failures must not litter the server log with tracebacks.
        else:
            try:
                out = self._invoke_outconn(request)
            except Exception as invoke_error:
                out = {'error': repr(invoke_error)}

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################

    def _invoke_outconn(self, request):

        outconn_name = request['outconn_name']
        text = request['text']
        chat_id = request['chat_id']

        conn = self.llm[outconn_name]

        # A chat id makes it a multi-turn chat call, otherwise it is a one-shot invoke.
        if chat_id:
            response = conn.chat(text, chat_id)
        else:
            response = conn.invoke(text)

        out = {
            'text': response['text'],
            'usage': response['usage'],
        }
        return out

# ################################################################################################################################
# ################################################################################################################################
