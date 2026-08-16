# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The outgoing LLM connection this service invokes
_outconn_name = 'test.llm.local-docker'

# ################################################################################################################################
# ################################################################################################################################

class LLMCheck(Service):
    """ Sends the incoming text to the outgoing LLM connection and returns the model's reply.
    """
    name = 'test.llm.local-docker.check'

    # I/O definition
    input = 'text'
    output = 'reply'

    def handle(self):

        response = self.llm[_outconn_name].invoke(self.request.input.text)
        self.response.payload.reply = response['text']

# ################################################################################################################################
# ################################################################################################################################
