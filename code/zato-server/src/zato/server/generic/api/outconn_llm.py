# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import LLM
from zato.common.llm_models import model_list
from zato.common.typing_ import cast_
from zato.server.connection.llm.claude import ClaudeClient
from zato.server.connection.llm.common import Role_Assistant, Role_User
from zato.server.connection.llm.gemini import GeminiClient
from zato.server.connection.llm.openai_ import OpenAIClient
from zato.server.connection.llm.store import ChatHistoryStore
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import stranydict, strnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.llm.common import LLMClient
    LLMClient = LLMClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Default values applied when a configuration key is missing or None -
# the default model is the first entry of the generated catalog.
llm_config_defaults:'dict[str, object]' = {
    'model': model_list[0]['id'],
    'timeout': LLM.DEFAULT.TIMEOUT,
    'max_tokens': LLM.DEFAULT.MAX_TOKENS,
    'max_history_turns': LLM.DEFAULT.MAX_HISTORY_TURNS,
    'chat_expiry': LLM.DEFAULT.CHAT_EXPIRY,
}

# Config keys that must be integers but may arrive as strings from opaque storage
llm_int_config_keys = ('timeout', 'max_tokens', 'max_history_turns', 'chat_expiry')

# Maps each derived provider to the client class built in add_client
_provider_client_map = {
    LLM.PROVIDER.OPENAI.id: OpenAIClient,
    LLM.PROVIDER.CLAUDE.id: ClaudeClient,
    LLM.PROVIDER.GEMINI.id: GeminiClient,
}

# Maps human-friendly catalog names to the provider and the id sent on the wire,
# built from the generated catalog in zato.common.llm_models.
_catalog_by_name:'dict[str, dict[str, str]]' = {}

for _model in model_list:
    _catalog_by_name[_model['name']] = {'provider': _model['provider'], 'id': _model['id']}

# Hand-typed model names select their protocol by these prefixes,
# with OpenAI the protocol of everything else, self-hosted or proxied included.
_claude_model_prefix = 'claude-'
_gemini_model_prefix = 'gemini-'

# A turn is one user message plus the assistant's reply
_messages_per_turn = 2

# The per-chat lock is held for at most the provider timeout plus this margin, in seconds
_chat_lock_ttl_margin = 30

# How long a competing call waits for the per-chat lock, in seconds
_chat_lock_block = 10

# ################################################################################################################################
# ################################################################################################################################

class OutconnLLMWrapper(Wrapper):
    """ Wraps a queue of connections to LLM providers.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config['auth_url'] = config['address']
        super(OutconnLLMWrapper, self).__init__(config, 'LLM', server)

# ################################################################################################################################

    def add_client(self) -> 'None':

        # The model name alone decides which protocol the connection speaks ..
        model = self.config['model']

        # .. catalog names like "Fable 5" resolve to their provider
        # .. and to the id the provider's API expects ..
        if model in _catalog_by_name:
            entry = _catalog_by_name[model]
            provider = entry['provider']
            self.config['model'] = entry['id']

        # .. while hand-typed names select the protocol by prefix and go out unchanged,
        # .. with OpenAI covering everything self-hosted or proxied.
        elif model.startswith(_claude_model_prefix):
            provider = LLM.PROVIDER.CLAUDE.id
        elif model.startswith(_gemini_model_prefix):
            provider = LLM.PROVIDER.GEMINI.id
        else:
            provider = LLM.PROVIDER.OPENAI.id

        client_class = _provider_client_map[provider]

        try:
            conn = client_class(self.config)
        except Exception:
            logger.warning('LLM client could not be built (%s); e:`%s`', self.config['name'], format_exc())
        else:
            _ = self.client.put_client(conn)

# ################################################################################################################################

    def invoke(self, text:'str') -> 'stranydict':
        """ A one-shot call - nothing is loaded from or saved to the chat history store.
        """
        messages = [{'role': Role_User, 'content': text}]

        with self.client() as client:
            client = cast_('LLMClient', client)
            out = client.invoke(messages)

        return out

# ################################################################################################################################

    def chat(self, text:'str', chat_id:'str'='') -> 'stranydict':
        """ A multi-turn call - history is kept in Redis under the chat's id. Without a chat_id,
        nothing is loaded or saved and the call is a one-shot, exactly like invoke.
        """

        # Without a chat id there is no history to speak of ..
        if not chat_id:
            out = self.invoke(text)
            return out

        # .. the store keeps this chat's history in Redis with the configured expiry ..
        cache_api = self.server.config_manager.cache_api
        store = ChatHistoryStore(cache_api, self.config['name'], self.config['chat_expiry'])

        # .. the per-chat lock serializes concurrent calls to the same chat,
        # .. held for at most the provider timeout plus a margin ..
        lock_name = store.get_key(chat_id)
        lock_ttl = self.config['timeout'] + _chat_lock_ttl_margin

        with self.server.zato_lock_manager(lock_name, ttl=lock_ttl, block=_chat_lock_block):

            # .. load what was said so far and append the user's turn ..
            history = store.load(chat_id)
            history.append({'role': Role_User, 'content': text})

            # .. only the last max_history_turns turns are sent to the provider - a turn is a user message
            # .. plus the assistant's reply and the current user message counts as the newest turn,
            # .. which is why one message fewer than the full turn count goes out ..
            max_messages = self.config['max_history_turns'] * _messages_per_turn - 1
            messages_to_send = history[-max_messages:]

            # .. call the provider ..
            with self.client() as client:
                client = cast_('LLMClient', client)
                response = client.invoke(messages_to_send)

            # .. append the assistant's turn and save the full history with a refreshed expiry -
            # .. older turns stay in Redis until expiry but never leave the store.
            history.append({'role': Role_Assistant, 'content': response['text']})
            store.save(chat_id, history)

        out = response
        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        with self.client() as client:
            client = cast_('LLMClient', client)
            client.ping()

# ################################################################################################################################

    def delete(self, ignored_reason:'strnone'=None) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
