# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from zato.server.connection.llm.common import LLMClient, LLMError, Role_System, Role_User

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist

# ################################################################################################################################
# ################################################################################################################################

class GeminiClient(LLMClient):
    """ Talks to the Gemini generateContent API.
    """

# ################################################################################################################################

    def _get_headers(self) -> 'stranydict':

        out = {
            'Content-Type': 'application/json',
            'x-goog-api-key': self.api_key,
        }
        return out

# ################################################################################################################################

    def invoke(self, messages:'strdictlist') -> 'stranydict':
        """ Sends messages to the generateContent endpoint and maps the response to a plain dict.
        """

        # The API wants system messages as the top-level systemInstruction and everything else
        # as contents entries whose roles are user or model, each with a parts list ..
        system_parts = []
        contents = []

        for message in messages:

            if message['role'] == Role_System:
                system_parts.append(message['content'])
                continue

            if message['role'] == Role_User:
                role = 'user'
            else:
                role = 'model'

            contents.append({
                'role': role,
                'parts': [{'text': message['content']}],
            })

        # .. build the request ..
        url = f'{self.address}/models/{self.model}:generateContent'
        headers = self._get_headers()
        request_body:'stranydict' = {
            'contents': contents,
        }

        if system_parts:
            request_body['systemInstruction'] = {
                'parts': [{'text': '\n'.join(system_parts)}],
            }

        # .. send it ..
        response = self.session.post(url, json=request_body, headers=headers, timeout=self.timeout)

        # .. anything other than an OK response is an error carrying the provider's body verbatim ..
        if response.status_code != OK:
            raise LLMError(f'Gemini request to `{url}` failed with HTTP {response.status_code} ({self.name})', response.text)

        data = response.json()

        # .. a blocked prompt arrives as an in-band error inside an OK response - it must raise, never pass as success ..
        if prompt_feedback := data.get('promptFeedback'):
            if block_reason := prompt_feedback.get('blockReason'):
                raise LLMError(f'Gemini blocked the prompt with reason `{block_reason}` ({self.name})', response.text)

        # .. no candidates in an OK response is an in-band error too ..
        candidates = data.get('candidates')
        if not candidates:
            raise LLMError(f'Gemini returned no candidates ({self.name})', response.text)

        # .. the answer's text is spread across the first candidate's parts ..
        first_candidate = candidates[0]
        candidate_content = first_candidate['content']
        text_parts = []

        for part in candidate_content['parts']:
            if 'text' in part:
                text_parts.append(part['text'])

        text = ''.join(text_parts)

        # .. map the token usage ..
        usage = data['usageMetadata']

        out = {
            'text': text,
            'usage': {
                'input_tokens': usage['promptTokenCount'],
                'output_tokens': usage['candidatesTokenCount'],
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
            raise LLMError(f'Gemini ping of `{url}` failed with HTTP {response.status_code} ({self.name})', response.text)

# ################################################################################################################################
# ################################################################################################################################
