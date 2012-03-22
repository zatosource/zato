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
import logging
from copy import deepcopy
from cStringIO import StringIO
from datetime import datetime
from hashlib import sha256
from httplib import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from string import Template
from threading import RLock
from traceback import format_exc
from uuid import uuid4

# lxml
from lxml import objectify

# Requests
import requests

# anyjson
from anyjson import loads

# Bunch
from bunch import Bunch

# sec-wall
from secwall.server import on_basic_auth, on_wsse_pwd
from secwall.wsse import WSSE

# Zato
from zato.common import HTTPException, SIMPLE_IO, soap_body_xpath, url_type, ZATO_NONE, ZATO_OK
from zato.common.util import security_def_type, TRACE1
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

soap_doc = Template("""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>$body</soap:Body></soap:Envelope>""")
zato_message = Template("""
<zato_message xmlns="http://gefira.pl/zato">
    <data>$data</data>
    <zato_env>
        <result>$result</result>
        <cid>$cid</cid>
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
     <faultstring>[$cid] $faultstring</faultstring>
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

def client_soap_error(cid, faultstring):
    return soap_error.safe_substitute(faultcode='Client', cid=cid, faultstring=faultstring)

def server_soap_error(cid, faultstring):
    return soap_error.safe_substitute(faultcode='Server', cid=cid, faultstring=faultstring)

class ClientHTTPError(HTTPException):
    def __init__(self, cid, msg, status):
        super(ClientHTTPError, self).__init__(cid, msg, status)
        
class BadRequest(ClientHTTPError):
    def __init__(self, cid, msg):
        super(BadRequest, self).__init__(cid, msg, BAD_REQUEST)
        
class Forbidden(ClientHTTPError):
    def __init__(self, cid, msg):
        super(Forbidden, self).__init__(cid, msg, FORBIDDEN)
        
class NotFound(ClientHTTPError):
    def __init__(self, cid, msg):
        super(NotFound, self).__init__(cid, msg, NOT_FOUND)

class Security(object):
    """ Performs all the HTTP/SOAP-related security checks.
    """
    def __init__(self, url_sec=None, basic_auth_config=None, tech_acc_config=None,
                 wss_config=None):
        self.url_sec = url_sec 
        self.basic_auth_config = basic_auth_config
        self.tech_acc_config = tech_acc_config
        self.wss_config = wss_config
        self.url_sec_lock = RLock()
        self._wss = WSSE()
                 
    def handle(self, cid, url_data, request_data, body, headers):
        """ Calls other concrete security methods as appropriate.
        """
        sec_def, sec_def_type = url_data.sec_def, url_data.sec_def.sec_type
        
        handler_name = '_handle_security_{0}'.format(sec_def_type.replace('-', '_'))
        getattr(self, handler_name)(cid, sec_def, request_data, body, headers)

    def _handle_security_basic_auth(self, cid, sec_def, request_data, body, headers):
        """ Performs the authentication using HTTP Basic Auth.
        """
        env = {'HTTP_AUTHORIZATION':headers.get('AUTHORIZATION')}
        url_config = {'basic-auth-username':sec_def.username, 'basic-auth-password':sec_def.password}
        
        result = on_basic_auth(env, url_config, False)
        
        if not result:
            msg = 'FORBIDDEN cid:[{0}], sec-wall code:[{1}], description:[{2}]\n'.format(
                cid, result.code, result.description)
            logger.error(msg)
            raise Forbidden(cid, msg)
        
    def _handle_security_wss(self, cid, sec_def, request_data, body, headers):
        """ Performs the authentication using WS-Security.
        """
        url_config = {}
        
        url_config['wsse-pwd-password'] = sec_def['password']
        url_config['wsse-pwd-username'] = sec_def['username']
        url_config['wsse-pwd-reject-empty-nonce-creation'] = sec_def['reject_empty_nonce_creat']
        url_config['wsse-pwd-reject-stale-tokens'] = sec_def['reject_stale_tokens']
        url_config['wsse-pwd-reject-expiry-limit'] = sec_def['reject_expiry_limit']
        url_config['wsse-pwd-nonce-freshness-time'] = sec_def['nonce_freshness_time']
        
        result = on_wsse_pwd(self._wss, url_config, body, False)
        
        if not result:
            msg = 'FORBIDDEN cid:[{0}], sec-wall code:[{1}], description:[{2}]\n'.format(
                cid, result.code, result.description)
            logger.error(msg)
            raise Forbidden(cid, msg)
        
    def _handle_security_tech_acc(self, cid, sec_def, request_data, body, headers):
        """ Performs the authentication using technical accounts.
        """
        zato_headers = ('X_ZATO_USER', 'X_ZATO_PASSWORD')
        
        for header in zato_headers:
            if not headers.get(header, None):
                error_msg = ("[{0}] The header [{1}] doesn't exist or is empty, URI=[{2}, "
                      "headers=[{3}]]").\
                        format(cid, header, request_data.uri, headers)
                logger.error(error_msg)
                raise Forbidden(cid, error_msg)

        # Note that logs get a specific information what went wrong whereas the
        # user gets a generic 'username or password' message
        msg_template = '[{0}] The {1} is incorrect, URI:[{2}], X_ZATO_USER:[{3}]'

        if headers['X_ZATO_USER'] != sec_def.name:
            error_msg = msg_template.format(cid, 'username', request_data.uri, headers['X_ZATO_USER'])
            user_msg = msg_template.format(cid, 'username or password', request_data.uri, headers['X_ZATO_USER'])
            logger.error(error_msg)
            raise Forbidden(cid, user_msg)
        
        incoming_password = sha256(headers['X_ZATO_PASSWORD'] + ':' + sec_def.salt).hexdigest()
        
        if incoming_password != sec_def.password:
            error_msg = msg_template.format(cid, 'password', request_data.uri, headers['X_ZATO_USER'])
            user_msg = msg_template.format(cid, 'username or password', request_data.uri, headers['X_ZATO_USER'])
            logger.error(error_msg)
            raise Forbidden(cid, user_msg)
        
# ##############################################################################
        
    def url_sec_get(self, url):
        """ Returns the security configuration of the given URL
        """
        with self.url_sec_lock:
            return self.url_sec.get(url)
        
    def _update_url_sec(self, msg, sec_def_type, delete=False):
        """ Updates URL security definitions that use the security configuration
        of the name and type given in 'msg' so that existing definitions use 
        the new configuration or, optionally, deletes the URL security definition
        altogether if 'delete' is True.
        """
        for sec_def_name, sec_def_value in self.url_sec.items():
            sec_def = sec_def_value.sec_def
            if sec_def != ZATO_NONE and sec_def.type == sec_def_type:
                name = msg.get('old_name') if msg.get('old_name') else msg.get('name')
                if sec_def.name == name:
                    if delete:
                        del self.url_sec[sec_def_name]
                    else:
                        for key, new_value in msg.items():
                            if key in sec_def:
                                sec_def[key] = msg[key]

# ##############################################################################

    def _update_basic_auth(self, name, config):
        if name in self.basic_auth_config:
            self.basic_auth_config[name].clear()
            
        self.basic_auth_config[name] = Bunch()
        self.basic_auth_config[name].config = config

    def basic_auth_get(self, name):
        """ Returns the configuration of the HTTP Basic Auth security definition
        of the given name.
        """
        with self.url_sec_lock:
            return self.basic_auth_config.get(name)

    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CREATE(self, msg, *args):
        """ Creates a new HTTP Basic Auth security definition
        """
        with self.url_sec_lock:
            self._update_basic_auth(msg.name, msg)
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_EDIT(self, msg, *args):
        """ Updates an existing HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            del self.basic_auth_config[msg.old_name]
            self._update_basic_auth(msg.name, msg)
            self._update_url_sec(msg, security_def_type.basic_auth)
            
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_DELETE(self, msg, *args):
        """ Deletes an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            del self.basic_auth_config[msg.name]
            self._update_url_sec(msg, security_def_type.basic_auth, True)
        
    def on_broker_pull_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg, *args):
        """ Changes password of an HTTP Basic Auth security definition.
        """
        with self.url_sec_lock:
            self.basic_auth_config[msg.name]['config']['password'] = msg.password
            self._update_url_sec(msg, security_def_type.basic_auth)

# ##############################################################################

    def _update_tech_acc(self, name, config):
        if name in self.tech_acc_config:
            self.tech_acc_config[name].clear()
            
        self.tech_acc_config[name] = Bunch()
        self.tech_acc_config[name].config = config

    def tech_acc_get(self, name):
        """ Returns the configuration of the technical account of the given name.
        """
        with self.url_sec_lock:
            return self.tech_acc_config.get(name)

    def on_broker_pull_msg_SECURITY_TECH_ACC_CREATE(self, msg, *args):
        """ Creates a new technical account.
        """
        with self.url_sec_lock:
            self._update_tech_acc(msg.name, msg)
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_EDIT(self, msg, *args):
        """ Updates an existing technical account.
        """
        with self.url_sec_lock:
            del self.tech_acc_config[msg.old_name]
            self._update_tech_acc(msg.name, msg)
            self._update_url_sec(msg, security_def_type.tech_account)
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_DELETE(self, msg, *args):
        """ Deletes a technical account.
        """
        with self.url_sec_lock:
            del self.tech_acc_config[msg.name]
            self._update_url_sec(msg, security_def_type.tech_account, True)
        
    def on_broker_pull_msg_SECURITY_TECH_ACC_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a technical account.
        """
        with self.url_sec_lock:
            # The message's 'password' attribute already takes the salt 
            # into account (pun intended ;-))
            self.tech_acc_config[msg.name]['password'] = msg.password
            self._update_url_sec(msg, security_def_type.tech_account)
            
# ##############################################################################

    def _update_wss(self, name, config):
        if name in self.wss_config:
            self.wss_config[name].clear()
            
        self.wss_config[name] = Bunch()
        self.wss_config[name].config = config

    def wss_get(self, name):
        """ Returns the configuration of the WSS definition of the given name.
        """
        with self.url_sec_lock:
            return self.wss_config.get(name)

    def on_broker_pull_msg_SECURITY_WSS_CREATE(self, msg, *args):
        """ Creates a new WS-Security definition.
        """
        with self.url_sec_lock:
            self._update_wss(msg.name, msg)
        
    def on_broker_pull_msg_SECURITY_WSS_EDIT(self, msg, *args):
        """ Updates an existing WS-Security definition.
        """
        with self.url_sec_lock:
            del self.wss_config[msg.old_name]
            self._update_wss(msg.name, msg)
            self._update_url_sec(msg, security_def_type.wss)
        
    def on_broker_pull_msg_SECURITY_WSS_DELETE(self, msg, *args):
        """ Deletes a WS-Security definition.
        """
        with self.url_sec_lock:
            del self.wss_config[msg.name]
            self._update_url_sec(msg, security_def_type.wss, True)
        
    def on_broker_pull_msg_SECURITY_WSS_CHANGE_PASSWORD(self, msg, *args):
        """ Changes the password of a WS-Security definition.
        """
        with self.url_sec_lock:
            # The message's 'password' attribute already takes the salt 
            # into account.
            self.wss_config[msg.name]['password'] = msg.password
            self._update_url_sec(msg, security_def_type.wss)
            
# ##############################################################################

    def on_broker_pull_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Creates or updates an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            old_url_path = msg.get('old_url_path')
            if msg.sec_type:
                sec_def_dict = getattr(self, msg.sec_type + '_config')
                sec_def = deepcopy(sec_def_dict[msg.security_name].config)
            else:
                sec_def = ZATO_NONE
                
            if old_url_path in self.url_sec:
                del self.url_sec[old_url_path]
                
            self.url_sec[msg.url_path] = Bunch()
            self.url_sec[msg.url_path].sec_def = sec_def
            self.url_sec[msg.url_path].transport = msg.transport
            self.url_sec[msg.url_path].data_format = msg.data_format
            
    def on_broker_pull_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        with self.url_sec_lock:
            raise NotImplementedError()

# ##############################################################################

class RequestHandler(object):
    """ Handles all the incoming HTTP/SOAP requests.
    """
    def __init__(self, security=None, soap_handler=None, plain_http_handler=None,
                 simple_io_config=None):
        self.security = security
        self.soap_handler = soap_handler
        self.plain_http_handler = plain_http_handler
        self.simple_io_config = simple_io_config
        
    def wrap_error_message(self, cid, url_type, msg):
        """ Wraps an error message in a transport-specific envelope.
        """
        if url_type == ZATO_URL_TYPE_SOAP:
            return server_soap_error(cid, msg)
        
        # Let's return the message as-is if we don't have any specific envelope
        # to use.
        return msg        
    
    def handle(self, cid, task, thread_ctx):
        """ Base method for handling incoming HTTP/SOAP messages. If the security
        configuration is one of the technical account or HTTP basic auth, 
        the security validation is being performed. Otherwise, that step 
        is postponed until a concrete transport-specific handler is invoked.
        """
        url_data = self.security.url_sec_get(task.request_data.uri)

        if url_data:
            
            transport = url_data['transport']
            
            try:
                payload = task.request_data.getBodyStream().getvalue()
                headers = task.request_data.headers
                
                # No security at all for that URL.
                if url_data.sec_def != ZATO_NONE:
                    if url_data.sec_def.sec_type in(security_def_type.tech_account, security_def_type.basic_auth, 
                                                security_def_type.wss):
                        self.security.handle(cid, url_data, task.request_data, payload, headers)
                    else:
                        log_msg = '[{0}] sec_def.sec_type:[{1}] needs no auth'.format(cid, url_data.sec_def.sec_type)
                        logger.debug(log_msg)
                else:
                    log_msg = '[{0}] No security for URL [{1}]'.format(cid, task.request_data.uri)
                    logger.debug(log_msg)
                
                handler = getattr(self, '{0}_handler'.format(transport))

                response = handler.handle(cid, task, payload, headers, transport, thread_ctx, 
                    self.simple_io_config, url_data['data_format'])
                task.response_headers['Content-Type'] = response.content_type
          
                return response.payload

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
                    msg = 'Caught an exception, cid:[{0}], status:[{1}], reason:[{2}], _format_exc:[{3}]'.format(
                        cid, status, reason, _format_exc)
                    logger.debug(msg)
                    
                if transport == 'soap':
                    response = client_soap_error(cid, response)
                    
                task.setResponseStatus(status, reason)
                return response
        else:
            response = "[{0}] The URL [{1}] doesn't exist".format(cid, task.request_data.uri)
            task.setResponseStatus(NOT_FOUND, _reason_not_found)
            
            logger.error(response)
            return response
        
class _BaseMessageHandler(object):
    
    def __init__(self, http_soap={}, server=None):
        self.http_soap = http_soap
        self.server = server # A ParallelServer instance
    
    def init(self, cid, task, request, headers, transport, data_format):
        logger.debug('[{0}] request:[{1}] headers:[{2}]'.format(cid, request, headers))

        if transport == 'soap':
            # HTTP headers are all uppercased at this point.
            soap_action = headers.get('SOAPACTION')
    
            if not soap_action:
                raise BadRequest(cid, 'Client did not send the SOAPAction header')
    
            # SOAP clients may send an empty header, i.e. SOAPAction: "",
            # as opposed to not sending the header at all.
            soap_action = soap_action.lstrip('"').rstrip('"')
    
            if not soap_action:
                raise BadRequest(cid, 'Client sent an empty SOAPAction header')
        else:
            soap_action = ''

        _soap_actions = self.http_soap.getall(task.request_data.uri)
        
        for _soap_action_info in _soap_actions:
            
            # TODO: Remove the call to .keys() when this pull request is merged in
            #       https://github.com/dsc/bunch/pull/4
            if soap_action in _soap_action_info.keys():
                _service_info = _soap_action_info[soap_action]
                break
        else:
            msg = '[{0}] Could not find the service config for URL:[{1}], SOAP action:[{2}]'.format(
                cid, task.request_data.uri, soap_action)
            logger.warn(msg)
            raise NotFound(cid, msg)

        logger.debug('[{0}] impl_name:[{1}]'.format(cid, _service_info.impl_name))

        logger.log(TRACE1, '[{0}] service_store.services:[{1}]'.format(cid, self.server.service_store.services))
        service_data = self.server.service_store.service_data(_service_info.impl_name)

        if data_format == SIMPLE_IO.FORMAT.XML:
            if transport == 'soap':
                soap = objectify.fromstring(request)
                body = soap_body_xpath(soap)
                if not body:
                    raise BadRequest(cid, 'Client did not send the [{1}] element'.format(body_path))
                payload = get_body_payload(body)
            else:
                payload = objectify.fromstring(request)
        elif data_format == SIMPLE_IO.FORMAT.JSON:
            payload = loads(request)
        else:
            payload = request
        
        return payload, _service_info.impl_name, service_data
    
    def handle_security(self):
        raise NotImplementedError('Must be implemented by subclasses')
    
    def handle(self, cid, task, raw_request, headers, transport, thread_ctx, simple_io_config, data_format):
        payload, impl_name, service_data = self.init(cid, task, raw_request, headers, transport, data_format)

        service_instance = self.server.service_store.new_instance(impl_name)
        service_instance.update(service_instance, self.server, thread_ctx.broker_client, 
            thread_ctx.store, cid, payload, raw_request, transport, simple_io_config,
            data_format)

        service_instance.handle()
        response = service_instance.response
        if not isinstance(response.payload, basestring):
            response.payload = response.payload.getvalue()

        if isinstance(service_instance, AdminService) and data_format == SIMPLE_IO.FORMAT.XML:
            response.payload = zato_message.safe_substitute(cid=service_instance.cid, 
                result=response.result, details=response.result_details, data=response.payload)

        if transport == 'soap':
            response.payload = soap_doc.safe_substitute(body=response.payload)

        logger.debug('[{0}] Returning response=[{1}]'.format(cid, response.payload))
        return response
    
    def on_broker_pull_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Updates the configuration so that there's a link between a URL
        and a SOAP method to a service.
        """
        old_url_path = msg.get('old_url_path')
        old_soap_action = msg.get('old_soap_action', '')
        
        # A plain HTTP channel has always one SOAP action, the dummy empty one ''
        # so we can just quickly recreate it from scratch
        if msg.transport == url_type.plain_http:
            soap_action = ''
            if old_url_path in self.http_soap:
                del self.http_soap[old_url_path]
        else:
            soap_action = msg.soap_action
            
            # Delete the old SOAP action if it existed at all and then find out
            # whether that was the only SOAP action attached to the URL. If it was,
            # delete the URL as well.
            if old_url_path in self.http_soap:
                if old_soap_action in self.http_soap[old_url_path]:
                    del self.http_soap[old_url_path][old_soap_action]
                if not self.http_soap[old_url_path]:
                    del self.http_soap[old_url_path]
                
        url_path_bunch = self.http_soap.setdefault(msg.url_path, Bunch())
        soap_action_bunch = url_path_bunch.setdefault(soap_action, Bunch())

        for name in('id', 'impl_name', 'is_internal', 'method', 'name',
                    'service_id', 'service_name', 'soap_version', 'url_path'):
            soap_action_bunch[name] = msg[name]
            
    def on_broker_pull_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        raise NotImplementedError()
        
class SOAPHandler(_BaseMessageHandler):
    """ Dispatches incoming SOAP messages to services.
    """
    def __init__(self, http_soap=None, server=None):
        super(SOAPHandler, self).__init__(http_soap, server)

class PlainHTTPHandler(_BaseMessageHandler):
    """ Dispatches incoming plain HTTP messages to services.
    """
    def __init__(self, http_soap=None, server=None):
        super(PlainHTTPHandler, self).__init__(http_soap, server)

class HTTPSOAPWrapper(object):
    """ A thin wrapper around the API exposed by the 'requests' package.
    """
    def __init__(self, config):
        self.config = config
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.requests_module = requests
        self.session = self.requests_module.session()
        
        self.soap = {}
        self.soap['1.1'] = {}
        self.soap['1.1']['content_type'] = 'text/xml; charset=utf-8'
        self.soap['1.1']['message'] = """<?xml version="1.0" encoding="utf-8"?>
<s11:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  {header}
  <s11:Body>{data}</s11:Body>
</s11:Envelope>"""
        self.soap['1.1']['header_template'] = """<s11:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" >
          <wsse:Security>
            <wsse:UsernameToken>
              <wsse:Username>{Username}</wsse:Username>
              <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{Password}</wsse:Password>
            </wsse:UsernameToken>
          </wsse:Security>
        </s11:Header>
        """

        self.soap['1.2'] = {}
        self.soap['1.2']['content_type'] = 'application/soap+xml; charset=utf-8'
        self.soap['1.2']['message'] = """<?xml version="1.0" encoding="utf-8"?>
<s12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  {header}
  <s12:Body></s12:Body>
</s12:Envelope>"""
        self.soap['1.2']['header_template'] = """<s12:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" >
          <wsse:Security>
            <wsse:UsernameToken>
              <wsse:Username>{Username}</wsse:Username>
              <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{Password}</wsse:Password>
            </wsse:UsernameToken>
          </wsse:Security>
        </s12:Header>
        """
        
        self.set_auth()
        
    def set_auth(self):
        """ Configures the security for requests, if any is to be configured at all.
        """
        self.requests_auth = self.auth if self.config['sec_type'] == security_def_type.basic_auth else None
        if self.config['sec_type'] == security_def_type.wss:
            self.soap[self.config['soap_version']]['header'] = self.soap[self.config['soap_version']]['header_template'].format(
                Username=self.config['username'], Password=self.config['password'])
        
    def __str__(self):
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)
    
    __repr__ = __str__
    
    def _impl(self):
        """ Returns the self.session object through which access to HTTP/SOAP
        resources is mediated.
        """
        return self.session

    impl = property(fget=_impl, doc=_impl.__doc__)
    
    def _get_auth(self):
        """ Returns a username and password pair or None, if no security definition
        has been attached.
        """
        if self.config['sec_type'] in(security_def_type.basic_auth, security_def_type.wss):
            auth = (self.config['username'], self.config['password'])
        else:
            auth = None
            
        return auth
    
    auth = property(fget=_get_auth, doc=_get_auth)
    
    def ping(self, cid):
        """ Pings a given HTTP/SOAP resource
        """
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'About to ping:[{}]'.format(self.config_no_sensitive)
            logger.debug(msg)
         
        # session will write some info to it ..
        verbose = StringIO()
        
        start = datetime.now()
        
        # .. invoke the other end ..
        r = self.session.head(self.config['address'], auth=self.requests_auth, prefetch=True,
                config={'verbose':verbose}, headers={'X-Zato-CID':cid})
        
        # .. store additional info, get and close the stream.
        verbose.write('Code: {}'.format(r.status_code))
        verbose.write('\nResponse time: {}'.format(datetime.now() - start))
        value = verbose.getvalue()
        verbose.close()
        
        return value
    
    def get(self, cid, params=None, prefetch=True, *args, **kwargs):
        """ Invokes a resource using the GET method.
        """
        headers = kwargs.pop('headers', {})
        if not 'X-Zato-CID' in headers:
            headers['X-Zato-CID'] = cid

        return self.session.get(self.config['address'], params=params or {}, 
            prefetch=prefetch, auth=self.requests_auth, *args, **kwargs)
    
    def _soap_data(self, data, headers):
        """ Wraps the data in a SOAP-specific messages and adds the headers required.
        """
        soap_config = self.soap[self.config['soap_version']]
        
        # The idea here is that even though there usually won't be the Content-Type
        # header provided by the user, we shouldn't overwrite it if one has been
        # actually passed in.
        if not headers.get('Content-Type'):
            headers['Content-Type'] = soap_config['content_type']
            
        if self.config['sec_type'] == security_def_type.wss:
            soap_header = soap_config['header']
        else:
            soap_header = ''
            
        return soap_config['message'].format(header=soap_header, data=data), headers
    
    def post(self, cid, data='', prefetch=True, *args, **kwargs):
        """ Invokes a resource using the POST method.
        """
        if self.config['transport'] == 'soap':
            data, headers = self._soap_data(data, kwargs.pop('headers', {}))
            
        if not 'X-Zato-CID' in headers:
            headers['X-Zato-CID'] = cid

        return self.session.post(self.config['address'], data=data, 
            prefetch=prefetch, auth=self.requests_auth, headers=headers, *args, **kwargs)
    
    send = post
