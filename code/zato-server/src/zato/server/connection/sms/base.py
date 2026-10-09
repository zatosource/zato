# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The interface of an SMS provider class - building a send request and reading its response, verifying, reading
# and answering a callback, and polling the provider's pull endpoints. A provider class holds the connection
# configuration and no other state.

# stdlib
from typing import NamedTuple

# Zato
from zato.common.api import SMS
from zato.common.sms.model import Kind_Message, Kind_Status, SMSEvent, Status_Sent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.ext.bunch import Bunch
    from zato.common.sms.model import SendResult
    from zato.common.typing_ import any_, anydict, anylist, strdict, stranydict, strnone

    SMSEventList = list[SMSEvent]
    PollRequestList = list['PollRequest']
    PollResult = tuple[SMSEventList, stranydict]
    SendRequest = tuple[str, str, strdict, any_]
    CallbackResponse = tuple[int, str, str]

# ################################################################################################################################
# ################################################################################################################################

# The HTTP method names providers are called with
Method_GET = 'GET'
Method_POST = 'POST'

# The content types providers answer callbacks with
Content_Type_XML = 'text/xml'
Content_Type_Text = 'text/plain'
Content_Type_JSON = 'application/json'

# The HTTP header names read during callback verification, in the lower case the server uses for request headers
Header_Authorization = 'authorization'

# The request context keys of a callback's headers, query string and content type
Ctx_Headers = 'headers'
Ctx_Query = 'query'
Ctx_Content_Type = 'content_type'

# ################################################################################################################################
# ################################################################################################################################

class ProviderError(Exception):
    """ Raised when a provider's response does not match the documented response format.
    """

# ################################################################################################################################

class CallbackRejected(Exception):
    """ Raised when a callback's signature does not verify.
    """

# ################################################################################################################################
# ################################################################################################################################

class PollRequest(NamedTuple):
    """ One HTTP request of a poll - the full URL and the headers.
    """
    method: 'str'
    url: 'str'
    headers: 'strdict'
    params: 'strdict'

    # A tag the provider class reads the response by, e.g. the direction the request lists
    tag: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

def new_event(
    kind:'str',
    id:'str',
    from_:'str',
    to:'str',
    body:'str',
    status:'str',
    error_code:'str',
    received_at:'str',
    raw:'anydict',
    ) -> 'SMSEvent':
    """ Builds one common event out of the fields a provider class read.
    """
    out = SMSEvent()
    out.kind = kind
    out.id = id
    out.from_ = from_
    out.to = to
    out.body = body
    out.status = status
    out.error_code = error_code
    out.received_at = received_at
    out.raw = raw
    return out

# ################################################################################################################################

def new_message_event(id:'str', from_:'str', to:'str', body:'str', received_at:'str', raw:'anydict') -> 'SMSEvent':
    """ Builds an incoming-text event.
    """
    out = new_event(Kind_Message, id, from_, to, body, '', '', received_at, raw)
    return out

# ################################################################################################################################

def new_status_event(id:'str', from_:'str', to:'str', status:'str', error_code:'str', received_at:'str',
    raw:'anydict') -> 'SMSEvent':
    """ Builds a delivery-report event.
    """
    out = new_event(Kind_Status, id, from_, to, '', status, error_code, received_at, raw)
    return out

# ################################################################################################################################

def map_status(mapping:'strdict', provider_status:'str') -> 'str':
    """ Maps a provider's status word onto the common vocabulary. A word not in the mapping maps to Status_Sent.
    """
    key = provider_status.lower()

    if key in mapping:
        out = mapping[key]
    else:
        out = Status_Sent

    return out

# ################################################################################################################################

def text_or_empty(value:'any_') -> 'str':
    """ Returns the value as a string, or an empty string when the value is None.
    """
    if value is None:
        out = ''
    else:
        out = str(value)

    return out

# ################################################################################################################################
# ################################################################################################################################

class Provider:
    """ The base class of every SMS provider. A subclass implements the request and response formats of one provider.
    """
    name = ''

    # The provider's status words, in lower case, mapped onto the common vocabulary
    status_mapping:'strdict' = {}

    def __init__(self, config:'Bunch') -> 'None':
        self.config = config
        self.host = config[SMS.Field_Host].rstrip('/')
        self.username = config[SMS.Field_Username]
        self.password = config[SMS.Field_Secret]
        self.sender = config[SMS.Field_Sender]

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'{self.__class__.__name__}({self.config.name} at {hex(id(self))})'

# ################################################################################################################################

    def build_send_request(self, to:'str', body:'str', sender:'str', callback_url:'strnone') -> 'SendRequest':
        """ The HTTP request that sends one message - its method, URL, headers and data.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def read_send_response(self, response:'Response') -> 'SendResult':
        """ Reads the response to a send request, raising ProviderError when the response is not a success.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def build_ping_request(self) -> 'SendRequest':
        """ The authenticated read request used to verify the connection's credentials.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def verify_callback(self, request_ctx:'stranydict', raw_body:'bytes', url:'str') -> 'None':
        """ Verifies a callback's signature, raising CallbackRejected when it does not verify.
        A provider without callback signatures accepts every callback.
        """

# ################################################################################################################################

    def read_callback(self, request_ctx:'stranydict', raw_body:'bytes') -> 'SMSEventList':
        """ The events one callback contains.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def callback_response(self) -> 'CallbackResponse':
        """ The response to an accepted callback - a status code, a content type and a body.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def build_poll_requests(self, state:'stranydict') -> 'PollRequestList':
        """ The requests of one poll, built from the state the previous poll recorded.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def read_poll_response(self, request:'PollRequest', response:'Response', state:'stranydict') -> 'PollResult':
        """ The events one poll response contains and the state the next poll starts from.
        """
        raise NotImplementedError()

# ################################################################################################################################

    def has_more_pages(self, state:'stranydict') -> 'bool':
        """ Whether the state has pages not yet read, which a further round of the same poll reads.
        """
        return False

# ################################################################################################################################

    def map_status(self, provider_status:'str') -> 'str':
        out = map_status(self.status_mapping, provider_status)
        return out

# ################################################################################################################################
# ################################################################################################################################

# Provider classes by provider constant, registered by the registry module
provider_classes:'anydict' = {}

def register_provider(provider_class:'any_') -> 'None':
    provider_classes[provider_class.name] = provider_class

# ################################################################################################################################

def get_provider_class(name:'str') -> 'any_':
    """ The provider class of one provider constant.
    """
    if name not in provider_classes:
        raise ProviderError(f'SMS provider `{name}` is not one of `{sorted(provider_classes)}`')

    out = provider_classes[name]
    return out

# ################################################################################################################################

def get_provider(config:'Bunch') -> 'Provider':
    """ A provider object bound to one connection's configuration.
    """
    provider_class = get_provider_class(config[SMS.Field_Provider])
    out = provider_class(config)
    return out

# ################################################################################################################################

def get_all_provider_names() -> 'anylist':
    out = sorted(provider_classes)
    return out

# ################################################################################################################################
# ################################################################################################################################
