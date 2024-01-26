# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK
from json import dumps
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import DATA_FORMAT, WEB_SOCKET
from zato.common.util.api import make_repr, new_cid
from zato.cy.reqresp.payload import SimpleIOPayload

# Past builtins
from zato.common.py23_.past.builtins import basestring

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# This is an from our WSX gateway that the actual response, if any, is wrapped in that element
wsx_gateway_response_elem = WEB_SOCKET.GatewayResponseElem

# ################################################################################################################################
# ################################################################################################################################

copy_bad_request = 'Bad request'
copy_forbidden = 'You are not authorized to access this resource'
copy_not_found = 'Not found'

error_response = {
    BAD_REQUEST: {
        DATA_FORMAT.JSON: dumps({'error': copy_bad_request}).encode('latin1'),
    },
    FORBIDDEN: {
        DATA_FORMAT.JSON: dumps({'error': copy_forbidden}).encode('latin1'),
    },
    NOT_FOUND: {
        DATA_FORMAT.JSON: dumps({'error': copy_not_found}).encode('latin1'),
    },
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

class ClientMessage:
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
        self.ext_client_name = ''
        self.ext_client_id = None
        self.reply_to_sk = None
        self.deliver_to_sk = None
        self.client_attrs = {}

        self.is_auth = False
        self.secret = ''

    def __repr__(self):
        return make_repr(self)

    def get_meta(self, attrs=('action', 'service', 'id', 'timestamp', 'cid', 'in_reply_to', 'ext_client_id', 'ext_client_name')):
        out = {}
        for name in attrs:
            out[name] = getattr(self, name)
        return out

# ################################################################################################################################

class ServerMessage:
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

    def serialize(self, _dumps_func):
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

                        # If this is a response from a WSX gateway (helpers.web-sockets-gateway),
                        # we need to extract its actual payload.
                        if isinstance(data, dict):
                            if wsx_gateway_response_elem in data:
                                data = data[wsx_gateway_response_elem]

                else:
                    data = self.data

                if isinstance(data, basestring):
                    data = data if isinstance(data, str) else data.decode('utf8')

                msg['data'] = data

            return _dumps_func(msg)
        except Exception:
            logger.warning('Exception while serializing message `%r`, e:`%s`', msg, format_exc())
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
