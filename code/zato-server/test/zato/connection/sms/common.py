# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared fixtures of the SMS provider tests - the connection configuration, the test message, the response
# test double and the callback request context.

# stdlib
from base64 import b64encode
from json import dumps

# Zato
from zato.common.api import SMS
from zato.common.ext.bunch import Bunch
from zato.server.connection.sms.base import Ctx_Headers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The connection every provider is built from
Host = 'https://sms.example.test'
Username = 'account-user'
Password = 'account-secret'
Sender = '+12025550100'
Signature_Secret = 'VonageSignatureSecretForTests1234567890'

# The message every send test sends
To = '+12025550101'
Body = 'Your order 1234 has shipped'
Callback_URL = 'https://zato.example.test/zato/sms/orders'

# The webhook URL callbacks are verified against
Webhook_URL = 'https://zato.example.test/zato/sms/orders'

# ################################################################################################################################
# ################################################################################################################################

class Response:
    """ A test double of a provider's HTTP response.
    """
    def __init__(self, status_code:'int', payload:'any_') -> 'None':
        self.status_code = status_code
        self.ok = status_code < 400

        if isinstance(payload, str):
            self.text = payload
        else:
            self.text = dumps(payload)

# ################################################################################################################################

def new_provider(provider_class:'any_', **extra:'any_') -> 'any_':
    """ A provider instance over the shared connection configuration.
    """
    config = Bunch()
    config.name = 'test.sms.' + provider_class.name
    config[SMS.Field_Host] = Host
    config[SMS.Field_Username] = Username
    config[SMS.Field_Secret] = Password
    config[SMS.Field_Sender] = Sender

    for key, value in extra.items():
        config[key] = value

    out = provider_class(config)
    return out

# ################################################################################################################################

def basic_auth(username:'str', password:'str') -> 'str':
    credentials = f'{username}:{password}'.encode('utf8')
    out = 'Basic ' + b64encode(credentials).decode('ascii')
    return out

# ################################################################################################################################

def ctx(headers:'stranydict') -> 'stranydict':
    """ The request context of a callback, with lower-case header names.
    """
    lowered = {}

    for name, value in headers.items():
        lowered[name.lower()] = value

    out = {Ctx_Headers: lowered}
    return out

# ################################################################################################################################
# ################################################################################################################################
