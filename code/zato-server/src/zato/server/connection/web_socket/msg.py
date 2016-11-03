# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from httplib import FORBIDDEN, NOT_FOUND, OK

# Bunch
from bunch import Bunch

# pyrapidjson
from rapidjson import dumps

# Zato
from zato.common import DATA_FORMAT
from zato.common.util import make_repr, new_cid

# ################################################################################################################################

xml_error_template = '<?xml version="1.0" encoding="utf-8"?><error>{}</error>'

copy_forbidden = b'You are not authorized to access this resource'
copy_not_found = b'Not found'

error_response = {

    FORBIDDEN: {
        DATA_FORMAT.JSON: dumps({'error': copy_forbidden}),
        DATA_FORMAT.XML: xml_error_template.format(copy_forbidden)
    },

    NOT_FOUND: {
        DATA_FORMAT.JSON: dumps({'error': copy_not_found}),
        DATA_FORMAT.XML: xml_error_template.format(copy_not_found)
    }

}

# ################################################################################################################################

class MSG_PREFIX:
    _COMMON = 'zato.ws.server.{}'

    REQ_TO_CLIENT = _COMMON.format('req-client')
    RESP_AUTH = _COMMON.format('resp-auth')
    RESP_SERVICE_INVOKE_OK = _COMMON.format('resp-ok')
    RESP_SERVICE_INVOKE_ERROR = _COMMON.format('resp-err')

# ################################################################################################################################

class ClientMessage(object):
    """ An individual message received from a WebSocket client.
    """
    def __init__(self):
        self.action = None
        self.service = None
        self.sec_type = None
        self.username = None
        self.password = None
        self.id = None
        self.timestamp = None
        self.cid = new_cid()
        self.in_reply_to = None
        self.data = Bunch()
        self.has_credentials = None
        self.token = None
        self.ext_client_name = None
        self.ext_client_id = None

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class ServerMessage(object):
    """ A message sent from a WebSocket server to a client.
    """
    is_response = True

    def __init__(self, id_prefix, cid, in_reply_to=None, status=OK, error_message='', _now=datetime.utcnow):
        self.id = '{}.{}'.format(id_prefix, cid)
        self.in_reply_to = in_reply_to
        self.meta = Bunch(id=self.id, timestamp=_now().isoformat())
        self.data = Bunch()

        if self.is_response:
            self.meta.in_reply_to = in_reply_to
            self.meta.status = status

        if error_message:
            self.meta.error_message = error_message

    def serialize(self):
        return dumps({
            'meta': self.meta,
            'data': self.data,
        })

# ################################################################################################################################

class AuthenticateResponse(ServerMessage):
    def __init__(self, token, *args, **kwargs):
        super(AuthenticateResponse, self).__init__(MSG_PREFIX.RESP_AUTH, *args, **kwargs)
        self.data.token = token

# ################################################################################################################################

class OKResponse(ServerMessage):
    def __init__(self, cid, in_reply_to, data, *ignored_args, **ignored_kwargs):
        super(OKResponse, self).__init__(MSG_PREFIX.RESP_SERVICE_INVOKE_OK, cid, in_reply_to)
        self.data = data

# ################################################################################################################################

class ErrorResponse(ServerMessage):
    def __init__(self, cid, in_reply_to, status, error_message):
        super(ErrorResponse, self).__init__(MSG_PREFIX.RESP_SERVICE_INVOKE_ERROR, cid, in_reply_to, status, error_message)
        self.data = {'cid': cid}

# ################################################################################################################################

class ClientInvokeRequest(ServerMessage):
    is_response = False

    def __init__(self, cid, data):
        super(ClientInvokeRequest, self).__init__(MSG_PREFIX.REQ_TO_CLIENT, cid)
        self.data = data

# ################################################################################################################################