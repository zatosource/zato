# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Redis
from redis import Redis

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.distlock import LockManager
from zato.server.connection.cache import CacheAPI
from zato.server.connection.llm.store import ChatHistoryStore
from zato.server.generic.api.outconn_llm import OutconnLLMWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class _TestConfigManager:
    """ Carries just what the wrapper reaches for on the real config manager.
    """
    def __init__(self, cache_api:'CacheAPI') -> 'None':
        self.cache_api = cache_api
        self.generic_conn_api = {}

# ################################################################################################################################
# ################################################################################################################################

class _TestParallelServer:
    """ Carries just what the wrapper reaches for on the real parallel server.
    """
    def __init__(self, cache_api:'CacheAPI') -> 'None':
        self.config_manager = _TestConfigManager(cache_api)
        self.zato_lock_manager = LockManager('zato-pass-through', 'zato', cast_('any_', None))

# ################################################################################################################################
# ################################################################################################################################

def _get_wrapper(
    llm_test_server:'any_',
    redis_server:'anydict',
    conn_name:'str',
    max_history_turns:'int'=20,
    chat_expiry:'int'=86400,
) -> 'tuple[OutconnLLMWrapper, CacheAPI]':
    """ Builds a wrapper over the provider simulator with one client ready in its queue,
    backed by the test-managed Redis.
    """
    config = Bunch()
    config.id = 1
    config.name = conn_name
    config.username = None
    config.is_active = True
    config.pool_size = 1
    config.queue_build_cap = 30
    config.address = llm_test_server.url('/v1')
    config.secret = 'test-key'
    config.model = 'gpt-4o-mini'
    config.timeout = 10
    config.max_tokens = 256
    config.max_history_turns = max_history_turns
    config.chat_expiry = chat_expiry

    redis_client = Redis(host=redis_server['host'], port=redis_server['port'])
    cache_api = CacheAPI(redis_client)

    server = _TestParallelServer(cache_api)
    wrapper = OutconnLLMWrapper(config, cast_('any_', server))

    # Build the one client synchronously instead of through the queue's greenlets
    wrapper.add_client()

    out = (wrapper, cache_api)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLLMChat:

    def test_invoke_is_one_shot(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        wrapper, cache_api = _get_wrapper(llm_test_server, redis_server, 'chat.oneshot.invoke')
        llm_test_server.configure('/v1/chat/completions', reply_text='One-shot reply')

        response = wrapper.invoke('Hello')

        assert response['text'] == 'One-shot reply'

        # Nothing was written to the history store
        store = ChatHistoryStore(cache_api, 'chat.oneshot.invoke', 86400)
        assert store.load('any-chat-id') == []

# ################################################################################################################################

    def test_chat_without_chat_id_is_one_shot(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        wrapper, cache_api = _get_wrapper(llm_test_server, redis_server, 'chat.oneshot.chat')

        _ = wrapper.chat('Hello')

        # Only the current message went out and nothing was stored
        request = llm_test_server.last_request
        assert request['body']['messages'] == [{'role': 'user', 'content': 'Hello'}]

        store = ChatHistoryStore(cache_api, 'chat.oneshot.chat', 86400)
        assert store.load('any-chat-id') == []

# ################################################################################################################################

    def test_chat_appends_and_replays_history(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        wrapper, cache_api = _get_wrapper(llm_test_server, redis_server, 'chat.history')

        # First turn ..
        llm_test_server.configure('/v1/chat/completions', reply_text='reply-1')
        response1 = wrapper.chat('First question', 'chat-123')
        assert response1['text'] == 'reply-1'

        # .. second turn, which must carry the whole first turn along.
        llm_test_server.configure('/v1/chat/completions', reply_text='reply-2')
        response2 = wrapper.chat('Second question', 'chat-123')
        assert response2['text'] == 'reply-2'

        request = llm_test_server.last_request
        assert request['body']['messages'] == [
            {'role': 'user', 'content': 'First question'},
            {'role': 'assistant', 'content': 'reply-1'},
            {'role': 'user', 'content': 'Second question'},
        ]

        # The stored history holds both full turns
        store = ChatHistoryStore(cache_api, 'chat.history', 86400)
        history = store.load('chat-123')
        assert history == [
            {'role': 'user', 'content': 'First question'},
            {'role': 'assistant', 'content': 'reply-1'},
            {'role': 'user', 'content': 'Second question'},
            {'role': 'assistant', 'content': 'reply-2'},
        ]

        # The key carries the configured expiry
        redis_key = 'zato:cache:' + store.get_key('chat-123')
        ttl = cache_api.redis.ttl(redis_key)
        assert 0 < ttl <= 86400

# ################################################################################################################################

    def test_chat_trims_what_it_sends_but_keeps_full_history(
        self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        # Two turns of history means at most three messages ever go out
        wrapper, cache_api = _get_wrapper(llm_test_server, redis_server, 'chat.trim', max_history_turns=2)

        for turn_number in range(1, 5):
            llm_test_server.configure('/v1/chat/completions', reply_text=f'reply-{turn_number}')
            _ = wrapper.chat(f'question-{turn_number}', 'chat-trim')

        # The last request was trimmed to the newest two turns
        request = llm_test_server.last_request
        assert request['body']['messages'] == [
            {'role': 'user', 'content': 'question-3'},
            {'role': 'assistant', 'content': 'reply-3'},
            {'role': 'user', 'content': 'question-4'},
        ]

        # The store still holds all four turns
        store = ChatHistoryStore(cache_api, 'chat.trim', 86400)
        history = store.load('chat-trim')
        history_length = len(history)
        assert history_length == 8

        assert history[0] == {'role': 'user', 'content': 'question-1'}
        assert history[7] == {'role': 'assistant', 'content': 'reply-4'}

# ################################################################################################################################

    def test_chat_history_expires(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        wrapper, cache_api = _get_wrapper(llm_test_server, redis_server, 'chat.expiry', chat_expiry=1)

        _ = wrapper.chat('Hello', 'chat-expiry')

        store = ChatHistoryStore(cache_api, 'chat.expiry', 1)
        history = store.load('chat-expiry')
        history_length = len(history)
        assert history_length == 2

        # Once the expiry passes, the history is gone and the chat starts afresh
        time.sleep(1.2)
        assert store.load('chat-expiry') == []

# ################################################################################################################################

    def test_chat_history_survives_wrapper_rebuild(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        wrapper1, _ = _get_wrapper(llm_test_server, redis_server, 'chat.rebuild')
        llm_test_server.configure('/v1/chat/completions', reply_text='reply-1')
        _ = wrapper1.chat('First question', 'chat-rebuild')

        # A new wrapper for the same connection name sees the same history - it lives in Redis, not in the wrapper
        wrapper2, _ = _get_wrapper(llm_test_server, redis_server, 'chat.rebuild')
        llm_test_server.configure('/v1/chat/completions', reply_text='reply-2')
        _ = wrapper2.chat('Second question', 'chat-rebuild')

        request = llm_test_server.last_request
        assert request['body']['messages'] == [
            {'role': 'user', 'content': 'First question'},
            {'role': 'assistant', 'content': 'reply-1'},
            {'role': 'user', 'content': 'Second question'},
        ]

# ################################################################################################################################

    def test_ping_checks_the_models_endpoint(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        wrapper, _ = _get_wrapper(llm_test_server, redis_server, 'chat.ping')
        wrapper.ping()

        request = llm_test_server.last_request
        assert request['path'] == '/v1/models'

# ################################################################################################################################
# ################################################################################################################################
