# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from llm_outconn import change_llm_api_key, create_llm_outconn, delete_llm_outconn, edit_llm_outconn, \
    invoke_llm_outconn_from_ide, ping_llm_outconn, wait_for_llm_invoker_service, wait_for_llm_outconn_row

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.llm.end.to.end.' + CryptoManager.generate_hex_string(32) + '.'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# The connection pool builds its clients in the background right after a connection
# is created in the browser, so the first attempts may find no client yet
_Expected_Log_Patterns = ('No free connections',)

# ################################################################################################################################
# ################################################################################################################################

def _invoke_with_retry(page:'Page', base_url:'str', outconn_name:'str', text:'str', chat_id:'str'='') -> 'anydict':
    """ Invokes an outgoing LLM connection through the pre-deployed service, driven from
    the IDE in the browser, retrying while the connection configured a moment ago
    in the browser propagates to the server.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_llm_outconn_from_ide(page, base_url, outconn_name, text, chat_id=chat_id)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            # The service reports errors as a reply field, e.g. while the connection
            # configured a moment ago is still propagating to the server.
            if error := out.get('error'):
                last_error = error
                time.sleep(_Propagation_Poll_Interval)
                continue

            return out

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

class TestLLMOutconnEndToEnd:
    """ End-to-end scenarios - every connection is configured through the browser
    and then exercised by a pre-deployed service against the live LLM provider simulator,
    with assertions on both what the simulator received and what the service got back.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Expected_Log_Patterns)
    def test_invoke_end_to_end(
        self, logged_in_page:'Page', zato_dashboard:'anydict', llm_test_server:'any_') -> 'None':
        """ A connection created in the browser reaches the provider with the configured
        model and API key, and the reply's text and token usage come back to the service.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_llm_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'invoke'
        api_key = 'key.' + CryptoManager.generate_hex_string(32)

        llm_test_server.clear_requests()
        llm_test_server.configure('/v1/chat/completions', reply_text='Hello from the simulator')

        # Create the connection in the browser and give it a known API key ..
        outconn_id = create_llm_outconn(page, base_url, name, llm_test_server.url('/v1'), {
            'model': 'gpt-4o-mini',
        })
        change_llm_api_key(page, outconn_id, api_key)

        # .. invoke it from the IDE in the browser ..
        result = _invoke_with_retry(page, base_url, name, 'Hello there')

        # .. the reply's text and usage came back to the service ..
        assert result['text'] == 'Hello from the simulator', f'Expected the simulator reply, got: {result}'
        assert result['usage']['input_tokens'] > 0
        assert result['usage']['output_tokens'] > 0

        # .. and the simulator received the configured model, the message and the key.
        request = llm_test_server.last_request
        assert request['path'] == '/v1/chat/completions'
        assert request['body']['model'] == 'gpt-4o-mini'
        assert request['body']['messages'] == [{'role': 'user', 'content': 'Hello there'}]
        assert request['headers']['Authorization'] == f'Bearer {api_key}'

        # The connection pings fine too - by now its pool is built, so this cannot be flaky.
        ping_response = ping_llm_outconn(page, name)
        assert ping_response.status == OK

        # Clean up.
        delete_llm_outconn(page, outconn_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Expected_Log_Patterns)
    def test_edit_changes_model(
        self, logged_in_page:'Page', zato_dashboard:'anydict', llm_test_server:'any_') -> 'None':
        """ Changing the model in the browser's edit form changes what the provider receives.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_llm_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'edit'

        llm_test_server.clear_requests()

        # Create the connection with the initial model and prove it works ..
        outconn_id = create_llm_outconn(page, base_url, name, llm_test_server.url('/v1'), {
            'model': 'gpt-4o-mini',
        })

        _ = _invoke_with_retry(page, base_url, name, 'Before the edit')
        assert llm_test_server.last_request['body']['model'] == 'gpt-4o-mini'

        # .. change the model in the edit form ..
        edit_llm_outconn(page, outconn_id, {'name': name, 'model': 'gpt-4o'})
        _ = wait_for_llm_outconn_row(page, name)

        # .. and keep invoking until the request carries the new model - the edit
        # propagates to the server's connection pool in the background.
        deadline = time.monotonic() + _Propagation_Timeout

        while time.monotonic() < deadline:

            _ = _invoke_with_retry(page, base_url, name, 'After the edit')
            model = llm_test_server.last_request['body']['model']

            if model == 'gpt-4o':
                break

            time.sleep(_Propagation_Poll_Interval)

        else:
            raise Exception(f'The edited model did not reach the provider within {_Propagation_Timeout}s')

        # Clean up.
        delete_llm_outconn(page, outconn_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Expected_Log_Patterns)
    def test_chat_keeps_history(
        self, logged_in_page:'Page', zato_dashboard:'anydict', llm_test_server:'any_') -> 'None':
        """ Two chat calls under the same chat id make the second request carry
        the whole first turn along - the history lives in Redis on the server.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_llm_invoker_service(page, base_url)

        name = _Test_Name_Prefix + 'chat'
        chat_id = 'chat.' + CryptoManager.generate_hex_string(32)

        llm_test_server.clear_requests()

        outconn_id = create_llm_outconn(page, base_url, name, llm_test_server.url('/v1'), {
            'model': 'gpt-4o-mini',
        })

        # The first turn ..
        llm_test_server.configure('/v1/chat/completions', reply_text='reply-1')
        result1 = _invoke_with_retry(page, base_url, name, 'First question', chat_id=chat_id)
        assert result1['text'] == 'reply-1'

        # .. the second turn, which must carry the whole first turn along.
        llm_test_server.configure('/v1/chat/completions', reply_text='reply-2')
        result2 = _invoke_with_retry(page, base_url, name, 'Second question', chat_id=chat_id)
        assert result2['text'] == 'reply-2'

        request = llm_test_server.last_request
        assert request['body']['messages'] == [
            {'role': 'user', 'content': 'First question'},
            {'role': 'assistant', 'content': 'reply-1'},
            {'role': 'user', 'content': 'Second question'},
        ]

        # Clean up.
        delete_llm_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
