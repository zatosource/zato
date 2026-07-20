# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from zato.server.connection.llm.common import LLMClient, LLMError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist

# ################################################################################################################################
# ################################################################################################################################

class OpenAIClient(LLMClient):
    """ Talks to OpenAI-compatible chat completion endpoints - this covers OpenAI itself, Azure-style deployments
    and self-hosted servers such as Ollama, vLLM or LiteLLM, which only differ in the address and the key.
    """

# ################################################################################################################################

    def _get_headers(self) -> 'stranydict':

        headers = {'Content-Type': 'application/json'}

        # The key is optional because self-hosted endpoints may not require one
        if self.api_key:
            headers['Authorization'] = 'Bearer ' + self.api_key

        return headers

# ################################################################################################################################

    def invoke(self, messages:'strdictlist') -> 'stranydict':
        """ Sends messages to the chat completions endpoint and maps the response to a plain dict.
        """

        # Build the request ..
        url = self.address + '/chat/completions'
        headers = self._get_headers()
        request_body = {
            'model': self.model,
            'messages': messages,
        }

        # .. send it ..
        response = self.session.post(url, json=request_body, headers=headers, timeout=self.timeout)

        # .. anything other than an OK response is an error carrying the provider's body verbatim ..
        if response.status_code != OK:
            raise LLMError(f'OpenAI request to `{url}` failed with HTTP {response.status_code} ({self.name})', response.text)

        # .. extract the answer's text ..
        data = response.json()
        choices = data['choices']
        first_choice = choices[0]
        message = first_choice['message']
        text = message['content']

        # .. map the token usage ..
        usage = data['usage']

        out = {
            'text': text,
            'usage': {
                'input_tokens': usage['prompt_tokens'],
                'output_tokens': usage['completion_tokens'],
            },
            'raw': data,
        }
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Confirms the endpoint is reachable and the key is accepted by listing models.
        """
        url = self.address + '/models'
        headers = self._get_headers()

        response = self.session.get(url, headers=headers, timeout=self.timeout)

        if response.status_code != OK:
            raise LLMError(f'OpenAI ping of `{url}` failed with HTTP {response.status_code} ({self.name})', response.text)

# ################################################################################################################################
# ################################################################################################################################
