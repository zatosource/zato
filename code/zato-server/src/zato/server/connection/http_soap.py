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
from httplib import BAD_REQUEST, FORBIDDEN, NOT_FOUND, responses
from string import Template
from threading import RLock
from traceback import format_exc

# lxml
from lxml import etree, objectify

# sec-wall
from secwall.server import on_basic_auth, on_wsse_pwd

# Zato
from zato.common import ClientSecurityException, HTTPException, soap_body_xpath, \
     ZATO_ERROR, ZATO_NONE, ZATO_OK, ZatoException, zato_ns_map
from zato.common.util import security_def_type, TRACE1
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
    def __init__(self, rid, msg, status):
        super(ClientHTTPError, self).__init__(rid, msg, status)
        
class BadRequest(ClientHTTPError):
    def __init__(self, rid, msg):
        super(BadRequest, self).__init__(rid, msg, BAD_REQUEST)
        
class Forbidden(ClientHTTPError):
    def __init__(self, rid, msg):
        super(Forbidden, self).__init__(rid, msg, FORBIDDEN)

class Security(object):
    """ Performs all the HTTP/SOAP-related security checks.
    """
    def __init__(self, url_sec={}, basic_auth_config={}, tech_acc_config={}, wss_config={}):
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.tech_acc_config = tech_acc_config
        self.wss_config = wss_config
        self.url_sec_lock = RLock()
                 
    def handle(self, rid, url_data, request_data, body, headers):
        """ Calls other concrete security methods as appropriate.
        """
        sec_def, sec_def_type = url_data.sec_def, url_data.sec_def.type
        
        handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
        getattr(self, handler_name)(rid, sec_def, request_data, body, headers)

    def _handle_security_basic_auth(self, rid, sec_def, request_data, body, headers):

        ba_config = self.basic_auth_config[sec_def.name]
        
        env = {'HTTP_AUTHORIZATION':headers['AUTHORIZATION']}
        url_config = {'basic-auth-username':ba_config.username, 'basic-auth-password':ba_config.password}
        
        result = on_basic_auth(env, url_config)
        
        if not result:
            msg = 'FORBIDDEN rid:[{0}], sec-wall code:[{1}], description:[{2}]\n'.format(
                rid, result.code, result.description)
            logger.error(msg)
            raise Forbidden(rid, msg)
        
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
        
# ##############################################################################
        
    def url_sec_get(self, url):
        """ Returns the security configuration of the given URL
        """
        with self.url_sec_lock:
            return self.url_sec.get(url)
        
