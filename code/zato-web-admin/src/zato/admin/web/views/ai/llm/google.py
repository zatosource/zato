# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger
from urllib.request import Request, urlopen

# Zato
from zato.admin.web.views.ai.llm.base import BaseLLMClient

if 0:
    from zato.common.typing_ import generator_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

API_URL_Template = 'https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={api_key}'

# ################################################################################################################################
# ################################################################################################################################

class GoogleClient(BaseLLMClient):
    """ Client for Google Gemini API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from Google Gemini.
        """
        url = API_URL_Template.format(model=model, api_key=self.api_key)

        headers = {
            'Content-Type': 'application/json',
        }

        # Convert messages to Gemini format
        contents = self._convert_messages(messages)

        body = {
            'contents': contents,
        }

        body_bytes = json.dumps(body).encode('utf-8')

        request = Request(url, data=body_bytes, headers=headers, method='POST')

        try:
            with urlopen(request) as response:
                for line in response:
                    line = line.decode('utf-8').strip()

                    if not line:
                        continue

                    if not line.startswith('data: '):
                        continue

                    data_str = line[6:]

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    candidates = data.get('candidates', [])
                    if not candidates:
                        continue

                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])

                    for part in parts:
                        text = part.get('text', '')
                        if text:
                            yield self._format_chunk(text)

                    finish_reason = candidates[0].get('finishReason')
                    if finish_reason == 'STOP':
                        yield self._format_done()
                        return

        except Exception as e:
            logger.warning('Google Gemini API error: %s', e)
            yield self._format_error(e)

# ################################################################################################################################

    def _convert_messages(self, messages:'list') -> 'list':
        """ Converts OpenAI-style messages to Gemini format.
        """
        out = []

        for msg in messages:
            role = msg.get('role', 'user')

            # Gemini uses 'user' and 'model' roles
            if role == 'assistant':
                role = 'model'

            content = msg.get('content', '')

            out.append({
                'role': role,
                'parts': [{'text': content}]
            })

        return out

# ################################################################################################################################
# ################################################################################################################################
