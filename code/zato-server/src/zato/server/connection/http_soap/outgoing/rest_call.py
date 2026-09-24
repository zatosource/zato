# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from traceback import format_exc
from urllib.parse import quote, urlencode

# requests-toolbelt
from requests_toolbelt import MultipartEncoder

# Zato
from zato.common.api import ContentType, DATA_FORMAT, HTTP_SOAP, URL_TYPE
from zato.common.exception import BadRequest, BackendInvocationError
from zato.common.json_ import dumps, loads
from zato.common.marshal_.api import extract_model_class, is_list, Model
from zato.common.pubsub.outgoing import Attempts_None, Key_Data, Key_Headers, Key_Method, Key_Params, SendRejected, SendResult
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid_server
from zato.common.util.open_ import open_rb
from zato.server.connection.http_soap.invocation import build_jsonata_context, maybe_run_callback, merge_declarative_request
from zato.server.connection.http_soap.outgoing.audit import record_request_sent, record_response_received, \
    record_transport_error
from zato.server.connection.http_soap.outgoing.common import get_rest_rejection_error, is_rest_rejection, logger, \
    Read_Methods, Response, _needs_serialization

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.outgoing import OutgoingPublisher
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, anytuple, callnone, dictnone, list_, stranydict, strstrdict, type_
    callnone = callnone

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue
_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

class _PreparedRequest:
    """ One request right before it goes to the wire.
    """

    def __init__(
        self,
        *,
        method:'str',
        address:'str',
        data:'any_',
        headers:'strstrdict',
        qs_params:'stranydict',
        model:'any_',
        needs_audit:'bool',
        is_soap:'bool',
        data_text:'str | None',
        user_headers:'strstrdict',
        params:'stranydict',
    ) -> 'None':

        self.method = method
        self.address = address
        self.data = data
        self.headers = headers
        self.qs_params = qs_params

        self.model = model
        self.needs_audit = needs_audit
        self.is_soap = is_soap

        # What the queue stores
        self.data_text = data_text
        self.user_headers = user_headers
        self.params = params

# ################################################################################################################################
# ################################################################################################################################

class RESTCallMixin:
    """ The REST side of an outgoing connection - the address with its path parameters filled in,
    the request itself with its audit pair, the per-method shortcuts, file uploads and the typed
    calls that turn a response into a model.
    """

    publisher: 'OutgoingPublisher'

    def format_address(self, cid:'str', params:'stranydict') -> 'tuple[str, stranydict]':
        """ Formats a URL path to an external resource. Note that exceptions raised
        do not contain anything except for CID. This is in order to keep any potentially
        sensitive data out of what clients receive.
        """
        if not params:
            msg = 'No parameters given for URL path template `{}`, missing parameters: {}'.format(
                self.config['address_url_path'],
                self.path_params
            )
            raise BadRequest(cid, msg, needs_msg=True)

        # Path parameters are taken out of a copy of what the caller gave us and whatever is left
        # of that copy becomes the query string, so the caller's own dict is never written into.
        qs_params = dict(params)

        path_params = {}
        try:
            for name in self.path_params:
                value = qs_params.pop(name)

                # A path parameter fills in one segment of the address and nothing beyond it, so
                # every character that means something to a URL is encoded, the percent sign
                # included. A value arrives as it is meant to be read, so a slash in it is a slash
                # in that one segment and a value spelled as ../ names no directory above it.
                path_params[name] = quote(str(value), safe='')

            address = self.address.format(**path_params)

            out = address, qs_params
            return out
        except(KeyError, ValueError):
            msg = 'Could not build URL path template `{}`, missing parameters: {}'.format(
                self.config['address_url_path'],
                self.path_params
            )
            raise BadRequest(cid, msg, needs_msg=True)

