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

API_URL = 'https://api.openai.com/v1/chat/completions'

# ################################################################################################################################
# ################################################################################################################################

class OpenAIClient(BaseLLMClient):
    """ Client for OpenAI GPT API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from OpenAI.
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        body = {
            'model': model,
            'stream': True,
            'messages': messages,
        }

        body_bytes = json.dumps(body).encode('utf-8')

        request = Request(API_URL, data=body_bytes, headers=headers, method='POST')

        try:
            with urlopen(request) as response:
                for line in response:
                    line = line.decode('utf-8').strip()

                    if not line:
                        continue

                    if not line.startswith('data: '):
                        continue

                    data_str = line[6:]

                    if data_str == '[DONE]':
                        yield self._format_done()
                        return

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = data.get('choices', [])
                    if not choices:
                        continue

                    delta = choices[0].get('delta', {})
                    content = delta.get('content', '')

                    if content:
                        yield self._format_chunk(content)

                    finish_reason = choices[0].get('finish_reason')
                    if finish_reason == 'stop':
                        yield self._format_done()
                        return

        except Exception as e:
            logger.warning('OpenAI API error: %s', e)
            yield self._format_error(e)

# ################################################################################################################################
# ################################################################################################################################
