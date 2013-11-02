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

# Django
from django.http import QueryDict

# Zato
from zato.common import CHANNEL, DATA_FORMAT, SIMPLE_IO, URL_PARAMS_PRIORITY, \
     URL_TYPE, zato_namespace, ZATO_ERROR, ZATO_NONE, ZATO_OK
from zato.common.util import security_def_type, TRACE1
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, \
     NotFound, Unauthorized
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

_status_internal_server_error = b'{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
_status_not_found = b'{} {}'.format(NOT_FOUND, responses[NOT_FOUND])
_status_unauthorized = b'{} {}'.format(UNAUTHORIZED, responses[UNAUTHORIZED])

soap_doc = b"""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="https://zato.io/ns/20130518"><soap:Body>{body}</soap:Body></soap:Envelope>""" # noqa

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
    def __init__(self, url_data=None, security=None, request_handler=None, simple_io_config=None):
        self.url_data = url_data
        self.security = security
        self.request_handler = request_handler
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
        
        # Needed in later steps
        path_info = wsgi_environ['PATH_INFO']
        soap_action = wsgi_environ.get('HTTP_SOAPACTION', '')
        
        # Fix up SOAP action - turns "my:soap:action" into my:soap:action,
        # that is, strips it out of surrounding quotes, if any.
        if soap_action:
            soap_action = self._handle_quotes_soap_action(soap_action)

        # Can we recognize this combination of URL path and SOAP action at all?
        url_match, channel_item = self.url_data.match(path_info, soap_action)
        
        # OK, we can possibly handle it
        if url_match:

            # Raise 404 if the channel is inactive
            if not channel_item.is_active:
                logger.warn('url_data:[%s] is not active, raising NotFound', sorted(url_match.items()))
                raise NotFound(cid, 'Channel inactive')
            
            # Read payload only now, right before it's needed the first time,
            # possibly, by security checks.
            payload = wsgi_environ['wsgi.input'].read()
            
            try:
                
                # Will raise an exception on any security violation
                self.url_data.check_security(cid, channel_item, path_info, payload, wsgi_environ)

                # OK, no security exception at that point means we can finally
                # invoke the service.
                response = self.request_handler.handle(cid, url_match, channel_item, wsgi_environ, 
                    payload, worker_store, self.simple_io_config)
                
                # Got response from the service so we can construct response headers now
                self.add_response_headers(wsgi_environ, response)

                # Return the payload to the client
                return response.payload

            except Exception, e:
                
                _format_exc = format_exc(e)
                status = _status_internal_server_error
                
                if isinstance(e, ClientHTTPError):
                    response = e.msg
                    status_code = e.status
                    
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
                logger.error('Caught an exception, cid:[%s], status_code:[%s], _format_exc:[%s]', cid, status_code, _format_exc)
                    
                try:
                    error_wrapper = get_client_error_wrapper(channel_item.transport, channel_item.data_format)
                except KeyError:
                    # It's OK. Apparently it's neither 'soap' nor json'
                    if logger.isEnabledFor(TRACE1):
                        msg = 'No client error wrapper for transport:[{}], data_format:[{}]'.format(
                            channel_item.transport, channel_item.data_format)
                        logger.log(TRACE1, msg)
                else:
                    response = error_wrapper(cid, response)
                    
                wsgi_environ['zato.http.response.status'] = status
                return response
            
        # This is 404, no such URL path and SOAP action is known.
        else:
            response = "[{}] Unknown URL:[{}] or SOAP action:[{}]".format(cid, path_info, soap_action)
            wsgi_environ['zato.http.response.status'] = _status_not_found
            
            logger.error(response)
            return response
        
    def add_response_headers(self, wsgi_environ, response):
        """ Adds HTTP response headers on a 200 OK.
        """
        wsgi_environ['zato.http.response.headers']['Content-Type'] = response.content_type
        wsgi_environ['zato.http.response.headers'].update(response.headers)
        wsgi_environ['zato.http.response.status'] = b'{} {}'.format(response.status_code, responses[response.status_code])
        
# ##############################################################################
        
class RequestHandler(object):
    """ Handles individual HTTP requests to a given service.
    """
    def __init__(self, server=None):
        self.server = server # A ParallelServer instance
        
    def _set_response_data(self, service, **kwargs):
        """ A callback invoked by the services after it's done producing the response.
        """
        data_format = kwargs.get('data_format')
        transport = kwargs.get('transport')
        
        self.set_payload(service.response, data_format, transport, service)
        self.set_content_type(service.response, data_format, transport, kwargs['url_match'])
        
        return service.response
    
    def create_channel_params(self, url_match, channel_item, wsgi_environ, raw_request):
        """ Collects parameters specific to this channel (HTTP) and updates wsgi_environ
        with HTTP-specific data.
        """
        path_params = url_match.named
        
        qs = wsgi_environ.get('QUERY_STRING')
        qs = QueryDict(qs, encoding='utf-8')
            
        if channel_item.data_format == DATA_FORMAT.POST:
            post = QueryDict(raw_request, encoding='utf-8')
        else:
            post = QueryDict(None, encoding='utf-8')
            
        wsgi_environ['zato.http.GET'] = qs
        wsgi_environ['zato.http.POST'] = post
        
        if channel_item.url_params_pri == URL_PARAMS_PRIORITY.QS_OVER_PATH:
            path_params.update((key, value) for key, value in qs.items())
            channel_params = path_params
        else:
            channel_params = dict((key, value) for key, value in qs.items())
            channel_params.update(path_params)
            
        return channel_params
    
    def handle(self, cid, url_match, channel_item, wsgi_environ, raw_request, worker_store, simple_io_config):
        """ Create a new instance of a service and invoke it.
        """
        service = self.server.service_store.new_instance(channel_item.service_impl_name)
        
        if channel_item.merge_url_params_req:
            channel_params = self.create_channel_params(url_match, channel_item, wsgi_environ, raw_request)
        else:
            channel_params = None
        
        response = service.update_handle(self._set_response_data, service, raw_request,
            CHANNEL.HTTP_SOAP, channel_item.data_format, channel_item.transport, self.server, worker_store.broker_client,
            worker_store, cid, simple_io_config, wsgi_environ=wsgi_environ, 
            url_match=url_match, channel_item=channel_item, channel_params=channel_params,
            merge_channel_params=channel_item.merge_url_params_req,
            params_priority=channel_item.params_pri)
                
        return response

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
    
    def set_content_type(self, response, data_format, transport, url_match):
        """ Sets a response's content type if one hasn't been supplied by the user.
        """
        # A user provided their own content type ..
        if response.content_type_changed:
            content_type = response.content_type
        else:
            # .. or they did not so let's find out if we're using SimpleIO ..
            if data_format == SIMPLE_IO.FORMAT.XML:
                if transport == URL_TYPE.SOAP:
                    if url_match.soap_version == '1.1':
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
