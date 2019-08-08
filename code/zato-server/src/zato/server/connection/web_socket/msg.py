# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from http.client import FORBIDDEN, NOT_FOUND, OK
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import Bunch

# pyrapidjson
from rapidjson import dumps

# Zato
from zato.common import DATA_FORMAT
from zato.common.util import make_repr, new_cid
from zato.server.service.reqresp import SimpleIOPayload

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

xml_error_template = '<?xml version="1.0" encoding="utf-8"?><error>{}</error>'

copy_forbidden = b'You are not authorized to access this resource'
copy_not_found = b'Not found'

error_response = {

    NOT_FOUND: {
        DATA_FORMAT.JSON: dumps({'error': copy_not_found}),
        DATA_FORMAT.XML: xml_error_template.format(copy_not_found)
    }

}

# ################################################################################################################################

class MSG_TYPE:
    _COMMON = 'zwsx.{}'

    REQ_TO_CLIENT = _COMMON.format('rqc')
    RESP_AUTH = _COMMON.format('rspa')
    RESP_OK = _COMMON.format('rspok')

    # A message from server indicating an error, no response from client is expected
    MSG_ERR = _COMMON.format('merr')

    # As above but in response to a previous request from client
    RESP_ERROR = _COMMON.format('rsperr')

    # A publish/subscribe message from server to client
    PUBSUB_REQ = _COMMON.format('psrq')

    # A client response to a previous pub/sub request
    PUBSUB_RESP = _COMMON.format('psrsp')

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
        self.reply_to_sk = None
        self.deliver_to_sk = None

    def __repr__(self):
        return make_repr(self)

    def get_meta(self, attrs=('action', 'service', 'id', 'timestamp', 'cid', 'in_reply_to', 'ext_client_id', 'ext_client_name')):
        out = {}
        for name in attrs:
            out[name] = getattr(self, name)
        return out

# ################################################################################################################################

class ServerMessage(object):
    """ A message sent from a WebSocket server to a client.
    """
    is_response = True

    def __init__(self, msg_type, cid, in_reply_to=None, status=OK, error_message='', ctx=None, _now=datetime.utcnow):
        self.id = cid
        self.in_reply_to = in_reply_to
        self.data = Bunch()

        self.meta = Bunch(id=self.id, timestamp=_now().isoformat(), msg_type=msg_type)
        if ctx:
            self.meta.ctx = ctx

        if self.is_response:
            self.meta.status = status
            if in_reply_to:
                self.meta.in_reply_to = in_reply_to

        if error_message:
            self.meta.error_message = error_message

    def serialize(self):
        """ Serialize server message to client. Note that we make it as small as possible because control messages
        in WebSockets (opcode >= 0x07) must have at most 125 bytes.
        """
        msg = {'meta': self.meta}

        try:
            if self.data:
                if isinstance(self.data, SimpleIOPayload):
                    data = self.data.getvalue(serialize=False)
                    keys = list(data.keys())
                    if len(keys) != 1:
                        raise ValueError('Unexpected data `{}`'.format(data))
                    else:
                        response_key = keys[0]
                        data = data[response_key]
                else:
                    data = self.data
                msg['data'] = data
            return dumps(msg)
        except Exception:
            logger.warn('Exception while serializing message `%r`, e:`%s`', msg, format_exc())
            raise

# ################################################################################################################################

class AuthenticateResponse(ServerMessage):
    def __init__(self, token, cid, *args, **kwargs):
        super(AuthenticateResponse, self).__init__(MSG_TYPE.RESP_AUTH, cid, *args, **kwargs)
        self.data.token = token

# ################################################################################################################################

class OKResponse(ServerMessage):
    def __init__(self, cid, in_reply_to, data, *ignored_args, **ignored_kwargs):
        super(OKResponse, self).__init__(MSG_TYPE.RESP_OK, cid, in_reply_to)
        self.data = data

# ################################################################################################################################

class ErrorResponse(ServerMessage):
    def __init__(self, cid, in_reply_to, status, error_message):
        super(ErrorResponse, self).__init__(MSG_TYPE.RESP_ERROR, cid, in_reply_to, status, error_message)
        self.data = {'cid': cid}

# ################################################################################################################################

class InvokeClientRequest(ServerMessage):
    is_response = False

    def __init__(self, cid, data, ctx, _msg_type=MSG_TYPE.REQ_TO_CLIENT):
        super(InvokeClientRequest, self).__init__(_msg_type, cid, ctx=ctx)
        self.data = data

class InvokeClientPubSubRequest(InvokeClientRequest):
    def __init__(self, cid, data, ctx, _msg_type=MSG_TYPE.PUBSUB_REQ):
        super(InvokeClientPubSubRequest, self).__init__(cid, data, ctx, _msg_type)

# ################################################################################################################################

class Forbidden(ServerMessage):
    is_response = True

    def __init__(self, cid, data):
        super(Forbidden, self).__init__(MSG_TYPE.MSG_ERR, cid, status=FORBIDDEN)
        self.data = data

# ################################################################################################################################
