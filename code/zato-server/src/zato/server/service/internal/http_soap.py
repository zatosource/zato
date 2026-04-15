# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from time import time

# Zato
from zato.common.api import CONNECTION, SEC_DEF_TYPE, URL_TYPE, ZATO_NONE
from zato.common.json_internal import dumps
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
from zato.server.service import AsIs, Boolean, Integer
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strintdict

# ################################################################################################################################
# ################################################################################################################################

_GetList_Optional = ('include_wrapper', 'cluster_id', 'connection', 'transport', 'data_format', 'needs_security_group_names')

# ################################################################################################################################
# ################################################################################################################################

def _fixup_list_fields(data):
    for key in ('gateway_service_list', 'security_groups'):
        value = data.get(key)
        if isinstance(value, str):
            try:
                data[key] = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                data[key] = []

def _resolve_security_fields(server, data):
    security_id = data.get('security_id')
    if security_id:
        for sec_item in server.config_store.get_list('security'):
            if sec_item.get('id') == security_id:
                data['security_name'] = sec_item['name']
                data['sec_type'] = sec_item.get('sec_type') or sec_item.get('type')
                break

def _get_entity_type(connection, transport):
    """ Map connection + transport to Rust ConfigStore entity type. """
    if connection == CONNECTION.CHANNEL or connection == 'channel':
        if transport == URL_TYPE.PLAIN_HTTP or transport == 'plain_http':
            return 'channel_rest'
        else:
            return 'channel_soap'
    else:
        if transport == URL_TYPE.PLAIN_HTTP or transport == 'plain_http':
            return 'outgoing_rest'
        else:
            return 'outgoing_soap'

# ################################################################################################################################
# ################################################################################################################################

class _BaseGet(AdminService):

    output = 'id', 'name', 'is_active', 'is_internal', 'url_path', \
        '-service_id', '-service_name', '-security_id', '-security_name', '-sec_type', \
        '-method', '-soap_action', '-soap_version', '-data_format', '-host', '-ping_method', '-pool_size', \
        '-merge_url_params_req', '-url_params_pri', '-params_pri', '-serialization_type', '-timeout', \
        '-content_type', '-cache_id', '-cache_name', Integer('-cache_expiry'), '-cache_type', \
        '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', \
        '-data_encoding', '-username', '-is_wrapper', '-wrapper_type', AsIs('-security_groups'), '-security_group_count', \
        '-security_group_member_count', '-needs_security_group_names', Boolean('-validate_tls'), '-gateway_service_list'

# ################################################################################################################################

    def _get_security_groups_info(self, item:'any_', security_groups_member_count:'strintdict') -> 'strdict':

        out:'strdict' = {
            'group_count': 0,
            'member_count': 0,
        }

        if security_groups := item.get('security_groups'):
            for group_id in security_groups:
                member_count = security_groups_member_count.get(group_id) or 0
                out['member_count'] += member_count
                out['group_count'] += 1

        return out

# ################################################################################################################################

class Get(_BaseGet):
    """ Returns information about an individual HTTP/SOAP object by its name.
    """
    input = '-cluster_id', '-id', '-name', '-connection', '-transport'

    def handle(self):
        input = self.request.input
        name = input.get('name') or input.get('id')
        connection = input.get('connection') or 'channel'
        transport = input.get('transport') or 'plain_http'
        entity_type = _get_entity_type(connection, transport)

        items = self.server.config_store.get_list(entity_type)
        for item in items:
            if item.get('name') == name or str(item.get('id')) == str(name):
                self.response.payload = item
                return

# ################################################################################################################################