# ################################################################################################################################

    def _prepare_request(
        self,
        method:'str',
        cid:'str',
        data:'any_',
        params:'dictnone',
        kwargs:'stranydict',
        needs_declarative_merge:'bool',
    ) -> '_PreparedRequest':
        """ Everything a request is before it goes to the wire, what is left in kwargs is what the requests library receives.
        """

        # First, make sure that the connection is active
        self._enforce_is_active()

        # A caller that records events of its own, such as the engine delivering to a channel's
        # destinations, turns this connection's own recording off for the duration of one call ..
        needs_audit = kwargs.pop('needs_audit', True)

        # .. and a connection that does not record anything anyway stays that way.
        if not self.needs_audit:
            needs_audit = False

        # Local variables
        _is_soap = self.config['transport'] == 'soap'

        # Pop it here for later use because we cannot pass it to the requests module
        model = kwargs.pop('model', None)

        # Fill in the blanks from the connection's declarative invocation profile (REST only) -
        # explicit arguments always win and JSONata values are evaluated at call time
        # against the data the caller passed in.
        if (not _is_soap) and needs_declarative_merge:
            declarative_headers = kwargs.pop('headers', None)
            context = build_jsonata_context(data)
            method, data, params, declarative_headers = merge_declarative_request(
                self.config, method, data, params, declarative_headers, context)
            if declarative_headers:
                kwargs['headers'] = declarative_headers

        # We do not serialize ourselves data based on this content type,
        # leaving it up to the underlying HTTP library to do it ..
        needs_serialize_based_on_content_type = self.config['content_type'] != ContentType.FormURLEncoded

        # .. otherwise, our input data may need to be serialized ..
        if needs_serialize_based_on_content_type:

            # .. we never serialize what already represents what ought to be sent as-is ..
            needs_request_serialize = _needs_serialization(data)

            # .. if we are here, we know check further if serialization is required ..
            if needs_request_serialize:

                # .. we are explicitly told to send JSON ..
                if self.config['data_format'] == DATA_FORMAT.JSON:

                    # .. models need to be converted to dicts before they can be serialized ..
                    if isinstance(data, Model):
                        data = data.to_dict()

                    # .. do serialize to JSON now ..
                    data = dumps(data)

                # .. we are explicitly told to submit form-like data ..
                elif self.config['data_format'] == DATA_FORMAT.FORM_DATA:
                    data = urlencode(data)

        # .. check if we have custom headers on input ..
        user_headers = kwargs.pop('headers', None) or {}

        # .. build a default set of headers now ..
        headers = self._create_headers(cid, user_headers)

        # .. SOAP requests need to be specifically formatted now ..
        if _is_soap:
            data, headers = self._soap_data(data, headers)

        # .. check if we have custom query parameters ..
        params = params or {}

        # .. if the address is a template, format it with input parameters ..
        if self.path_params:
            address, qs_params = self.format_address(cid, params)
        else:
            address, qs_params = self.address, dict(params)

        # Only a text body can be queued
        if isinstance(data, str):
            data_text = data
        else:
            data_text = None

        # .. make sure that Unicode objects are turned into bytes ..
        if needs_serialize_based_on_content_type and (not _is_soap):
            if isinstance(data, str):
                data = data.encode('utf-8')

        out = _PreparedRequest(
            method=method,
            address=address,
            data=data,
            headers=headers,
            qs_params=qs_params,
            model=model,
            needs_audit=needs_audit,
            is_soap=_is_soap,
            data_text=data_text,
            user_headers=user_headers,
            params=params,
        )

        return out

# ################################################################################################################################

    def _send_prepared(self, cid:'str', prepared:'_PreparedRequest', args:'anytuple', kwargs:'stranydict') -> 'Response':
        """ Sends one prepared request to the wire and turns the answer into a response.
        """
        method = prepared.method
        address = prepared.address
        qs_params = prepared.qs_params
        needs_audit = prepared.needs_audit
        model = prepared.model
        _is_soap = prepared.is_soap

        # .. record the outgoing request in the audit log ..
        endpoint = f'{method} {address}'

        # The whole call is recorded, not only its body - the address a path template resolved to,
        # the query string and the caller's own headers go with it.
        if needs_audit:
            record_request_sent(self, cid, endpoint, prepared.data, method,
                address=address, qs_params=qs_params, user_headers=prepared.user_headers)

        # .. do invoke the connection ..
        try:
            response = self.invoke_http(
                cid, method, address, prepared.data, prepared.headers, {}, params=qs_params, *args, **kwargs)
        except Exception as e:

            # .. record the error in the audit log before re-raising ..
            if needs_audit:
                record_transport_error(self, cid, endpoint, e)
            raise

        response = cast_('Response', response)

        # .. record the received response in the audit log, sharing the request's CID ..
        if needs_audit:
            record_response_received(self, cid, endpoint, response)

        # .. by default, we have no parsed response at all, ..
        # .. which means that we can assume it will be the same as the raw, text response ..
        response.data = response.text
        response.zato_method = method
        response.zato_address = address
        response.zato_qs_params = qs_params

        # .. check if we are explicitly told that we handle JSON ..
        _has_data_format_json = self.config['data_format'] == DATA_FORMAT.JSON

        # .. check if we perhaps received JSON in the response ..
        _has_json_content_type = 'application/json' in (response.headers.get('Content-Type') or '')

        # .. are we actually handling JSON in this response .. ?
        _is_json:'bool' = _has_data_format_json or _has_json_content_type

        # .. if yes, try to parse the response accordingly ..
        if _is_json:
            try:
                response.data = loads(response.text or '""')
            except ValueError as e:
                msg = 'Could not parse JSON response `{}`; e:`{}`'.format(response.text, e.args[0])
                raise BadRequest(cid, msg, needs_msg=True)

        # .. if we have a model class on input, deserialize the received response into one ..
        if model:
            response.data = self.server.marshal_api.from_dict(None, response.data, model)

        # .. deliver the response-mapped result to the configured callback in the background,
        # .. a no-op for connections without callback config ..
        if not _is_soap:
            maybe_run_callback(self.server, self.config, cid, response.data)

        # .. now, return the response to the caller.
        return response

