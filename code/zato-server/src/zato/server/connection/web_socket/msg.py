# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
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
        self.cid = new_cid()
        self.in_reply_to = None
        self.data = Bunch()
        self.has_credentials = False
        self.token = None

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class ServerMessage(object):
    """ A message sent from a WebSocket server to a client.
    """
    def __init__(self, id_prefix, in_reply_to, status=OK, error_message=''):
        self.id = '{}.{}'.format(id_prefix, new_cid())
        self.in_reply_to = in_reply_to
        self.meta = Bunch(id=self.id, in_reply_to=in_reply_to, status=status)
        self.data = Bunch()

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
        super(AuthenticateResponse, self).__init__('ws.auth', *args, **kwargs)
        self.data.token = token

# ################################################################################################################################

class ServiceInvokeResponse(ServerMessage):
    def __init__(self, in_reply_to, data, *ignored_args, **ignored_kwargs):
        super(ServiceInvokeResponse, self).__init__('ws.si', in_reply_to)
        self.data = data

# ################################################################################################################################

class ServiceErrorResponse(ServerMessage):
    def __init__(self, in_reply_to, cid, status, error_message):
        super(ServiceErrorResponse, self).__init__('ws.se', in_reply_to, status, error_message)
        self.data = {'cid': cid}

# ################################################################################################################################