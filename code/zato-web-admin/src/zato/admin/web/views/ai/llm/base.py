# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from abc import ABC, abstractmethod

if 0:
    from zato.common.typing_ import any_, generator_

# ################################################################################################################################
# ################################################################################################################################

class BaseLLMClient(ABC):
    """ Base class for LLM clients.
    """

    def __init__(self, api_key:'str') -> 'None':
        self.api_key = api_key

# ################################################################################################################################

    @abstractmethod
    def stream_chat(self, model:'str', messages:'list') -> 'generator_':
        """ Streams chat completion responses.
        Yields dicts with 'type' and 'content' keys.
        type can be: 'chunk', 'done', 'error'
        """
        pass

# ################################################################################################################################

    def _format_error(self, error:'any_') -> 'dict':
        """ Formats an error response.
        """
        out = {
            'type': 'error',
            'content': str(error)
        }
        return out

# ################################################################################################################################

    def _format_chunk(self, text:'str') -> 'dict':
        """ Formats a text chunk response.
        """
        out = {
            'type': 'chunk',
            'content': text
        }
        return out

# ################################################################################################################################

    def _format_done(self) -> 'dict':
        """ Formats a done response.
        """
        out = {
            'type': 'done',
            'content': ''
        }
        return out

# ################################################################################################################################
# ################################################################################################################################
