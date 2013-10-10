# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from cStringIO import StringIO
from httplib import INTERNAL_SERVER_ERROR, NOT_FOUND, responses, UNAUTHORIZED
from pprint import pprint
from traceback import format_exc

# anyjson
from anyjson import dumps

# Bunch
from bunch import Bunch

# Zato
from zato.common import CHANNEL, SIMPLE_IO, URL_TYPE, zato_namespace, ZATO_ERROR, ZATO_NONE, ZATO_OK
from zato.common.util import payload_from_request, security_def_type, TRACE1
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, \
     NotFound, Unauthorized
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

_status_internal_server_error = b'{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
_status_not_found = b'{} {}'.format(NOT_FOUND, responses[NOT_FOUND])
_status_unauthorized = b'{} {}'.format(UNAUTHORIZED, responses[UNAUTHORIZED])

soap_doc = b"""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="https://zato.io/ns/20130518"><soap:Body>{body}</soap:Body></soap:Envelope>"""

zato_message_soap = b"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="https://zato.io/ns/20130518">
  <soap:Body>{data}</soap:Body>
</soap:Envelope>"""

zato_message_plain = b'{data}'
zato_message_declaration = b"<?xml version='1.0' encoding='UTF-8'?>" + zato_message_plain

# Returned if there has been any exception caught.
soap_error = """<?xml version='1.0' encoding='UTF-8'?>
<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/1999/XMLSchema">
   <SOAP-ENV:Body>
     <SOAP-ENV:Fault>
     <faultcode>SOAP-ENV:{faultcode}</faultcode>
     <faultstring><![CDATA[cid [{cid}], faultstring [{faultstring}]]]></faultstring>
      </SOAP-ENV:Fault>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

def client_json_error(cid, faultstring):
    zato_env = {'zato_env':{'result':ZATO_ERROR, 'cid':cid, 'details':faultstring}} 
    return dumps(zato_env)

def client_soap_error(cid, faultstring):
    return soap_error.format(**{'faultcode':'Client', 'cid':cid, 'faultstring':faultstring})

def server_soap_error(cid, faultstring):
    return soap_error.format(**{'faultcode':'Server', 'cid':cid, 'faultstring':faultstring})

client_error_wrapper = {
    'json': client_json_error,
    'soap': client_soap_error,
}

def get_client_error_wrapper(transport, data_format):
    try:
        return client_error_wrapper[transport]
    except KeyError:
        # Any KeyError must be caught by the caller
        return client_error_wrapper[data_format] 
                
# ##############################################################################

