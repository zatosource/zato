# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# requests
from requests.sessions import Session as RequestsSession

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

class LLMError(Exception):
    """ Raised when an LLM provider rejects a request or returns an error - carries the provider's response body verbatim.
    """
    def __init__(self, message:'str', provider_body:'str') -> 'None':
        super().__init__(message)
        self.provider_body = provider_body

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
