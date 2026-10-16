# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the directory the hook marker file lives in -
# the test suite sets it for the server process and reads the file to prove
# which messages and replies passed through the hook services.
_marker_dir_env_key = 'Zato_Test_LLM_Marker_Dir'

# The file each hook invocation appends one line to
_hook_file_name = 'hooks.txt'

# The tool whose arguments the replacing request hook rewrites and the order id it substitutes
_replaced_tool_name = 'crm.order.status'
_replaced_order_id  = 'ORD-HOOK-9001'

# The tool the rejecting request hook refuses
_rejected_tool_name = 'crm.order.cancel'

# What the replacing response hook puts in place of every tool result
_replaced_result = {'replaced_by': 'crm.hook.response-replace'}

# ################################################################################################################################
# ################################################################################################################################

def _record(*parts:'object') -> 'None':
    """ Appends one line made of the given parts to the hook marker file.
    """
    marker_dir = os.environ[_marker_dir_env_key]
    hook_path = os.path.join(marker_dir, _hook_file_name)
    line = ' '.join(str(part) for part in parts)

    with open(hook_path, 'a') as hook_file:
        _ = hook_file.write(line + '\n')

# ################################################################################################################################

def _tool_name_of(message:'anydict') -> 'str':
    """ The tool a tools/call message names, or an empty string for every other message.
    """
    if message['method'] != 'tools/call':
        return ''

    out = message['params']['name']
    return out

# ################################################################################################################################
# ################################################################################################################################

class RequestRecord(Service):
    """ Records every message its gateway receives and leaves the message unchanged.
    """
    name = 'crm.hook.request-record'

    def handle(self):
        payload = self.request.payload
        _record('request', payload['gateway'], payload['method'], payload['username'], _tool_name_of(payload['request']))

# ################################################################################################################################

class ResponseRecord(Service):
    """ Records every reply its gateway sends and leaves the reply unchanged.
    """
    name = 'crm.hook.response-record'

    def handle(self):
        payload = self.request.payload
        reply_kind = 'error' if 'error' in payload['response'] else 'result'
        _record('response', payload['gateway'], payload['method'], reply_kind)

# ################################################################################################################################

class RequestReplace(Service):
    """ Rewrites the order id of every order status call and leaves every other message unchanged.
    """
    name = 'crm.hook.request-replace'

    def handle(self):
        payload = self.request.payload
        message = payload['request']

        if _tool_name_of(message) != _replaced_tool_name:
            return

        message['params']['arguments']['order_id'] = _replaced_order_id
        _record('replace', payload['gateway'], payload['method'], _replaced_order_id)

        self.response.payload = {'request': message}

# ################################################################################################################################

class RequestReject(Service):
    """ Refuses every order cancellation and lets every other message through.
    """
    name = 'crm.hook.request-reject'

    def handle(self):
        payload = self.request.payload

        if _tool_name_of(payload['request']) == _rejected_tool_name:
            _record('reject', payload['gateway'], payload['method'], _rejected_tool_name)
            raise Exception('Order cancellations are not permitted through this gateway')

# ################################################################################################################################

class ResponseReplace(Service):
    """ Replaces the content of every tool result and leaves every other reply unchanged.
    """
    name = 'crm.hook.response-replace'

    def handle(self):
        payload = self.request.payload
        body = payload['response']

        if payload['method'] != 'tools/call':
            return

        if 'result' not in body:
            return

        body['result'] = {'content': [{'type': 'text', 'text': dumps(_replaced_result)}]}
        _record('response-replace', payload['gateway'], payload['method'])

        self.response.payload = {'response': body}

# ################################################################################################################################
# ################################################################################################################################
