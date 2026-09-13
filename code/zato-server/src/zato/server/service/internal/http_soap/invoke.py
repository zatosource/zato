# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from time import time

# Zato
from zato.common.api import MISC, SEC_DEF_TYPE
from zato.common.odb.model import HTTPSOAP, SecurityBase
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.connection.http_soap import BadRequest
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

# How the dashboard's invoke feature reaches a channel - a plain-HTTP hop over the loopback
# address, on the port the server handling the invocation is itself listening on.
_Invoke_Scheme = 'http://'
_Invoke_Host = '127.0.0.1'

# One connection is all a single invocation needs, and the wrapper is discarded straight afterwards.
_Invoke_Pool_Size = 1

# Long enough for a channel to do real work while still ending rather than hanging the dashboard.
_Invoke_Timeout = 90

# What the dashboard sends when the user names no method.
_Invoke_Default_Method = 'POST'

# ################################################################################################################################

def _set_invoke_response(service, result):
    service.response.payload.status_code = result['status_code']
    service.response.payload.response_body = result['response_body']
    service.response.payload.response_time = result['response_time']

# ################################################################################################################################

def _parse_key_value_params(text):
    if not text or not text.strip():
        return {}

    result = {}
    for sep in ('&', '\n'):
        if sep in text:
            for pair in text.split(sep):
                pair = pair.strip()
                if '=' in pair:
                    key, _, value = pair.partition('=')
                    result[key.strip()] = value.strip()
            return result

    if '=' in text:
        key, _, value = text.partition('=')
        result[key.strip()] = value.strip()

    return result

# ################################################################################################################################
# ################################################################################################################################