class GetList(_BaseGet):
    """ Returns a list of HTTP/SOAP connections.
    """
    input = '-connection', '-transport', Integer('-cur_page'), Boolean('-paginate'), '-query', \
        *['-' + f if isinstance(f, str) else f for f in _GetList_Optional]
    output = _BaseGet.output + ('-connection', '-transport')

    def _build_sec_lookup(self):
        out = {}
        for sec in self.server.config_store.get_list('security'):
            out[sec.get('name')] = sec
        return out

    def _build_service_lookup(self):
        out = {}
        for svc_data in self.server.service_store.services.values():
            name = svc_data['name']
            service_id = self.server.service_store.get_service_id_by_name(name)
            out[name] = service_id
        return out

    def handle(self):
        from zato.common.api import Groups

        connection = self.request.input.get('connection') or 'channel'
        transport = self.request.input.get('transport') or 'plain_http'
        include_wrapper = self.request.input.get('include_wrapper') or False
        should_ignore_wrapper = not include_wrapper
        needs_security_group_names = self.request.input.get('needs_security_group_names') or False

        import logging
        _logger = logging.getLogger(__name__)

        entity_type = _get_entity_type(connection, transport)
        items = self.server.config_store.get_list(entity_type)

        _logger.info('http-soap.get-list -> entity_type:%s, include_wrapper:%s, item_count:%s',
            entity_type, include_wrapper, len(items))
        for _i, _item in enumerate(items):
            _logger.info('http-soap.get-list -> raw item[%s] is_wrapper:%s, wrapper_type:%s, name:%s, keys:%s',
                _i, _item.get('is_wrapper'), _item.get('wrapper_type'), _item.get('name'), list(_item.keys()))

        security_groups_member_count = self.invoke('zato.groups.get-member-count', group_type=Groups.Type.API_Clients)

        if needs_security_group_names:
            all_security_groups = self.invoke('zato.groups.get-list', group_type=Groups.Type.API_Clients)
        else:
            all_security_groups = []

        sec_lookup = self._build_sec_lookup()
        svc_lookup = self._build_service_lookup()

        out = []

        for item in items:

            security_groups_for_item_info = self._get_security_groups_info(item, security_groups_member_count)
            item['security_group_count'] = security_groups_for_item_info['group_count']
            item['security_group_member_count'] = security_groups_for_item_info['member_count']

            if needs_security_group_names:
                if security_groups_for_item := item.get('security_groups'):
                    new_security_groups = []
                    for item_group_id in security_groups_for_item:
                        for group in all_security_groups:
                            if item_group_id == group['id']:
                                new_security_groups.append(group['name'])
                                break
                    item['security_groups'] = sorted(new_security_groups)

            if should_ignore_wrapper and item.get('is_wrapper'):
                continue

            item['connection'] = connection
            item['transport'] = transport

            sec_name = item.get('security_name')
            if sec_name and sec_name in sec_lookup:
                sec_def = sec_lookup[sec_name]
                item['security_id'] = sec_def.get('id')
                item['sec_type'] = sec_def.get('sec_type') or sec_def.get('type')
            else:
                item.setdefault('security_id', None)
                item.setdefault('sec_type', None)

            svc_name = item.get('service') or item.get('service_name')
            item['service_name'] = svc_name
            item['service_id'] = svc_lookup.get(svc_name) if svc_name else None

            for field in ('soap_action', 'soap_version', 'ping_method', 'pool_size',
                          'serialization_type', 'timeout', 'cache_id', 'cache_name', 'cache_type'):
                item.setdefault(field, None)

            out.append(item)

        self.response.payload = self._paginate_list(out)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new HTTP/SOAP connection.
    """
    input = 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', '-data_format', \
        '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', '-params_pri', \
        '-serialization_type', '-timeout', '-content_type', \
        '-cache_id', Integer('-cache_expiry'), '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-is_active', '-transport', '-is_internal', '-cluster_id', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list'
    output = 'id', 'name', '-url_path'

    def handle(self):

        input = self.request.input
        connection = input.connection
        transport = input.get('transport') or URL_TYPE.PLAIN_HTTP

        entity_type = _get_entity_type(connection, transport)

        data = {}
        for key in ('name', 'url_path', 'connection', 'service', 'service_id', 'security_id', 'method',
            'soap_action', 'soap_version', 'data_format', 'host', 'ping_method', 'pool_size',
            'merge_url_params_req', 'url_params_pri', 'params_pri', 'serialization_type',
            'timeout', 'content_type', 'cache_id', 'cache_expiry', 'content_encoding',
            'match_slash', 'http_accept', 'should_parse_on_input', 'should_validate',
            'should_return_errors', 'data_encoding', 'is_active', 'transport', 'is_internal',
            'is_wrapper', 'wrapper_type', 'username', 'password', 'security_groups',
            'validate_tls', 'gateway_service_list'):
            value = input.get(key)
            if value is not None and value != '':
                data[key] = value

        data.setdefault('is_active', True)
        data.setdefault('is_internal', False)
        data.setdefault('transport', URL_TYPE.PLAIN_HTTP)

        _fixup_list_fields(data)
        _resolve_security_fields(self.server, data)

        name = input.name
        self.server.config_store.set(entity_type, name, data)

        stored = self.server.config_store.get(entity_type, name)
        self.response.payload.id = stored['id']
        self.response.payload.name = name
        self.response.payload.url_path = input.url_path

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an HTTP/SOAP connection.
    """
    input = 'id', 'name', 'url_path', 'connection', \
        '-service', '-service_id', AsIs('-security_id'), '-method', '-soap_action', '-soap_version', \
        '-data_format', '-host', '-ping_method', '-pool_size', Boolean('-merge_url_params_req'), '-url_params_pri', \
        '-params_pri', '-serialization_type', '-timeout', '-content_type', \
        '-cache_id', Integer('-cache_expiry'), '-content_encoding', Boolean('-match_slash'), '-http_accept', \
        '-should_parse_on_input', '-should_validate', '-should_return_errors', '-data_encoding', \
        '-cluster_id', '-is_active', '-transport', \
        '-is_wrapper', '-wrapper_type', '-username', '-password', AsIs('-security_groups'), Boolean('-validate_tls'), \
        '-gateway_service_list'
    output = '-id', '-name'

    def handle(self):

        input = self.request.input
        connection = input.connection
        transport = input.get('transport') or URL_TYPE.PLAIN_HTTP

        entity_type = _get_entity_type(connection, transport)

        data = {}
        for key in ('id', 'name', 'url_path', 'connection', 'service', 'service_id', 'security_id', 'method',
            'soap_action', 'soap_version', 'data_format', 'host', 'ping_method', 'pool_size',
            'merge_url_params_req', 'url_params_pri', 'params_pri', 'serialization_type',
            'timeout', 'content_type', 'cache_id', 'cache_expiry', 'content_encoding',
            'match_slash', 'http_accept', 'should_parse_on_input', 'should_validate',
            'should_return_errors', 'data_encoding', 'is_active', 'transport',
            'is_wrapper', 'wrapper_type', 'username', 'password', 'security_groups',
            'validate_tls', 'gateway_service_list'):
            value = input.get(key)
            if value is not None and value != '':
                data[key] = value

        data.setdefault('is_active', True)
        data.setdefault('transport', URL_TYPE.PLAIN_HTTP)

        _fixup_list_fields(data)
        _resolve_security_fields(self.server, data)

        name = input.name
        old_name = None
        for item in self.server.config_store.get_list(entity_type):
            if str(item.get('id')) == str(input.id):
                old_name = item.get('name')
                break
        if old_name and old_name != name:
            self.server.config_store.delete(entity_type, old_name)

        self.server.config_store.set(entity_type, name, data)

        stored = self.server.config_store.get(entity_type, name)
        self.response.payload.id = stored['id']
        self.response.payload.name = name

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an HTTP/SOAP connection.
    """
    input = '-id', '-name', '-connection', '-should_raise_if_missing', '-transport'
    output = '-details'

    def handle(self):

        input = self.request.input
        name = input.get('name') or input.get('id')
        connection = input.get('connection') or 'channel'
        transport = input.get('transport') or 'plain_http'

        if not name:
            raise Exception('Either ID or name are required on input')

        entity_type = _get_entity_type(connection, transport)
        delete_key = None
        for item in self.server.config_store.get_list(entity_type):
            if item.get('name') == name or str(item.get('id')) == str(name):
                delete_key = item['name']
                break

        if not delete_key:
            if input.get('should_raise_if_missing', True):
                raise Exception('HTTP/SOAP object with id or name `{}` not found'.format(name))
            return

        self.server.config_store.delete(entity_type, delete_key)
        self.response.payload.details = 'OK, deleted'

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an HTTP/SOAP connection.
    """
    input = 'id', '-ping_path'
    output = 'id', 'is_success', '-info'

    def handle(self):

        name = self.request.input.id

        for entity_type in ('outgoing_rest', 'outgoing_soap'):
            items = self.server.config_store.get_list(entity_type)
            for item in items:
                if str(item.get('id')) == str(name) or item.get('name') == str(name):
                    transport = item.get('transport', 'plain_http')
                    config_dict = getattr(self.outgoing, transport)
                    self.response.payload.id = self.request.input.id
                    try:
                        result = config_dict.get(item['name']).ping(self.cid, ping_path=self.request.input.ping_path)
                        is_success = True
                    except Exception as e:
                        result = e.args[0]
                        is_success = False
                    finally:
                        self.response.payload.info = result
                        self.response.payload.is_success = is_success
                    return

