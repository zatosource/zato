# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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

# stdlib
import logging, time
from cgi import escape
from hashlib import sha256
from httplib import FORBIDDEN, NOT_FOUND, responses
from string import Template
from traceback import format_exc

# lxml
from lxml import etree, objectify

# Zato
from zato.common import ClientSecurityException, HTTPException, soap_body_xpath, \
     ZATO_ERROR, ZATO_NONE, ZATO_OK, ZatoException, zato_ns_map
from zato.common.util import TRACE1
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

soap_doc = Template("""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>$body</soap:Body></soap:Envelope>""")
zato_message = Template("""
<zato_message xmlns="http://gefira.pl/zato">
    <data>$data</data>
    <zato_env>
        <result>$result</result>
        <rid>$rid</rid>
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
     <faultstring>[$rid] $faultstring</faultstring>
      </SOAP-ENV:Fault>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>""")

def get_body_payload(body):
    body_children_count = body[0].countchildren()

    if body_children_count == 0:
        body_payload = None
    elif body_children_count == 1:
        body_payload = body[0].getchildren()[0]
    else:
        body_payload = body[0].getchildren()

    return body_payload

def client_soap_error(rid, faultstring):
    return soap_error.safe_substitute(faultcode='Client', rid=rid, faultstring=faultstring)

def server_soap_error(rid, faultstring):
    return soap_error.safe_substitute(faultcode='Server', rid=rid, faultstring=faultstring)

class ClientHTTPError(HTTPException):
    def __init__(self, rid, msg):
        super(ClientSOAPError, self).__init__(rid, msg, BAD_REQUEST)