class InvokeChannel(AdminService):

    name = 'zato.http-soap.invoke-channel'
    input = 'id', '-payload', '-request_method', '-query_params', '-path_params'
    output = '-status_code', '-response_body', '-response_time'

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).first()
            if not item:
                raise Exception('REST channel `{}` not found'.format(self.request.input.id))

            channel_config = {
                'url_path': item.url_path,
                'security_id': item.security_id,
            }
            sec_config = self._get_security_config(session, item.security_id)

        url_path = self._resolve_url_path(channel_config)
        wrapper = self._build_temp_wrapper(channel_config, sec_config, url_path)

        try:
            result = self._invoke_wrapper(wrapper)
        finally:
            wrapper.session.close()

        _set_invoke_response(self, result)

    def _get_security_config(self, session, security_id):
        if not security_id:
            return {'sec_type': None, 'username': None, 'password': None, 'orig_username': None}

        sec_def = session.query(SecurityBase).filter_by(id=security_id).first()
        if not sec_def:
            return {'sec_type': None, 'username': None, 'password': None, 'orig_username': None}

        username = sec_def.username
        password = sec_def.password

        if username is None:
            username = ''

        if password is None:
            password = ''

        # A stored secret is decrypted here, and decrypt returns anything that is not
        # encrypted as it stands.
        if password:
            password = self.server.decrypt(password)

        # API key definitions keep a placeholder username in the ODB while the actual
        # header name is an opaque attribute of the definition, so it is resolved here.
        if sec_def.sec_type == SEC_DEF_TYPE.APIKEY:
            opaque = parse_instance_opaque_attr(sec_def)
            header = opaque.get('header') or self.server.api_key_header
            username = header

        return {
            'sec_type': sec_def.sec_type,
            'username': username,
            'password': password,
            'orig_username': username,
        }

    def _resolve_url_path(self, channel_config:'strdict') -> 'str':
        """ Returns the channel's URL path with its placeholders filled in from the path parameters
        given on input. A path that cannot be built is reported rather than sent out with its
        placeholders still in it.
        """
        url_path = channel_config['url_path']
        path_params = _parse_key_value_params(self.request.input.path_params)

        if path_params:
            try:
                url_path = url_path.format(**path_params)
            except (KeyError, ValueError):
                msg = f'Could not build URL path `{url_path}` out of path parameters `{path_params}`'
                raise BadRequest(self.cid, msg, needs_msg=True)

        out = url_path
        return out

    def _build_temp_wrapper(self, channel_config, sec_config, url_path):
        from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

        # The channel is invoked over the loopback address on the port this very server
        # is listening on, which the server always knows.
        port = self.server.port
        method = self.request.input.get('request_method', '') or _Invoke_Default_Method

        wrapper_config = {
            'id': 'temp-invoke-{}'.format(self.cid),
            'is_active': True,

            # The channel side already records this traffic in its own audit log
            'is_internal': True,
            'method': method,
            'data_format': 'json',
            'name': 'temp-invoke-channel-{}'.format(self.cid),
            'transport': 'plain_http',
            'address_host': '{}{}:{}'.format(_Invoke_Scheme, _Invoke_Host, port),
            'address_url_path': url_path,
            'soap_action': '',
            'soap_version': None,
            'ping_method': MISC.DEFAULT_HTTP_PING_METHOD,
            'pool_size': _Invoke_Pool_Size,
            'timeout': _Invoke_Timeout,
            'content_type': None,

            # The hop is a plain-HTTP one, so there is no certificate material in play
            'validate_tls': True,
            'tls_client_cert': None,
            'tls_client_key': None,

            'security_name': None,
            'security_id': None,
            'sec_type': sec_config.get('sec_type'),
            'username': sec_config.get('username'),
            'password': sec_config.get('password'),
            'password_type': None,
            'orig_username': sec_config.get('orig_username'),
            'salt': None,
        }

        return HTTPSOAPWrapper(self.server, wrapper_config)

    def _invoke_wrapper(self, wrapper):
        method = self.request.input.get('request_method', '') or _Invoke_Default_Method
        payload = self.request.input.get('payload', '') or ''
        query_params = _parse_key_value_params(self.request.input.get('query_params', ''))

        start = time()
        try:
            response = wrapper.http_request(method, self.cid, data=payload, params=query_params or None)
            elapsed = time() - start
            return {
                'status_code': response.status_code,
                'response_body': response.text,
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }
        except Exception as e:
            elapsed = time() - start
            return {
                'status_code': 0,
                'response_body': str(e),
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }

# ################################################################################################################################
# ################################################################################################################################

class InvokeOutconn(AdminService):

    name = 'zato.http-soap.invoke-outconn'
    input = 'id', '-payload', '-request_method', '-query_params', '-path_params'
    output = '-status_code', '-response_body', '-response_time'

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).first()
            if not item:
                raise Exception('REST outgoing connection `{}` not found'.format(self.request.input.id))
            outconn_name = item.name

        method = self.request.input.get('request_method', '') or _Invoke_Default_Method
        payload = self.request.input.get('payload', '') or ''
        params = self._build_params()

        result = self._invoke_outconn(outconn_name, method, payload, params)
        _set_invoke_response(self, result)

    def _build_params(self):
        params = {}
        path_params = _parse_key_value_params(self.request.input.get('path_params', ''))
        query_params = _parse_key_value_params(self.request.input.get('query_params', ''))
        params.update(path_params)
        params.update(query_params)
        return params

    def _invoke_outconn(self, outconn_name, method, payload, params):
        config_item = self.outgoing.plain_http.get(outconn_name)
        if not config_item:
            raise Exception('Outgoing REST connection wrapper `{}` not found'.format(outconn_name))

        conn = config_item.conn
        start = time()

        try:
            response = conn.http_request(method, self.cid, data=payload, params=params)
            elapsed = time() - start
            return {
                'status_code': response.status_code,
                'response_body': response.text,
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }
        except Exception as e:
            elapsed = time() - start
            return {
                'status_code': 0,
                'response_body': str(e),
                'response_time': '{:.1f}ms'.format(elapsed * 1000),
            }

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