# ##############################################################################        
        
    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition
        of the given name.
        """
        with self.basic_auth_lock:
            return self.basic_auth.get(name)

    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition
        """
        with self.basic_auth_lock:
            self.basic_auth[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.basic_auth_lock:
            del self.basic_auth[msg.old_name]
            self.basic_auth[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        with self.basic_auth_lock:
            del self.basic_auth[msg.name]
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        with self.basic_auth_lock:
            self.basic_auth[msg.name]['password'] = msg.password

# ##############################################################################

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        with self.tech_acc_lock:
            return self.tech_acc.get(name)

    def on_broker_pull_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        with self.tech_acc_lock:
            self.tech_acc[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        with self.tech_acc_lock:
            del self.tech_acc[msg.old_name]
            self.tech_acc[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        with self.tech_acc_lock:
            del self.tech_acc[msg.name]
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        with self.tech_acc_lock:
            # The message's 'password' attribute already takes the salt 
            # into account (pun intended ;-))
            self.tech_acc[msg.name]['password'] = msg.password
            
# ##############################################################################

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        with self.wss_lock:
            return self.wss.get(name)

    def on_broker_pull_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        with self.wss_lock:
            self.wss[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        with self.wss_lock:
            del self.wss[msg.old_name]
            self.wss[msg.name] = msg
        
    def on_broker_pull_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        with self.wss_lock:
            del self.wss[msg.name]
        
    def on_broker_pull_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        with self.wss_lock:
            # The message's 'password' attribute already takes the salt 
            # into account.
            self.wss[msg.name]['password'] = msg.password
            
# ##############################################################################

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
    
    def handle(self, rid, task, thread_ctx):
        """ Base method for handling incoming HTTP/SOAP messages. If the security
        configuration is one of the technical account or HTTP basic auth, 
        the security validation is being performed. Otherwise, that step 
        is postponed until a concrete transport-specific handler is invoked.
        """
        url_data = self.security.url_sec_get(task.request_data.uri)
        if url_data:
            
            transport = url_data['transport']
            
            try:
                request = task.request_data.getBodyStream().getvalue()
                headers = task.request_data.headers
                
                # No security at all for that URL.
                if url_data.sec_def != ZATO_NONE:
                    if url_data.sec_def.type in(security_def_type.tech_account, security_def_type.basic_auth):
                        self.security.handle(rid, url_data, task.request_data, request, headers)
                else:
                    log_msg = '[{0}] No security for URL [{1}]'.format(rid, task.request_data.uri)
                    logger.debug(log_msg)
                
                handler = getattr(self, '{0}_handler'.format(transport))
                return handler.handle(rid, request, headers, transport, thread_ctx)
            
            except ClientHTTPError, e:
                response = e.msg
                if transport == 'soap':
                    response = client_soap_error(rid, response)
                    
                task.setResponseStatus(e.status, e.reason)
                return response
        else:
            response = "[{0}] The URL [{1}] doesn't exist".format(rid, task.request_data.uri)
            task.setResponseStatus(NOT_FOUND, responses[NOT_FOUND])
            
            logger.error(response)
            return response
        
class _BaseMessageHandler(object):
    
    def init(self, rid, request, headers, transport):
        logger.debug('[{0}] request:[{1}] headers:[{2}]'.format(rid, request, headers))

        if transport == 'soap':
            # HTTP headers are all uppercased at this point.
            soap_action = headers.get('SOAPACTION')
    
            if not soap_action:
                raise BadRequest(rid, 'Client did not send the SOAPAction header')
    
            # SOAP clients may send an empty header, i.e. SOAPAction: "",
            # as opposed to not sending the header at all.
            soap_action = soap_action.lstrip('"').rstrip('"')
    
            if not soap_action:
                raise BadRequest(rid, 'Client sent an empty SOAPAction header')

        class_name = self.soap_config.get(soap_action)
        logger.debug('[{0}] class_name:[{1}]'.format(rid, class_name))

        if not class_name:
            raise BadRequest(rid, 'Unrecognized SOAPAction [{1}]'.format(soap_action))

        logger.log(TRACE1, '[{0}] service_store.services:[{1}]'.format(rid, self.service_store.services))
        service_data = self.service_store.service_data(class_name)

        soap = objectify.fromstring(request)
        body = soap_body_xpath(soap)

        if not body:
            raise BadRequest(rid, 'Client did not send the [{1}] element'.format(body_path))
        
        if transport == 'soap':
            payload = get_body_payload(body)
        else:
            payload = body
        
        return payload, class_name, service_data
    
    def handle_security(self):
        raise NotImplementedError('Must be implemented by subclasses')
    
    def handle(self, rid, request, headers, transport, thread_ctx):
        
        payload, class_name, service_data = self.init(rid, request, headers, transport)

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
        
class SOAPHandler(_BaseMessageHandler):
    """ Dispatches incoming SOAP messages to services.
    """
    def __init__(self, soap_config=None, service_store=None, wss_store=None, server=None):
        self.soap_config = soap_config
        self.service_store = service_store
        self.wss_store = wss_store
        self.server = server # A ParallelServer instance.
        
    def handle_security(self):
        if self.wss_store.needs_wss(class_name):
            # Will raise an exception if anything goes wrong.
            self.wss_store.handle_request(class_name, service_data, soap)

class PlainHTTPHandler(_BaseMessageHandler):
    """ Dispatches incoming plain HTTP messages to services.
    """
    def __init__(self, server=None):
        self.server = server # A ParallelServer instance.
        
    def handle(self, rid, request, headers, transport, thread_ctx):
        return super(PlainHTTPHandler, self).handle(rid, request, headers, transport, thread_ctx)