# ################################################################################################################################

class GetURLSecurity(AdminService):
    """ Returns a JSON document describing the security configuration of all Zato channels.
    """
    def handle(self):
        response = {}
        response['url_sec'] = sorted(self.worker_store.request_handler.security.url_sec.items())
        response['plain_http_handler.http_soap'] = sorted(self.worker_store.request_handler.plain_http_handler.http_soap.items())
        response['soap_handler.http_soap'] = sorted(self.worker_store.request_handler.soap_handler.http_soap.items())
        self.response.payload = dumps(response, sort_keys=True, indent=4)
        self.response.content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

def _set_invoke_response(service, result):
    """ Shared helper -- populates a service's response payload from an invocation result dict. """
    service.response.payload.status_code = result['status_code']
    service.response.payload.response_body = result['response_body']
    service.response.payload.response_time = result['response_time']

# ################################################################################################################################

def _parse_key_value_params(text):
    """ Parses 'key1=val1&key2=val2' or 'key1=val1\nkey2=val2' into a dict. """
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
    """ Invokes a REST channel by creating a temporary HTTPSOAPWrapper,
    calling the channel's local URL with its security credentials,
    and always cleaning up the wrapper afterwards.
    """

    name = 'zato.http-soap.invoke-channel'
    input = 'id', '-payload', '-request_method', '-query_params', '-path_params'
    output = '-status_code', '-response_body', '-response_time'

    def handle(self):
        channel_config = self._get_channel_config(self.request.input.id)
        sec_config = self._get_security_config(channel_config)
        url_path = self._resolve_url_path(channel_config)
        wrapper = self._build_temp_wrapper(channel_config, sec_config, url_path)

        try:
            result = self._invoke_wrapper(wrapper)
        finally:
            wrapper.session.close()

        _set_invoke_response(self, result)

    def _get_channel_config(self, channel_id):
        for item in self.server.config_store.get_list('channel_rest'):
            if str(item.get('id')) == str(channel_id) or item.get('name') == str(channel_id):
                return item
        raise Exception('REST channel `{}` not found'.format(channel_id))

    def _get_security_config(self, channel_config):
        """ Returns a dict with sec_type, username, password, orig_username
        for the channel's security definition, or a no-security dict.
        """
        security_id = channel_config.get('security_id')
        if not security_id or str(security_id) in ('None', ZATO_NONE, 'None/ZATO_NONE'):
            return {'sec_type': None, 'username': None, 'password': None, 'orig_username': None}

        for sec_item in self.server.config_store.get_list('security'):
            if str(sec_item.get('id')) == str(security_id):
                return self._extract_credentials(sec_item)

        return {'sec_type': None, 'username': None, 'password': None, 'orig_username': None}

    def _extract_credentials(self, sec_item):
        sec_type = sec_item.get('sec_type') or sec_item.get('type', '')
        username = sec_item.get('username', '') or ''
        orig_username = sec_item.get('orig_username', '') or username
        password = sec_item.get('password', '') or ''
        password = self._decrypt_password(password)

        return {
            'sec_type': sec_type,
            'username': username,
            'password': password,
            'orig_username': orig_username,
        }

    def _decrypt_password(self, password):
        if password and hasattr(self.server, 'decrypt'):
            try:
                return self.server.decrypt(password)
            except Exception:
                pass
        return password

    def _resolve_url_path(self, channel_config):
        url_path = channel_config.get('url_path', '/')
        path_params = _parse_key_value_params(self.request.input.get('path_params', ''))
        if path_params:
            try:
                url_path = url_path.format(**path_params)
            except (KeyError, ValueError):
                pass
        return url_path

    def _build_temp_wrapper(self, channel_config, sec_config, url_path):
        """ Builds a temporary HTTPSOAPWrapper pointing at the local channel URL. """
        port = getattr(self.server, 'port', 17010)
        method = self.request.input.get('request_method', '') or 'POST'
        query_params = _parse_key_value_params(self.request.input.get('query_params', ''))

        wrapper_config = {
            'id': 'temp-invoke-{}'.format(self.cid),
            'is_active': True,
            'method': method,
            'data_format': 'json',
            'name': 'temp-invoke-channel-{}'.format(self.cid),
            'transport': 'plain_http',
            'address_host': 'http://127.0.0.1:{}'.format(port),
            'address_url_path': url_path,
            'soap_action': '',
            'soap_version': None,
            'ping_method': 'HEAD',
            'pool_size': 1,
            'serialization_type': 'json',
            'timeout': 90,
            'content_type': None,
            'validate_tls': False,
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
        method = self.request.input.get('request_method', '') or 'POST'
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
    """ Invokes an existing REST outgoing connection by its ID. """

    name = 'zato.http-soap.invoke-outconn'
    input = 'id', '-payload', '-request_method', '-query_params', '-path_params'
    output = '-status_code', '-response_body', '-response_time'

    def handle(self):
        outconn_config = self._get_outconn_config(self.request.input.id)
        outconn_name = outconn_config['name']

        method = self.request.input.get('request_method', '') or 'POST'
        payload = self.request.input.get('payload', '') or ''
        params = self._build_params()

        result = self._invoke_outconn(outconn_name, method, payload, params)
        _set_invoke_response(self, result)

    def _get_outconn_config(self, outconn_id):
        for item in self.server.config_store.get_list('outgoing_rest'):
            if str(item.get('id')) == str(outconn_id) or item.get('name') == str(outconn_id):
                return item
        raise Exception('REST outgoing connection `{}` not found'.format(outconn_id))

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
