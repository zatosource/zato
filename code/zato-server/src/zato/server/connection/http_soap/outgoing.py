# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy
from datetime import datetime
from http.client import OK
from io import StringIO
from logging import DEBUG, getLogger
from traceback import format_exc
from urllib.parse import urlencode

# gevent
from gevent.lock import RLock

# requests
from requests import Response as _RequestsResponse
from requests.adapters import HTTPAdapter
from requests.exceptions import Timeout as RequestsTimeout
from requests.sessions import Session as RequestsSession

# requests-ntlm
from requests_ntlm import HttpNtlmAuth

# requests-toolbelt
from requests_toolbelt import MultipartEncoder

# Zato
from zato.common.api import ContentType, CONTENT_TYPE, DATA_FORMAT, NotGiven, SEC_DEF_TYPE, URL_TYPE
from zato.common.exception import Inactive, TimeoutException
from zato.common.json_ import dumps, loads
from zato.common.marshal_.api import extract_model_class, is_list, Model
from zato.common.typing_ import cast_
from zato.common.util.api import get_component_name
from zato.common.util.config import extract_param_placeholders
from zato.common.util.open_ import open_rb
from zato.server.connection.queue import ConnectionQueue

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.bearer_token import BearerTokenInfoResult
    from zato.common.typing_ import any_, callnone, dictnone, list_, stranydict, strdictnone, strstrdict, type_
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigDict
    ConfigDict = ConfigDict
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_rest')
has_debug = logger.isEnabledFor(DEBUG)

# ################################################################################################################################
# ################################################################################################################################

soapenv11_namespace = 'http://schemas.xmlsoap.org/soap/envelope/'
soapenv12_namespace = 'http://www.w3.org/2003/05/soap-envelope'

# ################################################################################################################################
# ################################################################################################################################

_API_Key = SEC_DEF_TYPE.APIKEY
_Basic_Auth = SEC_DEF_TYPE.BASIC_AUTH
_NTLM = SEC_DEF_TYPE.NTLM
_OAuth = SEC_DEF_TYPE.OAUTH
_TLS_Key_Cert = SEC_DEF_TYPE.TLS_KEY_CERT
_WSS = SEC_DEF_TYPE.WSS

# ################################################################################################################################
# ################################################################################################################################

class Response(_RequestsResponse):
    data: 'strdictnone'

# ################################################################################################################################
# ################################################################################################################################

class HTTPSAdapter(HTTPAdapter):
    """ An adapter which exposes a method for clearing out the underlying pool. Useful with HTTPS as it allows to update TLS
    material on the fly.
    """
    def clear_pool(self):
        self.poolmanager.clear()

# ################################################################################################################################
# ################################################################################################################################

class BaseHTTPSOAPWrapper:
    """ Base class for HTTP/SOAP connection wrappers.
    """
    def __init__(
        self,
        config, # type: stranydict
        _requests_session=None, # type: SASession | None
        server=None # type: ParallelServer | None
    ) -> 'None':
        self.config = config
        self.config['timeout'] = float(self.config['timeout']) if self.config['timeout'] else 0
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.RequestsSession = RequestsSession or _requests_session
        self.server = cast_('ParallelServer', server)
        self.session = RequestsSession()
        self.https_adapter = HTTPSAdapter()
        self.session.mount('https://', self.https_adapter)
        self._component_name = get_component_name()
        self.default_content_type = self.get_default_content_type()

        self.address = ''
        self.path_params = []
        self.base_headers = {}
        self.sec_type = self.config['sec_type']

        self.soap = {}
        self.soap['1.1'] = {}
        self.soap['1.1']['content_type'] = 'text/xml; charset=utf-8'
        self.soap['1.1']['message'] = """<?xml version="1.0" encoding="utf-8"?>
<s11:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s11="%s">
  {header}
  <s11:Body>{data}</s11:Body>
</s11:Envelope>""" % (soapenv11_namespace,)

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
<s12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:s12="%s">{header}
  <s12:Body>{data}</s12:Body>
