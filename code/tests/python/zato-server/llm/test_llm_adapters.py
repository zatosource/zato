# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK, SERVICE_UNAVAILABLE

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch
from zato.server.connection.llm.claude import ClaudeClient
from zato.server.connection.llm.common import LLMError
from zato.server.connection.llm.gemini import GeminiClient
from zato.server.connection.llm.openai_ import OpenAIClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

from llm_test_server import Input_Tokens, Output_Tokens

# ################################################################################################################################
# ################################################################################################################################

def _get_config(address:'str', model:'str', api_key:'str') -> 'Bunch':

    config = Bunch()
    config.name = 'Test LLM'
    config.address = address
    config.secret = api_key
    config.model = model
    config.timeout = 10
    config.max_tokens = 256

    return config

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAIClient:

    def _get_client(self, llm_test_server:'any_', api_key:'str'='test-key-openai') -> 'OpenAIClient':
        config = _get_config(llm_test_server.url('/v1'), 'gpt-4o-mini', api_key)
        out = OpenAIClient(config)
        return out

# ################################################################################################################################

    def test_invoke_maps_response(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        llm_test_server.configure('/v1/chat/completions', reply_text='Nice to meet you')

        response = client.invoke([{'role': 'user', 'content': 'Hello'}])

        assert response['text'] == 'Nice to meet you'
        assert response['usage'] == {'input_tokens': Input_Tokens, 'output_tokens': Output_Tokens}
        assert response['raw']['id'] == 'chatcmpl-test-1'

        # The request carried the model, the messages and the key
        request = llm_test_server.last_request
        assert request['path'] == '/v1/chat/completions'
        assert request['body']['model'] == 'gpt-4o-mini'
        assert request['body']['messages'] == [{'role': 'user', 'content': 'Hello'}]
        assert request['headers']['Authorization'] == 'Bearer test-key-openai'

# ################################################################################################################################

    def test_invoke_without_key_sends_no_auth_header(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server, api_key='')

        _ = client.invoke([{'role': 'user', 'content': 'Hello'}])

        request = llm_test_server.last_request
        assert 'Authorization' not in request['headers']

# ################################################################################################################################

    def test_invoke_error_raises_with_provider_body(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        error_body = {'error': {'message': 'Rate limit reached', 'type': 'rate_limit_error'}}
        llm_test_server.configure('/v1/chat/completions', respond_raw=(SERVICE_UNAVAILABLE, error_body))

        with pytest.raises(LLMError) as exc_info:
            _ = client.invoke([{'role': 'user', 'content': 'Hello'}])

        assert 'Rate limit reached' in exc_info.value.provider_body

# ################################################################################################################################

    def test_ping(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        client.ping()

        request = llm_test_server.last_request
        assert request['path'] == '/v1/models'
        assert request['method'] == 'GET'

# ################################################################################################################################

    def test_ping_error_raises(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        llm_test_server.configure('/v1/models', respond_raw=(BAD_REQUEST, {'error': 'Bad key'}))

        with pytest.raises(LLMError):
            client.ping()

# ################################################################################################################################
# ################################################################################################################################

class TestClaudeClient:

    def _get_client(self, llm_test_server:'any_', api_key:'str'='test-key-claude') -> 'ClaudeClient':
        config = _get_config(llm_test_server.address, 'claude-sonnet-4-5', api_key)
        out = ClaudeClient(config)
        return out

# ################################################################################################################################

    def test_invoke_maps_response(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        llm_test_server.configure('/v1/messages', reply_text='Nice to meet you')

        response = client.invoke([{'role': 'user', 'content': 'Hello'}])

        assert response['text'] == 'Nice to meet you'
        assert response['usage'] == {'input_tokens': Input_Tokens, 'output_tokens': Output_Tokens}
        assert response['raw']['id'] == 'msg_test_1'

        # The request carried the model, max_tokens, the messages and the required headers
        request = llm_test_server.last_request
        assert request['path'] == '/v1/messages'
        assert request['body']['model'] == 'claude-sonnet-4-5'
        assert request['body']['max_tokens'] == 256
        assert request['body']['messages'] == [{'role': 'user', 'content': 'Hello'}]
        assert request['headers']['x-api-key'] == 'test-key-claude'
        assert request['headers']['anthropic-version'] == '2023-06-01'

# ################################################################################################################################

    def test_invoke_lifts_system_messages(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)

        messages = [
            {'role': 'system', 'content': 'You are terse'},
            {'role': 'user', 'content': 'Hello'},
        ]
        _ = client.invoke(messages)

        # The system message became the top-level system field and left the messages list
        request = llm_test_server.last_request
        assert request['body']['system'] == 'You are terse'
        assert request['body']['messages'] == [{'role': 'user', 'content': 'Hello'}]

# ################################################################################################################################

    def test_invoke_error_raises_with_provider_body(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        error_body = {'type': 'error', 'error': {'type': 'overloaded_error', 'message': 'Overloaded'}}
        llm_test_server.configure('/v1/messages', respond_raw=(SERVICE_UNAVAILABLE, error_body))

        with pytest.raises(LLMError) as exc_info:
            _ = client.invoke([{'role': 'user', 'content': 'Hello'}])

        assert 'Overloaded' in exc_info.value.provider_body

# ################################################################################################################################

    def test_ping(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        client.ping()

        request = llm_test_server.last_request
        assert request['path'] == '/v1/models'
        assert request['method'] == 'GET'

# ################################################################################################################################
# ################################################################################################################################

class TestGeminiClient:

    def _get_client(self, llm_test_server:'any_', api_key:'str'='test-key-gemini') -> 'GeminiClient':
        config = _get_config(llm_test_server.url('/v1beta'), 'gemini-2.0-flash', api_key)
        out = GeminiClient(config)
        return out

# ################################################################################################################################

    def test_invoke_maps_response(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        llm_test_server.configure('/v1beta/models/gemini-2.0-flash:generateContent', reply_text='Nice to meet you')

        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi'},
            {'role': 'user', 'content': 'How are you?'},
        ]
        response = client.invoke(messages)

        assert response['text'] == 'Nice to meet you'
        assert response['usage'] == {'input_tokens': Input_Tokens, 'output_tokens': Output_Tokens}
        assert response['raw']['candidates'][0]['finishReason'] == 'STOP'

        # The request carried the contents with user and model roles, plus the key header
        request = llm_test_server.last_request
        assert request['path'] == '/v1beta/models/gemini-2.0-flash:generateContent'
        assert request['body']['contents'] == [
            {'role': 'user', 'parts': [{'text': 'Hello'}]},
            {'role': 'model', 'parts': [{'text': 'Hi'}]},
            {'role': 'user', 'parts': [{'text': 'How are you?'}]},
        ]
        assert request['headers']['x-goog-api-key'] == 'test-key-gemini'

# ################################################################################################################################

    def test_invoke_maps_system_instruction(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)

        messages = [
            {'role': 'system', 'content': 'You are terse'},
            {'role': 'user', 'content': 'Hello'},
        ]
        _ = client.invoke(messages)

        # The system message became the systemInstruction and left the contents list
        request = llm_test_server.last_request
        assert request['body']['systemInstruction'] == {'parts': [{'text': 'You are terse'}]}
        assert request['body']['contents'] == [{'role': 'user', 'parts': [{'text': 'Hello'}]}]

# ################################################################################################################################

    def test_blocked_prompt_raises(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)

        # A blocked prompt is an in-band error inside an OK response
        blocked_body = {'promptFeedback': {'blockReason': 'SAFETY'}}
        llm_test_server.configure('/v1beta/models/gemini-2.0-flash:generateContent', respond_raw=(OK, blocked_body))

        with pytest.raises(LLMError) as exc_info:
            _ = client.invoke([{'role': 'user', 'content': 'Hello'}])

        assert 'SAFETY' in str(exc_info.value)

# ################################################################################################################################

    def test_invoke_error_raises_with_provider_body(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        error_body = {'error': {'code': 400, 'message': 'API key not valid', 'status': 'INVALID_ARGUMENT'}}
        llm_test_server.configure('/v1beta/models/gemini-2.0-flash:generateContent', respond_raw=(BAD_REQUEST, error_body))

        with pytest.raises(LLMError) as exc_info:
            _ = client.invoke([{'role': 'user', 'content': 'Hello'}])

        assert 'API key not valid' in exc_info.value.provider_body

# ################################################################################################################################

    def test_ping(self, llm_test_server:'any_') -> 'None':

        client = self._get_client(llm_test_server)
        client.ping()

        request = llm_test_server.last_request
        assert request['path'] == '/v1beta/models'
        assert request['method'] == 'GET'

# ################################################################################################################################
# ################################################################################################################################
