# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import gettempdir, TemporaryDirectory

# Redis
from redis import Redis

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.skills.api import skill_file_name, skills_directory_name
from zato.common.typing_ import cast_
from zato.distlock import LockManager
from zato.server.connection.cache import CacheAPI
from zato.server.connection.llm.store import ChatHistoryStore
from zato.server.generic.api.outconn_llm import OutconnLLMWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# A wrapper paired with the cache API its chat history store uses
wrapper_and_cache = tuple[OutconnLLMWrapper, CacheAPI]

# How long one model call may take, in seconds
_timeout = 300

# The chat expiry the tests use, in seconds
_chat_expiry = 86400

# The default skills repository - a directory with no skills in it
_default_repo_location = gettempdir()

# The word the model is told to reply with
_reply_word = 'pineapple'

# The name the model is told to remember across chat turns
_remembered_name = 'Ines'

# The word the skill tells the model to include in every reply
_skill_marker = 'marmalade'

# The skill the model is given and its on-disk contents
_skill_name = 'reply-style'

_skill_contents = f"""---
name: reply-style
description: How to shape every reply
---

Include the word {_skill_marker} in every reply you give.
"""

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
    """ Carries just what the wrapper reaches for on the real parallel server,
    including where the user skills live.
    """
    def __init__(self, cache_api:'CacheAPI', repo_location:'str') -> 'None':
        self.name = 'test-llm-live-server'
        self.config_manager = _TestConfigManager(cache_api)
        self.zato_lock_manager = LockManager('zato-pass-through', 'zato', cast_('any_', None))
        self.repo_location = repo_location

        # A directory with no default-models.yaml, so the wrapper reads the default catalog
        self.user_conf_location = [gettempdir()]

# ################################################################################################################################
# ################################################################################################################################

def _write_skill(repo_location:'str') -> 'None':
    """ Puts the test skill on disk the way the Skills screen lays it out.
    """
    skill_directory = os.path.join(repo_location, skills_directory_name, _skill_name)
    os.makedirs(skill_directory)

    skill_path = os.path.join(skill_directory, skill_file_name)

    with open(skill_path, 'w') as skill_file:
        _ = skill_file.write(_skill_contents)

# ################################################################################################################################
# ################################################################################################################################

def _get_wrapper(
    ollama:'any_',
    redis_server:'anydict',
    conn_name:'str',
    repo_location:'str'=_default_repo_location,
) -> 'wrapper_and_cache':
    """ Builds a wrapper over the real Ollama with one client ready in its queue,
    backed by the test-managed Redis.
    """
    config = Bunch()
    config.id = 1
    config.name = conn_name
    config.username = None
    config.is_active = True
    config.pool_size = 1
    config.queue_build_cap = 30
    config.address = ollama['openai_url']
    config.secret = 'not-needed-for-ollama'
    config.model = ollama['model']
    config.timeout = _timeout
    config.max_tokens = 1024
    config.max_history_turns = 20
    config.chat_expiry = _chat_expiry

    redis_client = Redis(host=redis_server['host'], port=redis_server['port'])
    cache_api = CacheAPI(redis_client)

    server = _TestParallelServer(cache_api, repo_location)
    wrapper = OutconnLLMWrapper(config, cast_('any_', server))

    # Build the one client synchronously instead of through the queue's greenlets
    wrapper.add_client()

    out = (wrapper, cache_api)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLLMOllama:
    """ The outgoing LLM connection against the real local model.
    """

# ################################################################################################################################

    def test_invoke(self, ollama:'any_', redis_server:'anydict') -> 'None':

        wrapper, _ = _get_wrapper(ollama, redis_server, 'llm.live.invoke')

        response = wrapper.invoke(f'Reply with exactly this one word: {_reply_word}')

        assert _reply_word in response['text'].lower(), response['text']
        assert response['usage']['input_tokens'] > 0, response['usage']
        assert response['usage']['output_tokens'] > 0, response['usage']

# ################################################################################################################################

    def test_chat_keeps_history(self, ollama:'any_', redis_server:'anydict') -> 'None':

        wrapper, cache_api = _get_wrapper(ollama, redis_server, 'llm.live.chat')

        # The first turn states a fact ..
        _ = wrapper.chat(f'My name is {_remembered_name}. Remember it.', 'chat-live')

        # .. the second turn asks for the fact back.
        response = wrapper.chat('What is my name? Reply with just the name.', 'chat-live')

        assert _remembered_name in response['text'], response['text']

        # Both full turns are in the store
        store = ChatHistoryStore(cache_api, 'llm.live.chat', _chat_expiry)
        history = store.load('chat-live')
        history_length = len(history)

        assert history_length == 4, history

# ################################################################################################################################

    def test_skill_shapes_the_reply(self, ollama:'any_', redis_server:'anydict') -> 'None':

        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location)

            wrapper, _ = _get_wrapper(ollama, redis_server, 'llm.live.skill', repo_location)

            response = wrapper.invoke('Say hello.', skill=_skill_name)

            assert _skill_marker in response['text'].lower(), response['text']

# ################################################################################################################################

    def test_ping(self, ollama:'any_', redis_server:'anydict') -> 'None':

        wrapper, _ = _get_wrapper(ollama, redis_server, 'llm.live.ping')
        wrapper.ping()

# ################################################################################################################################
# ################################################################################################################################