class Security(object):
    """ Performs all the HTTP/SOAP-related security checks.
    """
    def handle(self, rid, url_data, request_data, body, headers):
        """ Calls other concrete security methods as appropriate.
        """
        
        # No security at all for that URL.
        if url_data.sec_def == ZATO_NONE:
            return True
        
        sec_def, sec_def_type = url_data.sec_def, url_data.sec_def.type
        
        handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
        getattr(self, handler_name)(rid, sec_def, request_data, body, headers)
    
    def _handle_security_tech_acc(self, rid, sec_def, request_data, body, headers):
        """ Handles the 'tech_acc' security config type.
        """
        zato_headers = ('X_ZATO_USER', 'X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                error_msg = ("[{0}] The header [{1}] doesn't exist or is empty, URI=[{2}, "
                      "headers=[{3}]]").\
                        format(rid, header, request_data.uri, headers)
                logger.error(error_msg)
                raise HTTPException(rid, error_msg, FORBIDDEN)

        msg_template = '[{0}] The {1} is incorrect, URI:[{2}], X_ZATO_USER:[{3}]'

        if headers['X_ZATO_USER'] != sec_def.name:
            error_msg = msg_template.format(rid, 'username', request_data.uri, headers['X_ZATO_USER'])
            logger.error(error_msg)
            raise HTTPException(rid, error_msg, FORBIDDEN)
        
        incoming_password = sha256(headers['X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            error_msg = msg_template.format(rid, 'password', request_data.uri, headers['X_ZATO_USER'])
            logger.error(error_msg)
            raise HTTPException(rid, error_msg, FORBIDDEN)

class RequestHandler(object):
    """ Handles all the incoming HTTP/SOAP requests.
    """
    def __init__(self, security=None, soap_handler=None, plain_http_handler=None):
        self.security = security
        self.soap_handler = soap_handler
        self.plain_http_handler = plain_http_handler
        
    def wrap_error_message(self, rid, url_type, msg):
        """ Wraps an error message in a transport-specific envelope.
        """
        if url_type == ZATO_URL_TYPE_SOAP:
            return server_soap_error(rid, msg)
        
        # Let's return the message as-is if we don't have any specific envelope
        # to use.
        return msg        
    
    def handle(self, rid, url_data, task, thread_ctx):
        if url_data:
            
            transport = url_data['transport']
            
            try:
                request = task.request_data.getBodyStream().getvalue()
                headers = task.request_data.headers            
                
                self.security.handle(rid, url_data, task.request_data, request, headers)
                
                # TODO: Shadow out any passwords that may be contained in HTTP
                # headers or in the message itself. Of course, that only applies
                # to auth schemes we're aware of (HTTP Basic Auth, WSS etc.)
                
                handler = getattr(self, '{0}_handler'.format(transport))
                return handler.handle(rid, request, headers, transport, thread_ctx)
            
            except ClientHTTPError, e:
                if transport == 'soap':
                    response = client_soap_error(rid, format_exc(e))
                else:
                    raise ZatoException('Unrecognized transport:[{0}]'.format(transport))
        
            #except HTTPException, e:
            #    task.setResponseStatus(e.status, responses[e.status])
            #    response = wrap_error_message(rid, transport, e.reason)        

        else:
            msg = "[{0}] The URL [{1}] doesn't exist".format(rid, task.request_data.uri)
            task.setResponseStatus(NOT_FOUND, responses[NOT_FOUND])
            
            logger.error(msg)
            return msg
        
class _BaseMessageHandler(object):
    
    def init(self, rid, request, headers, transport):
        logger.debug('[{0}] request:[{1}] headers:[{2}]'.format(rid, request, headers))

        # HTTP headers are all uppercased at this point.
        soap_action = headers.get('SOAPACTION')

        if not soap_action:
            raise ClientHTTPError(rid, 'Client did not send the SOAPAction header')

        # SOAP clients may send an empty header, i.e. SOAPAction: "",
        # as opposed to not sending the header at all.
        soap_action = soap_action.lstrip('"').rstrip('"')

        if not soap_action:
            raise ClientHTTPError(rid, 'Client sent an empty SOAPAction header')

        class_name = self.soap_config.get(soap_action)
        logger.debug('[{0}] class_name:[{1}]'.format(rid, class_name))

        if not class_name:
            raise ClientHTTPError(rid, 'Unrecognized SOAPAction [{1}]'.format(soap_action))

        logger.log(TRACE1, '[{0}] service_store.services:[{1}]'.format(rid, self.service_store.services))
        service_data = self.service_store.service_data(class_name)

        soap = objectify.fromstring(request)
        body = soap_body_xpath(soap)

        if not body:
            raise ClientHTTPError(rid, 'Client did not send the [{1}] element'.format(body_path))
        
        if transport == 'soap':
            payload = get_body_payload(body)
        else:
            payload = body
        
        return payload, class_name, service_data
    
    def handle_security(self):
        pass
    
    def invoke_service(self):
        pass
    
    def return_response(self):
        pass

    def handle(self, rid, request, headers, transport, thread_ctx):
        
        try:
            payload, class_name, service_data = self.init(rid, request, headers, transport)

            if self.wss_store.needs_wss(class_name):
                # Will raise an exception if anything goes wrong.
                self.wss_store.handle_request(class_name, service_data, soap)
                
            service_instance = self.service_store.new_instance(class_name)
            service_instance.update(service_instance, self.server, thread_ctx.broker_client, transport, rid)

            service_response = service_instance.handle(payload=payload, raw_request=request, transport=transport, thread_ctx=thread_ctx)

            # Responses from all Zato's interal services are wrapped in
            # in the <zato_message> element. Each one is also assigned the server's
            # public key.
            if isinstance(service_instance, AdminService):

                if logger.isEnabledFor(TRACE1):
                    logger.log(TRACE1, '[{0}] len(service_response)=[{1}]'.format(rid, len(service_response)))
                    for item in service_response:
                        logger.log(TRACE1, '[{0}] service_response item=[{1}]'.format(rid, item))

                result, rest = service_response
                if result == ZATO_OK:
                    details = ''
                    data = rest
                else:
                    details = rest
                    data = ''
                    
                response = zato_message.safe_substitute(rid=rid, result=result, details=details, data=data)
            else:
                response = service_response

            if transport == 'soap':
                response = soap_doc.safe_substitute(body=response)

            logger.debug('[{0}] Returning response=[{1}]'.format(rid, response))
            return response

        except ClientSecurityException, e:
            # TODO: Rethink if any errors may be logged here.
            msg = '[{0}] [{1}]'.format(rid, escape(format_exc()))
            logger.error(msg)
            return client_soap_error(rid, e.args[0])

        except Exception, e:
            # TODO: Rethink if any errors may be logged here.
            msg = '[{0}] [{1}]'.format(rid, escape(format_exc()))
            logger.error(msg)
            return server_soap_error(rid, msg)
        
class SOAPHandler(_BaseMessageHandler):
    """ Dispatches incoming SOAP messages to services.
    """
    def __init__(self, soap_config=None, service_store=None, wss_store=None, server=None):
        self.soap_config = soap_config
        self.service_store = service_store
        self.wss_store = wss_store
        self.server = server # A ParalleServer instance.

class PlainHTTPHandler(_BaseMessageHandler):
    """ Dispatches incoming plain HTTP messages to services.
    """
    def __init__(self, server=None):
        self.server = server
        
    def handle(self, rid, request, headers, transport, thread_ctx):
        return 'ZZZ'