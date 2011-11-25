# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, time
from cgi import escape
from string import Template
from traceback import format_exc
from httplib import HTTPConnection

# lxml
from lxml import etree, objectify

# Spring Python
from springpython.config import ApplicationContextAware
from springpython.context import InitializingObject

# Zato
from zato.common import soap_body_xpath, ZATO_OK, ZATO_ERROR, ZatoException, \
     ClientSecurityException, zato_ns_map
from zato.common.util import TRACE1
from zato.common.soap import SOAPPool
from zato.server.service.internal import AdminService

soap_doc = Template("""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>$body</soap:Body></soap:Envelope>""")
zato_message = Template("""
<zato_message xmlns="http://gefira.pl/zato">
    <data>$data</data>
    <zato_env>
        <result>$result</result>
        <req_id>$req_id</req_id>
        <details>$details</details>
    </zato_env>
</zato_message>""")

# Returned if there has been any exception caught.
soap_error = Template("""<?xml version='1.0' encoding='UTF-8'?>
<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/1999/XMLSchema">
   <SOAP-ENV:Body>
     <SOAP-ENV:Fault>
     <faultcode>SOAP-ENV:$faultcode</faultcode>
     <faultstring>[$req_id]
$faultstring</faultstring>
      </SOAP-ENV:Fault>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>""")

# TODO: Clean it up, it's not needed anymore
soap_pool = SOAPPool("http://localhost:17080/soap")

logger = logging.getLogger(__name__)

def soap_invoke(url, postdata, soap_action):
    headers = {"content-type": "text/xml", "SOAPAction": soap_action}
    payload = soap_doc.safe_substitute(body=postdata)

    response = http_pool.urlopen("POST", "/soap", payload, headers)
    return response.data

def get_body_payload(body):
    body_children_count = body[0].countchildren()

    if body_children_count == 0:
        body_payload = None
    elif body_children_count == 1:
        body_payload = body[0].getchildren()[0]
    else:
        body_payload = body[0].getchildren()

    return body_payload

def client_soap_error(req_id, faultstring):
    return soap_error.safe_substitute(faultcode='Client', 
        req_id=req_id, faultstring=faultstring)

def server_soap_error(req_id, faultstring):
    return soap_error.safe_substitute(faultcode='Server',
        req_id=req_id, faultstring=faultstring)

class ClientSOAPException(ZatoException):
    pass

class ServerSOAPException(ZatoException):
    pass

class SOAPChannelStore(object):
    def __init__(self, channels={}, config=None):
        self.channels = channels
        self.config = config

class SOAPConfig(dict):
    pass

class SOAPMessageHandler(ApplicationContextAware):

    def __init__(self, soap_config=None, service_store=None, crypto_manager=None,
                 wss_store=None):
        self.soap_config = soap_config
        self.service_store = service_store
        self.crypto_manager = crypto_manager
        self.wss_store = wss_store

    def handle(self, req_id, request, headers, thread_ctx):
        try:
            logger.debug("[{0}] request=[{1}] headers=[{2}]".format(req_id,
                request, headers))

            # HTTP headers are all uppercased at this point.
            soap_action = headers.get('SOAPACTION')

            if not soap_action:
                return client_soap_error(req_id, 'Client did not send the SOAPAction header')

            # SOAP clients may send an empty header, i.e. SOAPAction: "",
            # as opposed to not sending the header at all.
            soap_action = soap_action.lstrip('"').rstrip('"')

            if not soap_action:
                return client_soap_error(req_id, 'Client sent an empty SOAPAction header')

            service_class_name = self.soap_config.get(soap_action)
            logger.debug('[{0}] service_class_name=[{1}]'.format(req_id,
                service_class_name))

            if not service_class_name:
                return client_soap_error(req_id, '[{0}] Unrecognized SOAPAction [{1}]'.format(req_id,
                    soap_action))

            logger.log(TRACE1, '[{0}] service_store.services=[{1}]'.format(req_id,
                self.service_store.services))
            service_data = self.service_store.services.get(service_class_name)

            if not service_data:
                return server_soap_error(req_id, '[{0}] No service could handle SOAPAction [{1}]'.format(
                    req_id, soap_action))

            soap = objectify.fromstring(request)
            body = soap_body_xpath(soap)

            if not body:
                return client_soap_error('[{0}] Client did not send the [{1}] element'.format(
                    req_id, body_path))

            if self.wss_store.needs_wss(service_class_name):
                # Will raise an exception if anything goes wrong.
                self.wss_store.handle_request(service_class_name, service_data, soap)

            service_class = service_data['service_class']

            service_instance = service_class()
            service_instance.server = self.app_context.get_object('parallel_server')

            body_payload = ''#get_body_payload(body)

            service_response = service_instance.handle(payload=body_payload,
                    raw_request=request, channel='soap', thread_ctx=thread_ctx)

            # Responses from all Zato's interal services are wrapped in
            # in the <zato_message> element. Each one is also assigned the server's
            # public key.
            if isinstance(service_instance, AdminService):

                if logger.isEnabledFor(TRACE1):
                    logger.log(TRACE1, '[{0}] len(service_response)=[{1}]'.format(
                        req_id, len(service_response)))
                    for item in service_response:
                        logger.log(TRACE1, '[{0}] service_response item=[{1}]'.format(
                            req_id, item))

                result, rest = service_response
                if result == ZATO_OK:
                    details = ''
                    data = rest
                else:
                    details = rest
                    data = ''
                    
                response = zato_message.safe_substitute(req_id=req_id,
                    result=result, details=details, data=data)
            else:
                response = service_response

            response = soap_doc.safe_substitute(body=response)

            logger.debug('[{0}] Returning response=[{1}]'.format(
                req_id, response))
            return response

        except ClientSecurityException, e:
            # TODO: Rethink if any errors may be logged here.
            msg = '[{0}] [{1}]'.format(req_id, escape(format_exc()))
            logger.error(msg)
            return client_soap_error(req_id, e.args[0])

        except Exception, e:
            # TODO: Rethink if any errors may be logged here.
            msg = '[{0}] [{1}]'.format(req_id, escape(format_exc()))
            logger.error(msg)
            return server_soap_error(req_id, msg)
