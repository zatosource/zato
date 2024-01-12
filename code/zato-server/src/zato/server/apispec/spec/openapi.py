# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Bunch
from bunch import Bunch, bunchify

# Parse
from parse import parse

# PyYAML
from yaml import dump as yaml_dump, Dumper as YAMLDumper

# Zato
from zato.common.api import URL_TYPE
from zato.common.marshal_.api import Model
from zato.common.typing_ import cast_
from zato.common.util.file_system import fs_safe_name
from zato.common.util.import_ import import_string
from zato.server.apispec.parser.service import build_field_list

# Zato - Cython
from zato.simpleio import SIO_TYPE_MAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist, dictlist, stranydict, strorlist
    from zato.server.apispec.model import FieldInfo
    FieldInfo = FieldInfo

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_SIO_TYPE_MAP = SIO_TYPE_MAP()

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIGenerator:
    """ Generates OpenAPI specifications.
    """
    def __init__(
        self,
        data,                # type: dictlist
        channel_data,        # type: dictlist
        needs_api_invoke,    # type: bool
        needs_rest_channels, # type: bool
        api_invoke_path      # type: strorlist
        ) -> 'None':

        self.data = data
        self.channel_data = channel_data
        self.needs_api_invoke = needs_api_invoke
        self.needs_rest_channels = needs_rest_channels

        if api_invoke_path:
            api_invoke_path = api_invoke_path if isinstance(api_invoke_path, list) else [api_invoke_path]
        else:
            api_invoke_path = []

        self.api_invoke_path = api_invoke_path

# ################################################################################################################################

    def _get_request_name(self, service_name:'str') -> 'str':
        return 'request_{}'.format(fs_safe_name(service_name))

# ################################################################################################################################

    def _get_response_name(self, service_name:'str') -> 'str':
        return 'response_{}'.format(fs_safe_name(service_name))

# ################################################################################################################################

    def _add_model_schema(self, model_name:'str', model:'Model', out:'anydict') -> 'None':

        # Do not visit the model if we have already seen it
        if model_name in out:
            return
        else:
            out[model_name] = {}

        # Extract elements from the model object ..
        sio_elems = build_field_list(model, _SIO_TYPE_MAP.OPEN_API_V3)

        # .. and visit each of them, potentially recursing back into our function.
        self._visit_sio_elems(model_name, sio_elems, out)

# ################################################################################################################################

    def _visit_sio_elems(self, schema_name:'str', sio_elems:'anylist', out:'anydict') -> 'None':

        properties = {} # type: stranydict
        out[schema_name]['properties'] = properties

        # All the elements of this model that are required
        elems_required_names = [elem.name for elem in sio_elems if elem.is_required]

        # Go through each SIO element to build an OpenAPI property for it ..
        for info in sio_elems:
            info = cast_('FieldInfo', info)

            # .. this key will always exist ..
            property_map = {
                'description': info.description
            } # type: stranydict

            # .. for nested models, ref will exist ..
            if info.ref:

                # .. out of which we can extract a Python class name ..
                model_name = info.ref.replace('#/components/schemas/', '')

                # .. list elements will have type/items sub-elements ..
                if info.is_list:

                    property_map['type'] = 'array'
                    property_map['items'] = {
                        '$ref': info.ref
                    }

                # .. while non-list elements get the $ref element directly ..
                else:
                    property_map['$ref'] = info.ref

                # .. now, a model (class) ..
                model = import_string(model_name)

                # .. next, we can append this class's definitions to our dictionary of schemas ..
                self._add_model_schema(model_name, model, out)

            # .. while for simple types, these two will exist ..
            else:
                property_map['type'] = info.type

                if info.type == 'array':
                    property_map['items'] = {}

                elif info.type == 'object':
                    property_map['additionalProperties'] = {}

            # .. now, we can assign the property to its container.
            properties[info.name] = property_map

        if elems_required_names:
            out[schema_name]['required'] = elems_required_names

# ################################################################################################################################

    def _get_message_schemas(self, data:'dictlist', is_request:'bool') -> 'Bunch':

        if is_request:
            name_func = self._get_request_name
            msg_name = 'Request'
            sio_elem_attr = 'input'
        else:
            name_func = self._get_response_name
            msg_name = 'Response'
            sio_elem_attr = 'output'

        # All schema objects for input request or response
        out = Bunch()

        # Go through all the services ..
        for item in data:

            # .. skip it unless we can support OpenAPI ..
            if 'openapi_v3' not in item['simple_io']:
                continue

            # .. turn its class name into a schema name ..
            message_name = name_func(item['name'])

            # .. prepare it upfront here ..
            out[message_name] = {
                'title': '{} object for {}'.format(msg_name, item['name']),
                'type': 'object',
            }

            # .. get all the elements of the model class ..
            sio_elems = getattr(item['simple_io']['openapi_v3'], sio_elem_attr)

            # .. turn them into an OpenAPI schema ..
            self._visit_sio_elems(message_name, sio_elems, out)

        # .. and return our result to the caller.
        return out

# ################################################################################################################################

    def get_rest_channel(self, service_name:'str') -> 'anydictnone':
        for channel_item in self.channel_data:
            if channel_item['service_name'] == service_name:
                if channel_item['transport'] == URL_TYPE.PLAIN_HTTP:
                    return bunchify(channel_item)

