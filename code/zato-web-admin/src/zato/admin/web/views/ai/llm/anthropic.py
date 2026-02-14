# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from logging import getLogger
from traceback import format_exc
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

        body_json = json.dumps(body)
        body_bytes = body_json.encode('utf-8')

        logger.info('Anthropic request: model=%s messages=%s', model, json.dumps(messages, indent=2))

        request = Request(API_URL, data=body_bytes, headers=headers, method='POST')

        input_tokens = 0
        output_tokens = 0

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

                    logger.info('Anthropic event: %s data=%s', event_type, data_str)

                    if event_type == 'message_start':
                        message = data.get('message', {})
                        usage = message.get('usage', {})
                        input_tokens = usage.get('input_tokens', 0)
                        logger.info('Anthropic input_tokens: %d', input_tokens)

                    elif event_type == 'message_delta':
                        usage = data.get('usage', {})
                        output_tokens = usage.get('output_tokens', 0)
                        logger.info('Anthropic output_tokens: %d', output_tokens)

                    elif event_type == 'content_block_delta':
                        delta = data.get('delta', {})
                        text = delta.get('text', '')
                        if text:
                            chunk = self._format_chunk(text)
                            yield chunk

                    elif event_type == 'message_stop':
                        logger.info('Anthropic complete: input_tokens=%d output_tokens=%d', input_tokens, output_tokens)
                        yield self._format_done(input_tokens, output_tokens)
                        return

                    elif event_type == 'error':
                        error_data = data.get('error', {})
                        error_msg = error_data.get('message', 'Unknown error')
                        error_response = self._format_error(error_msg)
                        yield error_response
                        return

        except Exception as e:
            logger.warning('Anthropic API error: %s', format_exc())
            yield self._format_error(e)

# ################################################################################################################################
# ################################################################################################################################
