# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.json_internal import dumps
from zato.server.service import AsIs, Boolean, Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strintdict

# ################################################################################################################################
# ################################################################################################################################

_GetList_Optional = ('include_wrapper', 'cluster_id', 'connection', 'transport', 'data_format', 'needs_security_group_names')

# ################################################################################################################################
# ################################################################################################################################

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
    """ Base class for services returning information about HTTP/SOAP objects.
    """
    class SimpleIO:
        output_required = 'id', 'name', 'is_active', 'is_internal', 'url_path'
        output_optional = 'service_id', 'service_name', 'security_id', 'security_name', 'sec_type', \
            'method', 'soap_action', 'soap_version', 'data_format', 'host', 'ping_method', 'pool_size', 'merge_url_params_req', \
            'url_params_pri', 'params_pri', 'serialization_type', 'timeout', \
            'content_type', 'cache_id', 'cache_name', Integer('cache_expiry'), 'cache_type', \
            'content_encoding', Boolean('match_slash'), 'http_accept', \
                'should_parse_on_input', 'should_validate', 'should_return_errors', \
                'data_encoding', 'username', 'is_wrapper', 'wrapper_type', AsIs('security_groups'), 'security_group_count', \
                'security_group_member_count', 'needs_security_group_names', Boolean('validate_tls'), 'gateway_service_list'

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
    class SimpleIO(_BaseGet.SimpleIO):
        request_elem = 'zato_http_soap_get_request'
        response_elem = 'zato_http_soap_get_response'
        input_optional = 'cluster_id', 'id', 'name', 'connection', 'transport'

    def handle(self):
        input = self.request.input
        name = input.get('name') or input.get('id')
        connection = input.get('connection') or 'channel'
        transport = input.get('transport') or 'plain_http'
        entity_type = _get_entity_type(connection, transport)

        items = self.server.rust_config_store.get_list(entity_type)
        for item in items:
            if item.get('name') == name or str(item.get('id')) == str(name):
                self.response.payload = item
                return

# ################################################################################################################################

class GetList(_BaseGet):
    """ Returns a list of HTTP/SOAP connections.
    """
    class SimpleIO(GetListAdminSIO, _BaseGet.SimpleIO):
        request_elem = 'zato_http_soap_get_list_request'
        response_elem = 'zato_http_soap_get_list_response'
        input_optional = GetListAdminSIO.input_optional + _GetList_Optional
        output_optional = _BaseGet.SimpleIO.output_optional + ('connection', 'transport')
        output_repeated = True

    def handle(self):
        from zato.common.api import Groups

        connection = self.request.input.get('connection') or 'channel'
        transport = self.request.input.get('transport') or 'plain_http'
        include_wrapper = self.request.input.get('include_wrapper') or False
        should_ignore_wrapper = not include_wrapper
        needs_security_group_names = self.request.input.get('needs_security_group_names') or False

        entity_type = _get_entity_type(connection, transport)
        items = self.server.rust_config_store.get_list(entity_type)

        security_groups_member_count = self.invoke('zato.groups.get-member-count', group_type=Groups.Type.API_Clients)

        if needs_security_group_names:
            all_security_groups = self.invoke('zato.groups.get-list', group_type=Groups.Type.API_Clients)
        else:
            all_security_groups = []

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

            out.append(item)

        self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_create_request'
        response_elem = 'zato_http_soap_create_response'
        input_required = 'name', 'url_path', 'connection'
        input_optional = 'service', 'service_id', AsIs('security_id'), 'method', 'soap_action', 'soap_version', 'data_format', \
            'host', 'ping_method', 'pool_size', Boolean('merge_url_params_req'), 'url_params_pri', 'params_pri', \
            'serialization_type', 'timeout', 'content_type', \
            'cache_id', Integer('cache_expiry'), 'content_encoding', Boolean('match_slash'), 'http_accept', \
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding', \
            'is_active', 'transport', 'is_internal', 'cluster_id', \
            'is_wrapper', 'wrapper_type', 'username', 'password', AsIs('security_groups'), Boolean('validate_tls'), \
            'gateway_service_list'
        output_required = 'id', 'name'
        output_optional = 'url_path'

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

        name = input.name
        self.server.rust_config_store.set(entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name
        self.response.payload.url_path = input.url_path

# ################################################################################################################################

class Edit(AdminService):
    """ Updates an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_edit_request'
        response_elem = 'zato_http_soap_edit_response'
        input_required = 'id', 'name', 'url_path', 'connection'
        input_optional = 'service', 'service_id', AsIs('security_id'), 'method', 'soap_action', 'soap_version', \
            'data_format', 'host', 'ping_method', 'pool_size', Boolean('merge_url_params_req'), 'url_params_pri', \
            'params_pri', 'serialization_type', 'timeout', 'content_type', \
            'cache_id', Integer('cache_expiry'), 'content_encoding', Boolean('match_slash'), 'http_accept', \
            'should_parse_on_input', 'should_validate', 'should_return_errors', 'data_encoding', \
            'cluster_id', 'is_active', 'transport', \
            'is_wrapper', 'wrapper_type', 'username', 'password', AsIs('security_groups'), Boolean('validate_tls'), \
            'gateway_service_list'
        output_optional = 'id', 'name'

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

        name = input.name
        old_name = None
        for item in self.server.rust_config_store.get_list(entity_type):
            if str(item.get('id')) == str(input.id):
                old_name = item.get('name')
                break
        if old_name and old_name != name:
            self.server.rust_config_store.delete(entity_type, old_name)

        self.server.rust_config_store.set(entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name

# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_delete_request'
        response_elem = 'zato_http_soap_delete_response'
        input_optional = 'id', 'name', 'connection', 'should_raise_if_missing', 'transport'
        output_optional = 'details'

    def handle(self):

        input = self.request.input
        name = input.get('name') or input.get('id')
        connection = input.get('connection') or 'channel'
        transport = input.get('transport') or 'plain_http'

        if not name:
            raise Exception('Either ID or name are required on input')

        entity_type = _get_entity_type(connection, transport)
        delete_key = None
        for item in self.server.rust_config_store.get_list(entity_type):
            if item.get('name') == name or str(item.get('id')) == str(name):
                delete_key = item['name']
                break

        if not delete_key:
            if input.get('should_raise_if_missing', True):
                raise Exception('HTTP/SOAP object with id or name `{}` not found'.format(name))
            return

        self.server.rust_config_store.delete(entity_type, delete_key)
        self.response.payload.details = 'OK, deleted'

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an HTTP/SOAP connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_http_soap_ping_request'
        response_elem = 'zato_http_soap_ping_response'
        input_required = 'id'
        input_optional = 'ping_path'
        output_required = 'id', 'is_success'
        output_optional = 'info'

    def handle(self):

        name = self.request.input.id

        for entity_type in ('outgoing_rest', 'outgoing_soap'):
            items = self.server.rust_config_store.get_list(entity_type)
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