# ################################################################################################################################

    def resend_recorded(
        self,
        cid:'str',
        method:'str',
        address:'str',
        data:'any_',
        qs_params:'stranydict',
        user_headers:'strstrdict',
        ) -> 'Response':
        """ Repeats one recorded call exactly as it was made - the address already resolved, the
        query string and the caller's headers as they went out. Only the connection's own security
        headers are built afresh, out of the credentials it is configured with today.

        The connection's audit log is off for the call, the resend recording the attempt itself
        as a row linked to the original.
        """
        self._enforce_is_active()

        headers = self._create_headers(cid, user_headers)

        is_soap = self.config['transport'] == URL_TYPE.SOAP

        # A recorded SOAP body is the envelope as it went on the wire, and `_soap_data` leaves
        # an envelope alone while still settling the content type.
        if is_soap:
            data, headers = self._soap_data(data, headers)

        elif isinstance(data, str):
            data = data.encode('utf-8')

        prepared = _PreparedRequest(
            method=method,
            address=address,
            data=data,
            headers=headers,
            qs_params=qs_params,
            model=None,
            needs_audit=False,
            is_soap=is_soap,
            data_text=None,
            user_headers=user_headers,
            params=qs_params,
        )

        out = self._send_prepared(cid, prepared, (), {})
        return out

# ################################################################################################################################

    def _needs_queue(self, prepared:'_PreparedRequest') -> 'bool':
        """ Whether a request goes through the connection's queue.
        """
        if not self.config[_queue.Field_Use_Queue]:
            return False

        if prepared.is_soap:
            return False

        if prepared.method in Read_Methods:
            return False

        out = prepared.data_text is not None
        return out

# ################################################################################################################################

    def _send_or_queue(self, cid:'str', prepared:'_PreparedRequest', args:'anytuple', kwargs:'stranydict') -> 'SendResult':
        """ A send with the queue switch on.
        """
        request = {
            Key_Method: prepared.method,
            Key_Data: prepared.data_text,
            Key_Headers: prepared.user_headers,
            Key_Params: prepared.params,
        }

        # The direct attempt has no retries of its own
        kwargs[_retry.Field_Max_Retries] = 0

        def attempt() -> 'Response':
            response = self._send_prepared(cid, prepared, args, kwargs)

            if is_rest_rejection(response):
                raise SendRejected(get_rest_rejection_error(response), response)

            return response

        out = self.publisher.send_or_queue(cid, request, attempt)
        return out

# ################################################################################################################################

    def http_request(
        self,
        method:'str',
        cid:'str',
        data:'any_'='',
        params:'dictnone'=None,
        *args:'any_',
        **kwargs:'any_'
    ) -> 'Response | SendResult':

        prepared = self._prepare_request(method, cid, data, params, kwargs, needs_declarative_merge=True)

        if self._needs_queue(prepared):
            out = self._send_or_queue(cid, prepared, args, kwargs)
            return out

        out = self._send_prepared(cid, prepared, args, kwargs)
        return out

# ################################################################################################################################

    def send_from_queue(self, cid:'str', request:'stranydict') -> 'Response':
        """ Makes one attempt to deliver a request the queue holds, raising when the endpoint turned it down.
        """
        kwargs:'stranydict' = {
            'headers': request[Key_Headers],
            _retry.Field_Max_Retries: 0,
        }

        # A request without a method was never merged with the declarative profile
        method = request[Key_Method]
        needs_declarative_merge = not method

        prepared = self._prepare_request(
            method, cid, request[Key_Data], request[Key_Params], kwargs, needs_declarative_merge=needs_declarative_merge)

        response = self._send_prepared(cid, prepared, (), kwargs)

        if is_rest_rejection(response):
            raise SendRejected(get_rest_rejection_error(response), response)

        return response

# ################################################################################################################################

    def publish(self, data:'any_'='', cid:'str'='', **kwargs:'any_') -> 'PublishResult':
        """ Queues one message for delivery to this connection without trying the wire first.
        """

        # Handlers are given the body as text
        if not isinstance(data, str):
            data = dumps(data)

        if not cid:
            cid = new_cid_server()

        request = {
            Key_Method: '',
            Key_Data: data,
            Key_Headers: {},
            Key_Params: {},
        }

        out = self.publisher.publish_request(cid, Attempts_None, request, **kwargs)
        return out

