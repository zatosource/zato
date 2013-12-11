# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from json import dumps, loads

# Bunch
from bunch import Bunch, bunchify

# lxml
from lxml import objectify

# Zato
from zato.common import CHANNEL, DATA_FORMAT, ZATO_OK
from zato.server.service import Service

class CheckService(Service):
    """ Base class for services that check other Zato services using its own API.
    """
    def invoke_check(self, service, payload, data_format):

        if data_format == DATA_FORMAT.JSON:
            payload = dumps(payload)

        invoke_request = {
            'name': service,
            'payload': payload.encode('base64'),
            'channel': CHANNEL.INTERNAL_CHECK,
            'data_format': data_format,
            'transport': 'plain_http',
        }

        out = self.outgoing.plain_http['zato.check.service']
        invoke_response = out.conn.post(self.cid, invoke_request).data

        self.logger.info('invoke_response [%s]', invoke_response)

        if invoke_response['zato_env']['result'] == ZATO_OK:
            invoke_response = invoke_response['zato_service_invoke_response']
            response = invoke_response['response'].decode('base64')
            return response
        else:
            return invoke_response

    def invoke_check_json(self, service, payload=None):
        r = loads(self.invoke_check(service, payload, DATA_FORMAT.JSON))
        if 'response' in r:
            out = r['response']
        else:
            out = r

        self.logger.info('Returning [%s]', out)
        return bunchify(out)

    def invoke_check_xml(self, service, payload=None):
        return objectify.fromstring(self.invoke_check(service, payload, DATA_FORMAT.XML))
