# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# requests
from requests.sessions import Session as RequestsSession

# Zato
from zato.common.audit_log.common import LLMFinish

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    Bunch = Bunch

# ################################################################################################################################
# ################################################################################################################################

# The role names messages carry in chat history and in requests to providers
Role_System    = 'system'
Role_User      = 'user'
Role_Assistant = 'assistant'

# ################################################################################################################################
# ################################################################################################################################

# Each provider's own finish reasons mapped onto the shared vocabulary - OpenAI's in lower case, Claude's in snake case,
# Gemini's in upper case. A reason absent from here is written lowercased as the provider sent it.
_finish_reason_map = {

    # The model stopped on its own
    'stop':     LLMFinish.Stop,
    'end_turn': LLMFinish.Stop,
    'STOP':     LLMFinish.Stop,

    # The model ran out of tokens - the completion is truncated
    'length':     LLMFinish.Length,
    'max_tokens': LLMFinish.Length,
    'MAX_TOKENS': LLMFinish.Length,

    # The provider declined to answer - a content filter or a safety block
    'content_filter':     LLMFinish.Refusal,
    'refusal':            LLMFinish.Refusal,
    'SAFETY':             LLMFinish.Refusal,
    'RECITATION':         LLMFinish.Refusal,
    'PROHIBITED_CONTENT': LLMFinish.Refusal,
    'BLOCKLIST':          LLMFinish.Refusal,
    'SPII':               LLMFinish.Refusal,

    # The model asked for a tool to be called
    'tool_calls': LLMFinish.Tool_Use,
    'tool_use':   LLMFinish.Tool_Use,
}

# ################################################################################################################################

def normalize_finish_reason(value:'str | None') -> 'str':
    """ One provider's finish reason in the shared vocabulary - stop, length, refusal or tool_use - with anything
    the map does not know lowercased as it came and a missing reason an empty string.
    """
    if value is None:
        return ''

    if value in _finish_reason_map:
        out = _finish_reason_map[value]
    else:
        out = value.lower()

    return out

# ################################################################################################################################
# ################################################################################################################################

class LLMError(Exception):
    """ Raised when an LLM provider rejects a request or returns an error - carries the provider's response body verbatim,
    the HTTP status code and reason of the response when there was one, and the finish reason when the provider answered
    with HTTP 200 yet declined to complete, as Gemini does when it blocks a prompt.
    """
    def __init__(self, message:'str', provider_body:'str', status_code:'int'=0, reason:'str'='',
        finish_reason:'str'='') -> 'None':
        super().__init__(message)
        self.provider_body = provider_body
        self.status_code = status_code
        self.reason = reason
        self.finish_reason = finish_reason

# ################################################################################################################################
# ################################################################################################################################

class LLMClient:
    """ A base class for LLM provider clients - holds the connection's configuration and the HTTP session.
    """
    def __init__(self, config:'Bunch') -> 'None':

        self.config = config
        self.name = config['name'] # type: str

        # The base URL never ends in a slash so paths can always be appended verbatim
        address = config['address'] # type: str
        self.address = address.rstrip('/')

        # The API key is optional - self-hosted providers may not need one
        api_key = config['secret']
        if api_key is None:
            api_key = ''
        self.api_key = api_key # type: str

        self.model = config['model']           # type: str
        self.timeout = config['timeout']       # type: int
        self.max_tokens = config['max_tokens'] # type: int

        self.session = RequestsSession()

# ################################################################################################################################
# ################################################################################################################################