# ################################################################################################################################

    def get(self, cid:'str', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('GET', cid, '', params, *args, **kwargs)

    def delete(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('DELETE', cid, data, params, *args, **kwargs)

    def options(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('OPTIONS', cid, data, params, *args, **kwargs)

    def post(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('POST', cid, data, params, *args, **kwargs)

    send = post

    def put(self, cid:'str', data:'str'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('PUT', cid, data, params, *args, **kwargs)

    def patch(self, cid:'str', data:'str'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        return self.http_request('PATCH', cid, data, params, *args, **kwargs)

    def rest_invoke(self, cid:'str', data:'any_'='', params:'dictnone'=None, *args:'any_', **kwargs:'any_') -> 'Response':
        """ Invokes the connection with no explicit arguments needed - the HTTP method,
        query string, path params, headers and body all come from the connection's
        declarative invocation profile, with anything given explicitly winning.
        """
        return self.http_request('', cid, data, params, *args, **kwargs)

    def upload(
        self,
        cid,  # type: str
        item, # type: str
        field_name = 'data',      # type: str
        mime_type  = 'text/plain' # type: str
    ) -> 'Response':

        # Make sure such a file exists
        if not os.path.exists(item):
            raise Exception(f'File to upload not found -> `{item}`')

        # Ensure that the path actually is a file
        if not os.path.isfile(item):
            raise Exception(f'Path is not a file -> `{item}`')

        # Extract the file
        file_name = os.path.basename(item)

        # At this point, we have collected everything needed to upload the file and we can proceed
        with open_rb(item) as file_to_upload:

            # Build a list of fields to be encoded as a multi-part upload
            fields = {
                field_name: (file_name, file_to_upload, mime_type)
            }

            # .. this is  the object that builds a multi-part message out of the file ..
            encoder = MultipartEncoder(fields=fields)

            # .. build user headers based on what the encoder produced ..
            headers = {
                'Content-Type': encoder.content_type
            }

            # .. now, we can invoke the remote endpoint with our file on input.
            return self.post(cid, data=encoder, headers=headers)

# ################################################################################################################################

    def rest_call(
        self,
        *,
        cid,          # type: str
        data='',      # type: any_
        model=None,   # type: type_[Model] | None
        callback,     # type: callnone
        params=None,  # type: strdictnone
        headers=None, # type: strdictnone
        method='',    # type: str
        sec_def_name=None,    # type: any_
        auth_scopes=None,     # type: any_
        log_response=False,   # type: bool
        needs_exception=True, # type: bool
        max_retries=None,     # type: int | None
        retry_sleep_time=None,   # type: int | None
        retry_backoff_threshold=None, # type: int | None
        retry_backoff_multiplier=None, # type: int | None
    ) -> 'any_':

        # Invoke the system ..
        try:
            response:'Response' = self.http_request(
                method,
                cid,
                data=data,
                sec_def_name=sec_def_name,
                auth_scopes=auth_scopes,
                params=params,
                headers=headers,
                max_retries=max_retries,
                retry_sleep_time=retry_sleep_time,
                retry_backoff_threshold=retry_backoff_threshold,
                retry_backoff_multiplier=retry_backoff_multiplier,
            )
        except Exception as e:
            if needs_exception:
                raise
            else:
                logger.warning('Caught an exception -> %s -> %s', e, format_exc())
        else:

            # .. a response body is only logged by a caller that asked for it ..
            if log_response:
                logger.info('REST call response received -> %s', response.text)

            if not response.ok:
                if response.zato_qs_params:
                    qs_path = '?' + urlencode(response.zato_qs_params)
                else:
                    qs_path = ''
                msg =  f'Error calling outgoing connection: {self.config["name"]} -> {response.zato_method}'
                msg += f' {response.zato_address}{qs_path} -> {response.data}'

                logger.info(msg)
                raise BackendInvocationError(cid, msg, needs_msg=True)

            # .. extract the underlying data ..
            response_data = response.data

            # .. if we have a model, do make use of it here ..
            if model:

                # .. if this model is actually a list ..
                if is_list(model, True):

                    # .. extract the underlying model ..
                    model_class:'type_[Model]' = extract_model_class(model)

                    # .. build a list that we will map the response to ..
                    model_list:'list_[Model]' = []

                    # .. go through everything we had in the response ..
                    for item in response_data:

                        # .. build an actual model instance ..
                        _item = model_class.from_dict(item)

                        # .. and append it to the data that we are producing ..
                        model_list.append(_item)

                    data = model_list
                else:
                    data = model.from_dict(response_data)

            # .. if there is no model, use the response as-is ..
            else:
                data = response_data

            # .. run our callback, if there is any ..
            if callback:
                data = callback(data, cid=cid, model=model, callback=callback)

            # .. and return the data to our caller ..
            return data, response

# ################################################################################################################################
# ################################################################################################################################
