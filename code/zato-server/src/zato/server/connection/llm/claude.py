# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from zato.server.connection.llm.common import LLMClient, LLMError, Role_System

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist

# ################################################################################################################################
# ################################################################################################################################

# The Messages API requires this version header on every request
_anthropic_version = '2023-06-01'

# ################################################################################################################################
# ################################################################################################################################

class ClaudeClient(LLMClient):
    """ Talks to the Claude Messages API.
    """

# ################################################################################################################################

    def _get_headers(self) -> 'stranydict':

        out = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': _anthropic_version,
        }
        return out

# ################################################################################################################################

    def invoke(self, messages:'strdictlist') -> 'stranydict':
        """ Sends messages to the Messages API and maps the response to a plain dict.
        """

        # System messages cannot appear in the messages list - the API wants them as the top-level system field ..
        system_parts = []
        chat_messages = []

        for message in messages:
            if message['role'] == Role_System:
                system_parts.append(message['content'])
            else:
                chat_messages.append(message)

        # .. build the request - max_tokens is required by the API so it is always sent from the configuration ..
        url = self.address + '/v1/messages'
        headers = self._get_headers()
        request_body = {
            'model': self.model,
            'max_tokens': self.max_tokens,
            'messages': chat_messages,
        }

        if system_parts:
            request_body['system'] = '\n'.join(system_parts)

        # .. send it ..
        response = self.session.post(url, json=request_body, headers=headers, timeout=self.timeout)

        # .. anything other than an OK response is an error carrying the provider's body verbatim ..
        if response.status_code != OK:
            raise LLMError(f'Claude request to `{url}` failed with HTTP {response.status_code} ({self.name})', response.text)

        # .. the answer's text is spread across content blocks, only the textual ones carry it ..
        data = response.json()
        text_parts = []

        for block in data['content']:
            if block['type'] == 'text':
                text_parts.append(block['text'])

        text = ''.join(text_parts)

        # .. map the token usage ..
        usage = data['usage']

        out = {
            'text': text,
            'usage': {
                'input_tokens': usage['input_tokens'],
                'output_tokens': usage['output_tokens'],
            },
            'raw': data,
        }
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms the endpoint is reachable and the key is accepted by listing models.
        """
        url = self.address + '/v1/models'
        headers = self._get_headers()

        response = self.session.get(url, headers=headers, timeout=self.timeout)

        if response.status_code != OK:
            raise LLMError(f'Claude ping of `{url}` failed with HTTP {response.status_code} ({self.name})', response.text)

# ################################################################################################################################
# ################################################################################################################################
