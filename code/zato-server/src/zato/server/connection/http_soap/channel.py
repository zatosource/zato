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

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime
from httplib import INTERNAL_SERVER_ERROR, NOT_FOUND, responses
from traceback import format_exc

# anyjson
from anyjson import dumps

# Bunch
from bunch import Bunch

# Zato
from zato.common import SIMPLE_IO, URL_TYPE, ZATO_NONE
from zato.common.util import payload_from_request, security_def_type, TRACE1
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, \
     NotFound, Unauthorized
from zato.server.connection.request_response import should_store, store
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

_reason_not_found = responses[NOT_FOUND]
_reason_internal_server_error = responses[INTERNAL_SERVER_ERROR]

soap_doc = b"""<?xml version='1.0' encoding='UTF-8'?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>{body}</soap:Body></soap:Envelope>"""

zato_message = b"""<zato_message xmlns="http://gefira.pl/zato">
    {data}
    <zato_env>
        <result>{result}</result>
        <cid>{cid}</cid>
        <details>{details}</details>
    </zato_env>
</zato_message>"""

zato_message_declaration = b"<?xml version='1.0' encoding='UTF-8'?>" + zato_message

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

def client_soap_error(cid, faultstring):
    return soap_error.format(**{'faultcode':'Client', 'cid':cid, 'faultstring':faultstring})

def server_soap_error(cid, faultstring):
    return soap_error.format(**{'faultcode':'Server', 'cid':cid, 'faultstring':faultstring})
                
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
        
        # Let's return the message as-is if we don't have any specific envelope
        # to use.
        return msg        
    
    def dispatch(self, cid, req_timestamp, task, thread_ctx):
        """ Base method for dispatching incoming HTTP/SOAP messages. If the security
        configuration is one of the technical account or HTTP basic auth, 
        the security validation is being performed. Otherwise, that step 
        is postponed until a concrete transport-specific handler is invoked.
        """
        headers = task.request_data.headers
        soap_action = headers.get('SOAPACTION', '')
        url_data = self.security.url_sec_get(task.request_data.path, soap_action)

        if url_data:
            transport = url_data['transport']
            try:
                bs = task.request_data.getBodyStream()
                if task.request_data.body_rcv:
                    payload = bs.read()
                else:
                    payload = bs.getvalue()
                    
                headers = task.request_data.headers
                
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

                data_format = url_data['data_format']
                service_info, response = handler.handle(cid, task, payload, headers, transport, thread_ctx, self.simple_io_config, data_format, task.request_data)
                task.response_headers['Content-Type'] = response.content_type
                task.response_headers.update(response.headers)
                task.setResponseStatus(response.status_code, responses[response.status_code])
                
                # Optionally store the sample request/response pair
                if should_store(service_info.service_id):
                    store(thread_ctx.store.broker_client, cid, service_info.service_id, req_timestamp, datetime.utcnow(), payload, response.payload)
          
                return response.payload

            except Exception, e:
                _format_exc = format_exc(e)
                if isinstance(e, ClientHTTPError):
                    response = e.msg
                    status = e.status
                    reason = e.reason
                    if isinstance(e, Unauthorized):
                        task.response_headers['WWW-Authenticate'] = e.challenge
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
            response = "[{}] The URL:[{}] or SOAP action:[{}] doesn't exist".format(cid, task.request_data.uri, soap_action)
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

        _soap_actions = self.http_soap.getall(task.request_data.path)
        
        for _soap_action_info in _soap_actions:
            
            # TODO: Remove the call to .keys() when this pull request is merged in
            #       https://github.com/dsc/bunch/pull/4
            if soap_action in _soap_action_info.keys():
                service_info = _soap_action_info[soap_action]
                break
        else:
            msg = '[{0}] Could not find the service config for URL:[{1}], SOAP action:[{2}]'.format(
                cid, task.request_data.uri, soap_action)
            logger.warn(msg)
            raise NotFound(cid, msg)

        logger.debug('[{0}] impl_name:[{1}]'.format(cid, service_info.impl_name))

        logger.log(TRACE1, '[{0}] service_store.services:[{1}]'.format(cid, self.server.service_store.services))
        service_data = self.server.service_store.service_data(service_info.impl_name)
        
        return payload_from_request(request, data_format, transport), service_info, service_data
    
    def handle_security(self):
        raise NotImplementedError('Must be implemented by subclasses')
    
    def handle(self, cid, task, raw_request, headers, transport, thread_ctx, simple_io_config, data_format, request_data):
        payload, service_info, service_data = self.init(cid, task, raw_request, headers, transport, data_format)

        service_instance = self.server.service_store.new_instance(service_info.impl_name)
        service_instance.update(service_instance, self.server, thread_ctx.store.broker_client, thread_ctx.store, 
                cid, payload, raw_request, transport, simple_io_config, data_format, request_data)

        service_instance.pre_handle()
        service_instance.handle()
        
        response = service_instance.response
        
        self.set_payload(response, data_format, transport, service_instance)
        self.set_content_type(response, data_format, transport, service_info)
        
        service_instance.post_handle()

        logger.debug('[{}] Returning response.content_type:[{}], response.payload:[{}]'.format(cid, response.content_type, response.payload))
        return service_info, response

    # ##########################################################################
    
    def _get_xml_admin_payload(self, service_instance, response, data, zato_message_template):
        return zato_message_template.format(cid=service_instance.cid, result=response.result, 
            details=response.result_details, data=data.encode('utf-8'))
    
    def set_payload(self, response, data_format, transport, service_instance):
        """ Sets the actual payload to represent the service's response out of
        whatever the service produced. This includes converting dictionaries into
        JSON, adding Zato metadata and wrapping the mesasge in SOAP if need be.
        """
        if isinstance(service_instance, AdminService):
            if data_format == SIMPLE_IO.FORMAT.JSON:
                payload = response.payload.getvalue(False)
                payload.update({'zato_env':{'result':response.result, 'cid':service_instance.cid, 'details':response.result_details}})
                response.payload = dumps(payload)
            else:
                if transport == URL_TYPE.SOAP:
                    zato_message_template = zato_message
                else:
                    zato_message_template = zato_message_declaration
                    
                if response.payload:
                    if not isinstance(response.payload, basestring):
                        response.payload = self._get_xml_admin_payload(service_instance, 
                            response, response.payload.getvalue(), zato_message_template)
                else:
                    response.payload = self._get_xml_admin_payload(service_instance, 
                            response, '<response/>', zato_message_template)
        else:
            if not isinstance(response.payload, basestring):
                response.payload = response.payload.getvalue() if response.payload else ''

        if transport == URL_TYPE.SOAP:
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
