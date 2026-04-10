# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.json_internal import dumps
from zato.server.service import AsIs, Boolean, Integer
from zato.server.service.internal import AdminService

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
            svc_id = self.server.service_store.impl_name_to_id.get(svc_data.get('impl_name'), 0)
            out[name] = svc_id
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
                item.setdefault('security_id', sec_def.get('id'))
                item.setdefault('sec_type', sec_def.get('sec_type') or sec_def.get('type'))
            else:
                item.setdefault('security_id', None)
                item.setdefault('sec_type', None)

            svc_name = item.get('service') or item.get('service_name')
            item.setdefault('service_name', svc_name)
            item.setdefault('service_id', svc_lookup.get(svc_name, 0) if svc_name else None)

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