</s12:Envelope>""" % (soapenv12_namespace,)

        self.soap['1.2']['header_template'] = """<s12:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" >
          <wsse:Security>
            <wsse:UsernameToken>
              <wsse:Username>{Username}</wsse:Username>
              <wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{Password}</wsse:Password>
            </wsse:UsernameToken>
          </wsse:Security>
        </s12:Header>
        """

        self.set_address_data()
        self.set_auth()

# ################################################################################################################################

    def set_auth(self) -> 'None':

        # Local variables
        self.requests_auth = None
        self.username = None

        # #######################################
        #
        # API Keys
        #
        # #######################################
        if self.sec_type == _API_Key:
            username = self.config.get('orig_username')
            if not username:
                username = self.config['username']
            self.base_headers[username] = self.config['password']

        # #######################################
        #
        # HTTP Basic Auth
        #
        # #######################################
        elif self.sec_type in {_Basic_Auth}:
            self.requests_auth = self.auth
            self.username = self.requests_auth[0]

        # #######################################
        #
        # NTLM
        #
        # #######################################
        elif self.sec_type == _NTLM:
            _username, _password = self.auth
            _requests_auth = HttpNtlmAuth(_username, _password)
            self.requests_auth = _requests_auth
            self.username = _username

        # #######################################
        #
        # WS-Security
        #
        # #######################################
        elif self.sec_type == _WSS:
            self.soap[self.config['soap_version']]['header'] = \
                self.soap[self.config['soap_version']]['header_template'].format(
                    Username=self.config['username'], Password=self.config['password'])

# ################################################################################################################################

    def _get_auth(self) -> 'any_':
        """ Returns a username and password pair or None, if no security definition has been attached.
        """
        if self.sec_type in {_Basic_Auth, _NTLM}:
            auth = (self.config['username'], self.config['password'])
        else:
            auth = None

        return auth

    auth = property(fget=_get_auth, doc=_get_auth.__doc__)

# ################################################################################################################################

    def invoke_http(
        self,
        cid:'str',
        method:'str',
        address:'str',
        data:'str',
        headers:'strstrdict',
        hooks:'any_',
        *args:'any_',
        **kwargs:'any_'
    ) -> '_RequestsResponse':

        # Local variables
        max_retries = kwargs.get('max_retries', 0)
        retry_sleep_time = kwargs.get('retry_sleep_time', 2)
        retry_backoff_threshold = kwargs.get('retry_backoff_threshold', 3)
        retry_backoff_multiplier = kwargs.get('retry_backoff_multiplier', 2)
        params = kwargs.get('params')
        json = kwargs.pop('json', None)
        cert = self.config['tls_key_cert_full_path'] if self.sec_type == _TLS_Key_Cert else None

        if ('ZATO_SKIP_TLS_VERIFY' in os.environ) or ('Zato_Skip_TLS_Verify' in os.environ):
            tls_verify = False
        else:
            tls_verify = self.config.get('tls_verify', True)
            tls_verify = tls_verify if isinstance(tls_verify, bool) else tls_verify.encode('utf-8')

        # This is optional and, if not given, we will use the security configuration from self.config
        sec_def_name = kwargs.pop('sec_def_name', NotGiven)

        # If we have a security definition name on input, it must be a Bearer token (OAuth)
        if sec_def_name is not NotGiven:
            _sec_type = _OAuth
        else:
            sec_def_name = self.config['security_name']
            _sec_type = self.sec_type

        # Force type hints
        sec_def_name = cast_('str', sec_def_name)

        # Reusable
        is_bearer_token = _sec_type == _OAuth

        # OAuth scopes can be provided on input even if we do not have a Bearer token definition attached,
        # which is why we .pop them here, to make sure they do not propagate to the requests library.
        scopes = kwargs.pop('auth_scopes', '')

        try:

            # Bearer tokens are obtained dynamically ..
            if is_bearer_token:

                # .. this is reusable ..
                sec_def = self.server.security_facade.get_bearer_token_by_name(sec_def_name)

                # .. each OAuth definition will use a specific data format ..
                data_format = sec_def['data_format']

                # .. otherwise, we can check if they are provided in the security definition itself ..
                if not scopes:
                    scopes = sec_def.get('scopes') or ''
                    scopes = scopes.splitlines()
                    scopes = ' '.join(scopes)

                # .. get a Bearer token ..
                result = self._get_bearer_token_auth(sec_def_name, scopes, data_format)

                # .. populate headers ..
                headers['Authorization'] = f'Bearer {result.info.token}'

                # .. this is needed for later use ..
                token_expires_in_sec = result.cache_expiry
                token_is_cache_hit = result.is_cache_hit
                token_cache_hits = result.cache_hits

                # This is needed by request
                auth = None

            # .. we enter here if this is not a Bearer token definition ..
            else:

                # .. otherwise, the credentials will have been already obtained
                # .. but note that Suds connections don't have requests_auth, hence the getattr call ..
                auth = getattr(self, 'requests_auth', None)

                # .. we have no token to report about.
                token_expires_in_sec = None
                token_is_cache_hit = None
                token_cache_hits = None

            # .. basic details about what we are sending what we are sending ..
            msg = f'REST out → cid={cid}; {method} {address}; name:{self.config["name"]}; params={params}; len={len(data)}' + \
                  f'; sec={sec_def_name} ({_sec_type})'

            # .. optionally, log details of the Bearer token ..
            if is_bearer_token:
                msg += f'; expiry={token_expires_in_sec}; tok-from-cache={token_is_cache_hit}; tok-cache-hits={token_cache_hits}'

            # .. log the information about our request ..
            logger.info(msg)

            # .. do send it ..
            response = self.session.request(
                method, address, data=data, json=json, auth=auth, headers=headers, hooks=hooks,
                cert=cert, verify=tls_verify, timeout=self.config['timeout'], *args, **kwargs)

            # .. log what we received ..
            msg = f'REST out ← cid={cid}; {response.status_code} time={response.elapsed}; len={len(response.text)}'
            logger.info(msg)

            # .. and return it.
            return response

        except RequestsTimeout:
            raise TimeoutException(cid, format_exc())

# ################################################################################################################################

    def _get_bearer_token_auth(self, sec_def_name:'str', scopes:'str', data_format:'str') -> 'BearerTokenInfoResult':

        # This will get the token from cache or from the remote auth. server ..
        result = self.server.bearer_token_manager.get_bearer_token_info_by_sec_def_name(sec_def_name, scopes, data_format)

        # .. which we can return to our caller.
        return result

# ################################################################################################################################

    def ping(self, cid:'str', return_response:'bool'=False, log_verbose:'bool'=False, *, ping_path:'str'='/') -> 'any_':
        """ Pings a given HTTP/SOAP resource
        """
        logger.info('Pinging:`%s`', self.config_no_sensitive)

        # Session object will write some info to it ..
        verbose = StringIO()

        start = datetime.utcnow()
        ping_method = self.config['ping_method'] or 'HEAD'

        def zato_pre_request_hook(hook_data:'stranydict', *args:'any_', **kwargs:'any_') -> 'None':

            entry = '{} (UTC)\n{} {}\n'.format(datetime.utcnow().isoformat(),
                ping_method, hook_data['request'].url)
            _ = verbose.write(entry)

        # .. potential wrapper paths must be replaced ..
        ping_path = ping_path or '/'
        address = self.address.replace(r'{_zato_path}', ping_path)

        # .. invoke the other end ..
        response = self.invoke_http(cid, ping_method, address, '', self._create_headers(cid, {}),
            {'zato_pre_request':zato_pre_request_hook})

        # .. store additional info, get and close the stream.
        _ = verbose.write('Code: {}'.format(response.status_code))
        _ = verbose.write('\nResponse time: {}'.format(datetime.utcnow() - start))
        value = verbose.getvalue()
        verbose.close()

        if log_verbose:
            func = logger.info if response.status_code == OK else logger.warning
            func(value)

        return response if return_response else value

# ################################################################################################################################

    def get_default_content_type(self) -> 'str':

        if self.config['content_type']:
            return self.config['content_type']

        # For requests other than SOAP, set content type only if we know the data format
        if self.config['data_format']:

            # Not SOAP
            if self.config['transport'] == URL_TYPE.PLAIN_HTTP:

                # JSON
                return CONTENT_TYPE.JSON # type: ignore

        # SOAP
        elif self.config['transport'] == URL_TYPE.SOAP:

            # SOAP 1.1
            if self.config['soap_version'] == '1.1':
                return CONTENT_TYPE.SOAP11 # type: ignore

            # SOAP 1.2
            else:
                return CONTENT_TYPE.SOAP12 # type: ignore

        # If we are here, assume it is regular text by default
        return 'text/plain'

# ################################################################################################################################

    def _create_headers(self, cid:'str', user_headers:'strstrdict', now:'str'='') -> 'strstrdict':
        headers = deepcopy(self.base_headers)
        headers.update({
            'X-Zato-CID': cid,
            'X-Zato-Component': self._component_name,
            'X-Zato-Msg-TS': now or datetime.utcnow().isoformat(),
        })

        if self.config.get('transport') == URL_TYPE.SOAP:
            headers['SOAPAction'] = self.config.get('soap_action')

        content_type = user_headers.pop('Content-Type', self.default_content_type)
        if content_type:
            headers['Content-Type'] = content_type

        headers.update(user_headers)

        return headers

# ################################################################################################################################

    def set_address_data(self) -> 'None':
        """Sets the full address to invoke and parses input URL's configuration,
        to extract any named parameters that will have to be passed in by users
        during actual calls to the resource.
        """

        # Set the full adddress ..
        self.address = '{}{}'.format(self.config['address_host'], self.config['address_url_path'])

        # .. and parse out placeholders for path parameters.
        for param_name in extract_param_placeholders(self.config['address_url_path']):
            self.path_params.append(param_name[1:-1])

# ################################################################################################################################
# ################################################################################################################################

class HTTPSOAPWrapper(BaseHTTPSOAPWrapper):
    """ A thin wrapper around the API exposed by the 'requests' package.
    """
    def __init__(
        self,
        server, # type: ParallelServer
        config, # type: stranydict
        requests_module=None # type: any_
    ) -> 'None':
        super(HTTPSOAPWrapper, self).__init__(config, requests_module, server)
        self.server = server

# ################################################################################################################################

    def __str__(self) -> 'str':
        return '<{} at {}, config:[{}]>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    __repr__ = __str__

# ################################################################################################################################

    def format_address(self, cid:'str', params:'stranydict') -> 'tuple[str, stranydict]':
        """ Formats a URL path to an external resource. Note that exceptions raised
        do not contain anything except for CID. This is in order to keep any potentially
        sensitive data from leaking to clients.
        """
        if not params:
            logger.warning('CID:`%s` No parameters given for URL path:`%r`', cid, self.config['address_url_path'])
            raise ValueError('CID:`{}` No parameters given for URL path'.format(cid))

        path_params = {}
        try:
            for name in self.path_params: # type: ignore
                path_params[name] = params.pop(name)

            return (self.address.format(**path_params), dict(params))
        except(KeyError, ValueError):
            logger.warning('CID:`%s` Could not build URL address `%r` path:`%r` with params:`%r`, e:`%s`',
                cid, self.address, self.config['address_url_path'], params, format_exc())

            raise ValueError('CID:`{}` Could not build URL path'.format(cid))

# ################################################################################################################################

    def _impl(self) -> 'RequestsSession':
        """ Returns the self.session object through which access to HTTP/SOAP resources is provided.
        """
        return self.session

    impl = property(fget=_impl, doc=_impl.__doc__)

# ################################################################################################################################

    def _enforce_is_active(self) -> 'None':
        if not self.config['is_active']:
            raise Inactive(self.config['name'])

# ################################################################################################################################

    def _soap_data(self, data:'str | bytes', headers:'stranydict') -> 'tuple[any_, stranydict]':
        """ Wraps the data in a SOAP-specific messages and adds the headers required.
        """
        needs_soap_wrapper = False
        soap_config:'strstrdict' = self.soap[self.config['soap_version']]

        # The idea here is that even though there usually won't be the Content-Type
        # header provided by the user, we shouldn't overwrite it if one has been
        # actually passed in.
        if not headers.get('Content-Type'):
            headers['Content-Type'] = soap_config['content_type']

        # We do not need an envelope if the data already has one ..
        if isinstance(data, bytes):
            if b':Envelope' in data:
                return data, headers # type: ignore
            else:
                needs_soap_wrapper = True

        else:
            if ':Envelope' in data:
                return data, headers # type: ignore
            else:
                needs_soap_wrapper = True

        if needs_soap_wrapper:
            return soap_config['message'].format(header='', data=data), headers
        else:
            return data, headers

# ################################################################################################################################

    def http_request(
        self,
        method:'str',
        cid:'str',
        data:'any_'='',
        params:'dictnone'=None,
        *args:'any_',
        **kwargs:'any_'
    ) -> 'Response':

        # First, make sure that the connection is active
        self._enforce_is_active()

        # Local variables
        _is_soap = self.config['transport'] == 'soap'

        # Pop it here for later use because we cannot pass it to the requests module
        model = kwargs.pop('model', None)

        # We do not serialize ourselves data based on this content type,
        # leaving it up to the underlying HTTP library to do it ..
        needs_serialize_based_on_content_type = self.config.get('content_type') != ContentType.FormURLEncoded

        # .. otherwise, our input data may need to be serialized ..
        if needs_serialize_based_on_content_type:

            # .. but we never serialize string objects,
            # .. assuming they already represent what ought to be sent as-is ..
            needs_request_serialize = not isinstance(data, str)

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
        headers = kwargs.pop('headers', None) or {}

        # .. build a default set of headers now ..
        headers = self._create_headers(cid, headers)

        # .. SOAP requests need to be specifically formatted now ..
        if _is_soap:
            data, headers = self._soap_data(data, headers)

        # .. check if we have custom query parameters ..
        params = params or {}

        # .. if the address is a template, format it with input parameters ..
        if self.path_params:
            address, qs_params = self.format_address(cid, params) # type: ignore
        else:
            address, qs_params = self.address, dict(params)

        # .. make sure that Unicode objects are turned into bytes ..
        if needs_serialize_based_on_content_type and (not _is_soap):
            if isinstance(data, str):
                data = data.encode('utf-8')

        # .. do invoke the connection ..
        response = self.invoke_http(cid, method, address, data, headers, {}, params=qs_params, *args, **kwargs)

        # .. by default, we have no parsed response at all, ..
        # .. which means that we can assume it will be the same as the raw, text response ..
        response.data = response.text # type: ignore

        # .. check if we are explicitly told that we handle JSON ..
        _has_data_format_json = self.config['data_format'] == DATA_FORMAT.JSON

        # .. check if we perhaps received JSON in the response ..
        _has_json_content_type = 'application/json' in (response.headers.get('Content-Type') or '') # type: ignore

        # .. are we actually handling JSON in this response .. ?
        _is_json:'bool' = _has_data_format_json or _has_json_content_type # type: ignore

        # .. if yes, try to parse the response accordingly ..
        if _is_json:
            try:
                response.data = loads(response.text or '""') # type: ignore
            except ValueError as e:
                raise Exception('Could not parse JSON response `{}`; e:`{}`'.format(response.text, e.args[0]))

        # .. if we have a model class on input, deserialize the received response into one ..
        if model:
            response.data = self.server.marshal_api.from_dict(None, response.data, model) # type: ignore

        # .. now, return the response to the caller.
        return cast_('Response', response)

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

    def upload(
        self,
        cid,  # type: str
        item, # type: str
        field_name = 'data',      # type: str
        mime_type  = 'text/plain' # type: str
    ) -> 'Response':

        # Make sure such a file exists
        if not os.path.exists(item):
            raise Exception('File to upload not found -> `%s`', item)

        # Ensure that the path actually is a file
        if not os.path.isfile(item):
            raise Exception('Path is not a file -> `%s`', item)

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
        data='',      # type: ignore
        model=None,   # type: type_[Model] | None
        callback,     # type: callnone
        params=None,  # type: strdictnone
        headers=None, # type: strdictnone
        method='',    # type: str
        sec_def_name=None,    # type: any_
        auth_scopes=None,     # type: any_
        log_response=True,    # type: bool
        needs_exception=True, # type: bool
        max_retries=0,        # type: int
        retry_sleep_time=2,   # type: int
        retry_backoff_threshold=3, # type: int
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
            )
        except Exception as e:
            if needs_exception:
                raise
            else:
                logger.warn('Caught an exception -> %s -> %s', e, format_exc())
        else:

            # .. optionally, log what we received ..
            if log_response:
                logger.info('REST call response received -> %s', response.text)

            if not response.ok:
                raise Exception(response.text)

            # .. extract the underlying data ..
            response_data = response.data # type: ignore

            # .. if we have a model, do make use of it here ..
            if model:

                # .. if this model is actually a list ..
                if is_list(model, True): # type: ignore

                    # .. extract the underlying model ..
                    model_class:'type_[Model]' = extract_model_class(model) # type: ignore

                    # .. build a list that we will map the response to ..
                    data:'list_[Model]' = [] # type: ignore

                    # .. go through everything we had in the response ..
                    for item in response_data: # type: ignore

                        # .. build an actual model instance ..
                        _item = model_class.from_dict(item)

                        # .. and append it to the data that we are producing ..
                        data.append(_item) # type: ignore
                else:
                    data:'Model' = model.from_dict(response_data)

            # .. if there is no model, use the response as-is ..
            else:
                data = response_data # type: ignore

            # .. run our callback, if there is any ..
            if callback:
                data = callback(data, cid=cid, id=id, model=model, callback=callback)

            # .. and return the data to our caller ..
            return data, response

RESTWrapper = HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

class SudsSOAPWrapper(BaseHTTPSOAPWrapper):
    """ A thin wrapper around the suds SOAP library
    """
    def __init__(self, config:'stranydict') -> 'None':
        super(SudsSOAPWrapper, self).__init__(config)
        self.set_auth()
        self.update_lock = RLock()
        self.config = config
        self.config['timeout'] = float(self.config['timeout'])
        self.config_no_sensitive = deepcopy(self.config)
        self.config_no_sensitive['password'] = '***'
        self.address = '{}{}'.format(self.config['address_host'], self.config['address_url_path'])
        self.conn_type = 'Suds SOAP'
        self.client = ConnectionQueue(
            self.server,
            self.config['is_active'],
            self.config['pool_size'],
            self.config['queue_build_cap'],
            self.config['id'],
            self.config['name'],
            self.conn_type,
            self.address,
            self.add_client
        )

# ################################################################################################################################

    def set_auth(self) -> 'None':
        """ Configures the security for requests, if any is to be configured at all.
        """
        self.suds_auth = {'username':self.config['username'], 'password':self.config['password']}

# ################################################################################################################################

    def add_client(self) -> 'None':

        logger.info('About to add a client to `%s` (%s)', self.address, self.conn_type)

        try:

            # Lazy-imported here to make sure gevent monkey patches everything well in advance
            from suds.client import Client
            from suds.transport.https import HttpAuthenticated
            # from suds.transport.https import WindowsHttpAuthenticated
            from suds.wsse import Security, UsernameToken

            client = None
            transport = None

            if self.sec_type == _Basic_Auth:
                transport = HttpAuthenticated(**self.suds_auth)

            elif self.sec_type == _NTLM:

                # Suds
                from suds.transport.http import HttpTransport

                class WindowsHttpAuthenticated(HttpAuthenticated):
                    def u2handlers(self):
                        from ntlm3 import HTTPNtlmAuthHandler
                        handlers = HttpTransport.u2handlers(self)
                        handlers.append(HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(self.pm))
                        return handlers

                transport = WindowsHttpAuthenticated(**self.suds_auth)

            elif self.sec_type == _WSS:
                security = Security()
                token = UsernameToken(self.suds_auth['username'], self.suds_auth['password'])
                security.tokens.append(token)

                client = Client(self.address, autoblend=True, wsse=security)

            if self.sec_type in {_Basic_Auth, _NTLM}:
                client = Client(self.address, autoblend=True, transport=transport)

            # Still could be either none at all or WSS
            if not self.sec_type:
                client = Client(self.address, autoblend=True, timeout=self.config['timeout'])

            if client:
                _  = self.client.put_client(client)
            else:
                logger.warning('SOAP client to `%s` is None', self.address)

        except Exception:
            logger.warning('Error while adding a SOAP client to `%s` (%s) e:`%s`', self.address, self.conn_type, format_exc())

# ################################################################################################################################

    def build_client_queue(self) -> 'None':
        with self.update_lock:
            self.client.build_queue()

# ################################################################################################################################
# ################################################################################################################################
