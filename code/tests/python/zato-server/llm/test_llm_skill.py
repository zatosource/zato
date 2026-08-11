# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import gettempdir, TemporaryDirectory

# pytest
import pytest

# Redis
from redis import Redis

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.skills.api import skill_file_name, skills_directory_name
from zato.common.typing_ import cast_
from zato.distlock import LockManager
from zato.server.connection.cache import CacheAPI
from zato.server.generic.api.outconn_llm import OutconnLLMWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_skill_name = 'invoice-mapping'

_skill_contents = """---
name: invoice-mapping
description: How invoices map between systems
---

Map the invoice number to the reference field.
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
        self.name = 'test-llm-skill-server'
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

def _get_wrapper(llm_test_server:'any_', redis_server:'anydict', repo_location:'str') -> 'OutconnLLMWrapper':
    """ Builds a wrapper over the provider simulator with one client ready in its queue,
    reading skills from the given repository directory.
    """
    config = Bunch()
    config.id = 1
    config.name = 'llm.skill'
    config.username = None
    config.is_active = True
    config.pool_size = 1
    config.queue_build_cap = 30
    config.address = llm_test_server.url('/v1')
    config.secret = 'test-key'
    config.model = 'gpt-4o-mini'
    config.timeout = 10
    config.max_tokens = 256
    config.max_history_turns = 20
    config.chat_expiry = 86400

    redis_client = Redis(host=redis_server['host'], port=redis_server['port'])
    cache_api = CacheAPI(redis_client)

    server = _TestParallelServer(cache_api, repo_location)
    out = OutconnLLMWrapper(config, cast_('any_', server))

    # Build the one client synchronously instead of through the queue's greenlets
    out.add_client()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLLMSkill:

    def test_invoke_with_skill_prepends_system_context(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location)

            wrapper = _get_wrapper(llm_test_server, redis_server, repo_location)
            llm_test_server.configure('/v1/chat/completions', reply_text='With skill')

            response = wrapper.invoke('Map this invoice', skill=_skill_name)

            assert response['text'] == 'With skill'

            # The skill's instructions went out as the system message, before the user's turn
            request = llm_test_server.last_request
            body = request['body']
            messages = body['messages']

            assert messages == [
                {'role': 'system', 'content': 'Map the invoice number to the reference field.'},
                {'role': 'user', 'content': 'Map this invoice'},
            ]

# ################################################################################################################################

    def test_invoke_without_skill_sends_no_system_context(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        with TemporaryDirectory() as repo_location:

            wrapper = _get_wrapper(llm_test_server, redis_server, repo_location)

            _ = wrapper.invoke('Hello')

            request = llm_test_server.last_request
            body = request['body']
            messages = body['messages']

            assert messages == [{'role': 'user', 'content': 'Hello'}]

# ################################################################################################################################

    def test_invoke_with_missing_skill_is_an_error(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        with TemporaryDirectory() as repo_location:

            wrapper = _get_wrapper(llm_test_server, redis_server, repo_location)

            with pytest.raises(Exception, match='Skill not found'):
                _ = wrapper.invoke('Hello', skill='no-such-skill')

# ################################################################################################################################

    def test_chat_sends_skill_context_but_never_stores_it(self, llm_test_server:'any_', redis_server:'anydict') -> 'None':

        with TemporaryDirectory() as repo_location:

            _write_skill(repo_location)

            wrapper = _get_wrapper(llm_test_server, redis_server, repo_location)

            # Two turns of one chat, both with the skill ..
            llm_test_server.configure('/v1/chat/completions', reply_text='reply-1')
            _ = wrapper.chat('First question', 'chat-skill', skill=_skill_name)

            llm_test_server.configure('/v1/chat/completions', reply_text='reply-2')
            _ = wrapper.chat('Second question', 'chat-skill', skill=_skill_name)

            # .. the second request carries the system context once, in front of the history ..
            request = llm_test_server.last_request
            body = request['body']
            messages = body['messages']

            assert messages == [
                {'role': 'system', 'content': 'Map the invoice number to the reference field.'},
                {'role': 'user', 'content': 'First question'},
                {'role': 'assistant', 'content': 'reply-1'},
                {'role': 'user', 'content': 'Second question'},
            ]

# ################################################################################################################################
# ################################################################################################################################
