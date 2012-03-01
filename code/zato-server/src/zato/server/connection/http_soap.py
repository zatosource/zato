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
from hashlib import sha256
from httplib import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from string import Template
from threading import RLock
from traceback import format_exc

# lxml
from lxml import objectify

# sec-wall
from secwall.server import on_basic_auth, on_wsse_pwd
from secwall.wsse import WSSE

# Zato
from zato.common import HTTPException, soap_body_xpath, ZATO_NONE, ZATO_OK
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

_reason_not_found = responses[NOT_FOUND]
_reason_internal_server_error = responses[INTERNAL_SERVER_ERROR]

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
        
class NotFound(ClientHTTPError):
    def __init__(self, rid, msg):
        super(NotFound, self).__init__(rid, msg, NOT_FOUND)

class Security(object):
    """ Performs all the HTTP/SOAP-related security checks.
    """
    def __init__(self, url_sec={}, basic_auth_config={}, tech_acc_config={}, wss_config={}):
        self.url_sec = url_sec
        self.basic_auth_config = basic_auth_config
        self.tech_acc_config = tech_acc_config
        self.wss_config = wss_config
        self.url_sec_lock = RLock()
        self._wss = WSSE()
                 
    def handle(self, rid, url_data, request_data, body, headers):
        """ Calls other concrete security methods as appropriate.
        """
        sec_def, sec_def_type = url_data.sec_def, url_data.sec_def.type
        
        handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
        getattr(self, handler_name)(rid, sec_def, request_data, body, headers)

    def _handle_security_basic_auth(self, rid, sec_def, request_data, body, headers):
        """ Performs the authentication using HTTP Basic Auth.
        """
        sec_config = self.basic_auth_config[sec_def.name]
        
        env = {'HTTP_AUTHORIZATION':headers.get('AUTHORIZATION')}
        url_config = {'basic-auth-username':sec_config.username, 'basic-auth-password':sec_config.password}
        
        result = on_basic_auth(env, url_config, False)
        
        if not result:
            msg = 'FORBIDDEN rid:[{0}], sec-wall code:[{1}], description:[{2}]\n'.format(
                rid, result.code, result.description)
            logger.error(msg)
            raise Forbidden(rid, msg)
        
    def _handle_security_wss(self, rid, sec_def, request_data, body, headers):
        """ Performs the authentication using WS-Security.
        """
        sec_config = self.wss_config[sec_def.name]
        
        url_config = {}
        
        if sec_config['password_type'] == 'clear_text':
            url_config['wsse-pwd-password'] = sec_config['password']
        else:
            url_config['wsse-pwd-password-digest'] = sec_config['password']
        
        url_config['wsse-pwd-username'] = sec_config['username']
        url_config['wsse-pwd-reject-empty-nonce-creation'] = sec_config['reject_empty_nonce_creat']
        url_config['wsse-pwd-reject-stale-tokens'] = sec_config['reject_stale_tokens']
        url_config['wsse-pwd-reject-expiry-limit'] = sec_config['reject_expiry_limit']
        url_config['wsse-pwd-nonce-freshness-time'] = sec_config['nonce_freshness_time']
        
        result = on_wsse_pwd(self._wss, url_config, body, False)
        
        if not result:
            msg = 'FORBIDDEN rid:[{0}], sec-wall code:[{1}], description:[{2}]\n'.format(
                rid, result.code, result.description)
            logger.error(msg)
            raise Forbidden(rid, msg)
        
    def _handle_security_tech_acc(self, rid, sec_def, request_data, body, headers):
        """ Performs the authentication using technical accounts.
        """
        zato_headers = ('X_ZATO_USER', 'X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                error_msg = ("[{0}] The header [{1}] doesn't exist or is empty, URI=[{2}, "
                      "headers=[{3}]]").\
                        format(rid, header, request_data.uri, headers)
                logger.error(error_msg)
                raise Forbidden(rid, error_msg)

        # Note that logs get a specific information what went wrong whereas the
        # user gets a generic 'username or password' message
        msg_template = '[{0}] The {1} is incorrect, URI:[{2}], X_ZATO_USER:[{3}]'

        if headers['X_ZATO_USER'] != sec_def.name:
            error_msg = msg_template.format(rid, 'username', request_data.uri, headers['X_ZATO_USER'])
            user_msg = msg_template.format(rid, 'username or password', request_data.uri, headers['X_ZATO_USER'])
            logger.error(error_msg)
            raise Forbidden(rid, user_msg)
        
        incoming_password = sha256(headers['X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            error_msg = msg_template.format(rid, 'password', request_data.uri, headers['X_ZATO_USER'])
            user_msg = msg_template.format(rid, 'username or password', request_data.uri, headers['X_ZATO_USER'])
            logger.error(error_msg)
            raise Forbidden(rid, user_msg)
        
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
                    if url_data.sec_def.type in(security_def_type.tech_account, security_def_type.basic_auth, 
                                                security_def_type.wss):
                        self.security.handle(rid, url_data, task.request_data, request, headers)
                    else:
                        log_msg = '[{0}] sec_def.type:[{1}] needs no auth'.format(rid, url_data.sec_def.type)
                        logger.debug(log_msg)
                else:
                    log_msg = '[{0}] No security for URL [{1}]'.format(rid, task.request_data.uri)
                    logger.debug(log_msg)
                
                handler = getattr(self, '{0}_handler'.format(transport))
                return handler.handle(rid, task, request, headers, transport, thread_ctx)

            except Exception, e:
                _format_exc = format_exc(e)
                if isinstance(e, ClientHTTPError):
                    response = e.msg
                    status = e.status
                    reason = e.reason
                else:
                    response = _format_exc
                    status = INTERNAL_SERVER_ERROR
                    reason = _reason_internal_server_error
                    
                # TODO: This should be configurable. Some people may want such
                # things to be on DEBUG whereas for others ERROR will make most sense
                # in given circumstances.
                if logger.isEnabledFor(logging.DEBUG):
                    msg = 'Caught an exception, rid:[{0}], status:[{1}], reason:[{2}], _format_exc:[{3}]'.format(
                        rid, status, reason, _format_exc)
                    logger.debug(msg)
                    
                if transport == 'soap':
                    response = client_soap_error(rid, response)
                    
                task.setResponseStatus(status, reason)
                return response
        else:
            response = "[{0}] The URL [{1}] doesn't exist".format(rid, task.request_data.uri)
            task.setResponseStatus(NOT_FOUND, _reason_not_found)
            
            logger.error(response)
            return response
        
class _BaseMessageHandler(object):
    
    def __init__(self, http_soap={}, server=None):
        self.http_soap = http_soap
        self.server = server # A ParallelServer instance.
    
    def init(self, rid, task, request, headers, transport):
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
        else:
            soap_action = None

        _soap_actions = self.http_soap.getall(task.request_data.uri)
        
        for _soap_action_info in _soap_actions:
            
            # TODO: Remove the call to .keys() when this pull request is merged in
            #       https://github.com/dsc/bunch/pull/4
            if soap_action in _soap_action_info.keys():
                _service_info = _soap_action_info[soap_action]
                break
        else:
            msg = '[{0}] Could not find the service config for URL:[{1}], SOAP action:[{2}]'.format(
                rid, task.request_data.uri, soap_action)
            logger.warn(msg)
            raise NotFound(rid, msg)

        logger.debug('[{0}] impl_name:[{1}]'.format(rid, _service_info.impl_name))

        logger.log(TRACE1, '[{0}] service_store.services:[{1}]'.format(rid, self.server.service_store.services))
        service_data = self.server.service_store.service_data(_service_info.impl_name)

        if transport == 'soap':
            soap = objectify.fromstring(request)
            body = soap_body_xpath(soap)
    
            if not body:
                raise BadRequest(rid, 'Client did not send the [{1}] element'.format(body_path))
            payload = get_body_payload(body)
        else:
            payload = request
        
        return payload, _service_info.impl_name, service_data
    
    def handle_security(self):
        raise NotImplementedError('Must be implemented by subclasses')
    
    def handle(self, rid, task, request, headers, transport, thread_ctx):
        
        payload, impl_name, service_data = self.init(rid, task, request, headers, transport)

        service_instance = self.server.service_store.new_instance(impl_name)
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
    def __init__(self, http_soap=None, server=None):
        super(SOAPHandler, self).__init__(http_soap, server)
        
    def handle_security(self):
        if self.wss_store.needs_wss(class_name):
            # Will raise an exception if anything goes wrong.
            self.wss_store.handle_request(class_name, service_data, soap)

class PlainHTTPHandler(_BaseMessageHandler):
    """ Dispatches incoming plain HTTP messages to services.
    """
    def __init__(self, http_soap=None, server=None):
        super(PlainHTTPHandler, self).__init__(http_soap, server)
        
    def handle(self, rid, task, request, headers, transport, thread_ctx):
        return super(PlainHTTPHandler, self).handle(rid, task, request, headers, transport, thread_ctx)