class RequestDispatcher(object):
    """ Dispatches all the incoming HTTP/SOAP requests to appropriate handlers.
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
        if url_type == URL_TYPE.SOAP:
            return server_soap_error(cid, msg)
        
        # Let's return the message as-is if we didn't have any specific envelope
        # to use.
        return msg
    
    def _handle_quotes_soap_action(self, soap_action):
        """ Make sure quotes around SOAP actions are ignored so these two
        are equivalent:
        - SOAPAction: "my.soap.action"
        - SOAPAction: my.soap.action
        """
        if soap_action[0] == '"' and soap_action[-1] == '"':
            soap_action = soap_action[1:-1]
            
        return soap_action
    
    def dispatch(self, cid, req_timestamp, wsgi_environ, worker_store):
        """ Base method for dispatching incoming HTTP/SOAP messages. If the security
        configuration is one of the technical account or HTTP basic auth, 
        the security validation is being performed. Otherwise, that step 
        is postponed until a concrete transport-specific handler is invoked.
        """
        path_info = wsgi_environ['PATH_INFO']
        soap_action = wsgi_environ.get('HTTP_SOAPACTION', '')
        
        if soap_action:
            soap_action = self._handle_quotes_soap_action(soap_action)
            
        url_data = self.security.url_sec_get(path_info, soap_action)
        payload = wsgi_environ['wsgi.input'].read()
        
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'cid:[{}], payload:[{}], wsgi_environ:[{}]'.format(cid, payload, wsgi_environ)
            logger.debug(msg)

        if url_data:
            transport = url_data['transport']
            data_format = url_data['data_format']
            try:
                if not url_data.is_active:
                    msg = 'url_data:[{}] is not active, raising NotFound'.format(sorted(url_data.items()))
                    logger.warn(msg)
                    raise NotFound(cid, 'Inactive channel')
                
                if url_data.sec_def != ZATO_NONE:
                    if url_data.sec_def.sec_type in(security_def_type.tech_account, security_def_type.basic_auth, 
                                                security_def_type.wss):
                        self.security.handle(cid, url_data, path_info, payload, wsgi_environ)
                    else:
                        log_msg = '[{0}] sec_def.sec_type:[{1}] needs no auth'.format(cid, url_data.sec_def.sec_type)
                        logger.debug(log_msg)
                else:
                    log_msg = '[{0}] No security for URL [{1}]'.format(cid, path_info)
                    logger.debug(log_msg)
                
                handler = getattr(self, '{0}_handler'.format(transport))

                service_info, response = handler.handle(cid, wsgi_environ, payload, transport, worker_store, 
                    self.simple_io_config, data_format, path_info)
                wsgi_environ['zato.http.response.headers']['Content-Type'] = response.content_type
                wsgi_environ['zato.http.response.headers'].update(response.headers)
                wsgi_environ['zato.http.response.status'] = b'{} {}'.format(response.status_code, responses[response.status_code])

                return response.payload

            except Exception, e:
                _format_exc = format_exc(e)
                status = _status_internal_server_error
                if isinstance(e, ClientHTTPError):
                    response = e.msg
                    status_code = e.status
                    reason = e.reason
                    if isinstance(e, Unauthorized):
                        status = _status_unauthorized
                        wsgi_environ['zato.http.response.headers']['WWW-Authenticate'] = e.challenge
                    elif isinstance(e, NotFound):
                        status = _status_not_found
                else:
                    status_code = INTERNAL_SERVER_ERROR
                    response = _format_exc
                    
                # TODO: This should be configurable. Some people may want such
                # things to be on DEBUG whereas for others ERROR will make most sense
                # in given circumstances.
                if logger.isEnabledFor(logging.ERROR):
                    msg = 'Caught an exception, cid:[{0}], status_code:[{1}], _format_exc:[{2}]'.format(
                        cid, status_code, _format_exc)
                    logger.log(logging.ERROR, msg)
                    
                try:
                    error_wrapper = get_client_error_wrapper(transport, data_format)
                except KeyError:
                    # It's OK. Apparently it's neither 'soap' nor json'
                    if logger.isEnabledFor(TRACE1):
                        msg = 'No client error wrapper for transport:[{}], data_format:[{}]'.format(transport, data_format)
                        logger.log(TRACE1, msg)
                else:
                    response = error_wrapper(cid, response)
                    
                wsgi_environ['zato.http.response.status'] = status
                return response
        else:
            response = "[{}] URL:[{}] or SOAP action:[{}] doesn't exist".format(cid, path_info, soap_action)
            wsgi_environ['zato.http.response.status'] = _status_not_found
            
            logger.error(response)
            return response
        
class _BaseMessageHandler(object):
    
    def __init__(self, http_soap={}, server=None):
        self.http_soap = http_soap
        self.server = server # A ParallelServer instance
    
    def init(self, cid, path_info, request, headers, transport, data_format):

        if transport == 'soap':
            # HTTP headers are all uppercased at this point.
            soap_action = headers.get('HTTP_SOAPACTION')
    
            if not soap_action:
                raise BadRequest(cid, 'Client did not send the SOAPAction header')
            
            soap_action = self._handle_quotes_soap_action(soap_action)

            if not soap_action:
                raise BadRequest(cid, 'Client sent an empty SOAPAction header')
        else:
            soap_action = ''

        _soap_actions = self.http_soap.getall(path_info)
        
        for _soap_action_info in _soap_actions:
            
            # TODO: Remove the call to .keys() when this pull request is merged in
            #       https://github.com/dsc/bunch/pull/4
            if soap_action in _soap_action_info.keys():
                service_info = _soap_action_info[soap_action]
                break
        else:
            msg = '[{0}] Could not find the service config for URL:[{1}], SOAP action:[{2}]'.format(
                cid, path_info, soap_action)
            logger.warn(msg)
            raise NotFound(cid, msg)

        logger.debug('[{0}] impl_name:[{1}]'.format(cid, service_info.impl_name))

        if(logger.isEnabledFor(TRACE1)):
            buff = StringIO()
            pprint(self.server.service_store.services, stream=buff)
            logger.log(TRACE1, '[{0}] service_store.services:[{1}]'.format(cid, buff.getvalue()))
            buff.close()
            
        service_data = self.server.service_store.service_data(service_info.impl_name)
        
        return service_info
    
    def handle_security(self):
        raise NotImplementedError('Must be implemented by subclasses')
        
    def _set_response_data(self, service, **kwargs):
        data_format = kwargs.get('data_format')
        transport = kwargs.get('transport')
        
        self.set_payload(service.response, data_format, transport, service)
        self.set_content_type(service.response, data_format, transport, kwargs['service_info'])
        
        return service.response
    
    def handle(self, cid, wsgi_environ, raw_request, transport, worker_store, simple_io_config, data_format, path_info):
    
        service_info = self.init(cid, path_info, raw_request, wsgi_environ, transport, data_format)
        service = self.server.service_store.new_instance(service_info.impl_name)
        
        response = service.update_handle(self._set_response_data, service, raw_request,
            CHANNEL.HTTP_SOAP, data_format, transport, self.server, worker_store.broker_client,
            worker_store, cid, simple_io_config, service_info=service_info, wsgi_environ=wsgi_environ)
                
        return service_info, response

    # ##########################################################################
    
    def _get_xml_admin_payload(self, service_instance, zato_message_template, payload):
        
        if payload:
            data=payload.getvalue()
        else:
            data=b"""<{response_elem} xmlns="{namespace}">
                <zato_env>
                  <cid>{cid}</cid>
                  <result>{result}</result>
                </zato_env>
              </{response_elem}>
            """.format(response_elem=getattr(service_instance.SimpleIO, 'response_elem', 'response'),
                       namespace=getattr(service_instance.SimpleIO, 'namespace', zato_namespace),
                         cid=service_instance.cid, result=ZATO_OK)

        return zato_message_template.format(data=data.encode('utf-8'))
    
    def set_payload(self, response, data_format, transport, service_instance):
        """ Sets the actual payload to represent the service's response out of
        whatever the service produced. This includes converting dictionaries into
        JSON, adding Zato metadata and wrapping the mesasge in SOAP if need be.
        """
        if isinstance(service_instance, AdminService):
            if data_format == SIMPLE_IO.FORMAT.JSON:
                zato_env = {'zato_env':{'result':response.result, 'cid':service_instance.cid, 'details':response.result_details}}
                if response.payload:
                    payload = response.payload.getvalue(False)
                    payload.update(zato_env)
                else:
                    payload = zato_env
                    
                response.payload = dumps(payload)
                
            else:
                if transport == URL_TYPE.SOAP:
                    zato_message_template = zato_message_soap
                else:
                    zato_message_template = zato_message_declaration
                    
                if response.payload:
                    if not isinstance(response.payload, basestring):
                        response.payload = self._get_xml_admin_payload(service_instance, zato_message_template, response.payload)
                else:
                    response.payload = self._get_xml_admin_payload(service_instance, zato_message_template, None)
        else:
            if not isinstance(response.payload, basestring):
                response.payload = response.payload.getvalue() if response.payload else ''

        if transport == URL_TYPE.SOAP:
            if not isinstance(service_instance, AdminService):
                response.payload = soap_doc.format(body=response.payload)
    
    def set_content_type(self, response, data_format, transport, service_info):
        """ Sets a response's content type if one hasn't been supplied by the user.
        """
        # A user provided their own content type ..
        if response.content_type_changed:
            content_type = response.content_type
        else:
            # .. or they did not so let's find out if we're using SimpleIO ..
            if data_format == SIMPLE_IO.FORMAT.XML:
                if transport == URL_TYPE.SOAP:
                    if service_info['soap_version'] == '1.1':
                        content_type = self.server.soap11_content_type
                    else:
                        content_type = self.server.soap12_content_type
                else:
                    content_type = self.server.plain_xml_content_type
            elif data_format == SIMPLE_IO.FORMAT.JSON:
                content_type = self.server.json_content_type
            # .. alright, let's use the default value after all.
            else:
                content_type = response.content_type
                
        response.content_type = content_type
    
    # ##########################################################################
    
    def on_broker_msg_CHANNEL_HTTP_SOAP_CREATE_EDIT(self, msg, *args):
        """ Updates the configuration so that there's a link between a URL
        and a SOAP method to a service.
        """
        old_url_path = msg.get('old_url_path')
        old_soap_action = msg.get('old_soap_action', '')
        
        # A plain HTTP channel has always one SOAP action, the dummy empty one ''
        # so we can just quickly recreate it from scratch
        if msg.transport == URL_TYPE.PLAIN_HTTP:
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
            
    def on_broker_msg_CHANNEL_HTTP_SOAP_DELETE(self, msg, *args):
        """ Deletes an HTTP/SOAP channel.
        """
        if msg.transport == URL_TYPE.PLAIN_HTTP:
            del self.http_soap[msg.url_path]
        else:
            del self.http_soap[msg.url_path][msg.soap_action]
            if not self.http_soap[msg.url_path]:
                del self.http_soap[msg.url_path]
        
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
