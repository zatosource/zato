# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdictlist
    from zato.server.connection.cache import CacheAPI

# ################################################################################################################################
# ################################################################################################################################

# All chat history keys share this prefix
_Key_Prefix = 'llm:chat'

# ################################################################################################################################
# ################################################################################################################################

class ChatHistoryStore:
    """ Keeps per-chat message history in Redis - one JSON list per chat, written with an expiry,
    so retention is the expiry and history survives server restarts.
    """
    def __init__(self, cache_api:'CacheAPI', conn_name:'str', chat_expiry:'int') -> 'None':
        self.cache_api = cache_api
        self.conn_name = conn_name
        self.chat_expiry = chat_expiry

# ################################################################################################################################

    def get_key(self, chat_id:'str') -> 'str':
        out = f'{_Key_Prefix}:{self.conn_name}:{chat_id}'
        return out

# ################################################################################################################################

    def load(self, chat_id:'str') -> 'strdictlist':
        """ Returns the chat's history, or an empty list if the chat is new or its history has expired.
        """
        key = self.get_key(chat_id)
        history = self.cache_api.get(key)

        if history is None:
            history = []

        out = history
        return out

# ################################################################################################################################

    def save(self, chat_id:'str', history:'strdictlist') -> 'None':
        """ Stores the chat's history, refreshing its expiry.
        """
        key = self.get_key(chat_id)
        self.cache_api.set(key, history, expiry=self.chat_expiry)

# ################################################################################################################################

    def delete(self, chat_id:'str') -> 'None':
        """ Removes the chat's history.
        """
        key = self.get_key(chat_id)
        self.cache_api.delete(key)

# ################################################################################################################################
# ################################################################################################################################