# ################################################################################################################################

    def get_path_operation(self, service_name:'str') -> 'str':
        service_name_list = service_name.split('.') # E.g. my.api.name.get-client -> ['my', 'api', 'name', 'get-client']
        op_name = service_name_list[-1]

        if op_name.startswith('get'):
            return 'get'
        elif op_name.startswith('delete'):
            return 'delete'
        else:
            return 'post'

# ################################################################################################################################

    def has_path_elem(self, url_path:'str', elem_name:'str') -> 'bool':
        pattern = '{%s}' % elem_name
        return pattern in url_path

# ################################################################################################################################

    def generate(self) -> 'str':

        # Local aliases
        sec_name = 'BasicAuth'

        # Basic information, always available
        out = Bunch()
        out.openapi = '3.0.3'
        out.info = {
            'title': 'API spec',
            'version': '1.0',
        }
        out.servers = [{'url': 'http://127.0.0.1:17010'}]

        # Responses to refer to in paths
        out.components = Bunch()
        out.components.schemas = Bunch()

        # Security definition ..
        out.components['securitySchemes'] = {}
        out.components['securitySchemes'][sec_name] = {}
        out.components['securitySchemes'][sec_name]['type']   = 'http'
        out.components['securitySchemes'][sec_name]['scheme'] = 'basic'

        # .. apply the definition globally.
        out['security'] = []
        out['security'].append({sec_name:[]})

        # REST paths
        out.paths = Bunch()

        # Schemas for all services - it is possible that not all of them will be output,
        # for instance, if a service is not exposed through any REST channel.
        request_schemas  = self._get_message_schemas(self.data, True)
        response_schemas = self._get_message_schemas(self.data, False)

        schemas = {}
        schemas.update(request_schemas)
        schemas.update(response_schemas)

        out.components.schemas.update(schemas)

        for item in self.data:

            # Container for all the URL paths found for this item (service)
            url_paths = []

            # Parameters carried in URL paths, e.g. /user/{username}/{lang_code},
            # all of them will be treated as required and all of them will be string ones.
            channel_params = []

            # Now, collect all the paths that the spec will contain ..

            # .. generic API invoker, e.g. /zato/api/invoke/{service_name} ..
            if self.needs_api_invoke and self.api_invoke_path:
                for path in self.api_invoke_path:
                    url_paths.append(path.format(service_name=item['name']))

            # .. per-service specific REST channels.
            if self.needs_rest_channels:
                rest_channel = self.get_rest_channel(item['name'])

                if rest_channel:

                    # This is always needed, whether path parameters exist or not
                    url_paths.append(rest_channel['url_path'])

                    # Path parameters
                    group_names = rest_channel['match_target_compiled'].group_names
                    if group_names:

                        # Populate details of path parameters
                        for channel_param_name in sorted(group_names):
                            channel_params.append({
                                'name': channel_param_name,
                                'description': '',
                                'in': 'path',
                                'required': True,
                                'schema': {
                                    'type': 'string',
                                    'format': 'string',
                                }
                            })

            # Translate the service name into a normalised form
            service_name_fs = fs_safe_name(item['name'])

            for url_path in url_paths:

                out_path = out.paths.setdefault(url_path, Bunch()) # type: Bunch
                post = out_path.setdefault('post', Bunch()) # type: Bunch

                operation_id = 'post_{}'.format(fs_safe_name(url_path))

                request_name  = self._get_request_name(service_name_fs)
                response_name = self._get_response_name(service_name_fs)

                request_ref  = '#/components/schemas/{}'.format(request_name)
                response_ref = '#/components/schemas/{}'.format(response_name)

                request_body = Bunch()
                request_body.required = True

                request_body.content = Bunch()
                request_body.content['application/json'] = Bunch()
                request_body.content['application/json'].schema = Bunch()
                request_body.content['application/json'].schema['$ref'] = request_ref

                responses = Bunch()
                responses['200'] = Bunch()
                responses['200'].description = ''
                responses['200'].content = Bunch()
                responses['200'].content['application/json'] = Bunch()
                responses['200'].content['application/json'].schema = Bunch()
                responses['200'].content['application/json'].schema['$ref'] = response_ref

                post['operationId'] = operation_id
                post['requestBody'] = request_body
                post['responses']   = responses

                if channel_params:

                    # Whether this "url_path" should receive the channel parameters
                    should_attach = True

                    # The channel parameters dictionary needs to be ignored
                    # if the channel is actually an API invoker, i.e. these parameters
                    # should only be used with channels that are dedicated to a service
                    # because this is where they were extracted from.

                    # Iterate over all the API invokers ..
                    for path_pattern in self.api_invoke_path:

                        # .. if we have a match, it means that "url_path" is actually
                        # .. a path pointing to an API invoker, in which case we ignore it,
                        # .. meaning that we will not attach channel parameters to it.
                        if parse(path_pattern, url_path):
                            should_attach = False
                            break

                    # If we are here, it means that "url_path" is a standalone REST channel,
                    # which means that it will get its path parameters.
                    if should_attach:
                        post['parameters'] = channel_params

        return yaml_dump(out.toDict(), Dumper=YAMLDumper, default_flow_style=False)

# ################################################################################################################################
# ################################################################################################################################
