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

API_URL = 'https://api.anthropic.com/v1/messages'
API_Version = '2023-06-01'

# ################################################################################################################################
# ################################################################################################################################

class AnthropicClient(BaseLLMClient):
    """ Client for Anthropic Claude API.
    """

    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses from Anthropic.
        """
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': API_Version,
        }

        body = {
            'model': model,
            'max_tokens': 4096,
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

                    event_type = data.get('type', '')

                    if event_type == 'content_block_delta':
                        delta = data.get('delta', {})
                        text = delta.get('text', '')
                        if text:
                            yield self._format_chunk(text)

                    elif event_type == 'message_stop':
                        yield self._format_done()
                        return

                    elif event_type == 'error':
                        error_data = data.get('error', {})
                        error_msg = error_data.get('message', 'Unknown error')
                        yield self._format_error(error_msg)
                        return

        except Exception as e:
            logger.warning('Anthropic API error: %s', e)
            yield self._format_error(e)

# ################################################################################################################################
# ################################################################################################################################
