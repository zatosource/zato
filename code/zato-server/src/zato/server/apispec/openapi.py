# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from itertools import chain

# Bunch
from bunch import Bunch, bunchify

# PyYAML
from yaml import dump as yaml_dump, Dumper as YAMLDumper

# Zato
from zato.common import URL_TYPE
from zato.common.util import fs_safe_name

# ################################################################################################################################

class OpenAPIGenerator(object):
    """ Generates OpenAPI specifications.
    """
    def __init__(self, data, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path):
        self.data = data
        self.channel_data = channel_data
        self.needs_api_invoke = needs_api_invoke
        self.needs_rest_channels = needs_rest_channels
        self.api_invoke_path = api_invoke_path or []

# ################################################################################################################################

    def _get_response_name(self, service_name):
        return b'response_{}'.format(fs_safe_name(service_name))

# ################################################################################################################################

    def _get_response_schemas(self, data):

        out = Bunch()

        for item in data.services:

            response_name = self._get_response_name(item.name)
            out[response_name] = {
                b'title': b'Response object for {}'.format(item.name),
                b'type': b'object',
            }
            properties = {}
            out[response_name][b'properties'] = properties

            if 'openapi_v3' not in item.simple_io:
                continue

            output_required_names = [elem.name.encode('utf8') for elem in item.simple_io.openapi_v3.output_required]

            output_required = item.simple_io.openapi_v3.output_required
            output_optional = item.simple_io.openapi_v3.output_optional

            if output_required or output_optional:
                for sio_elem in chain(output_required, output_optional):
                    properties[sio_elem.name.encode('utf8')] = {
                        b'type': sio_elem.type.encode('utf8'),
                        b'format': sio_elem.subtype.encode('utf8'),
                    }

                if output_required_names:
                    out[response_name][b'required'] = output_required_names

        return out

# ################################################################################################################################

    def get_rest_channel(self, service_name):
        for channel_item in self.channel_data:
            if channel_item['service_name'] == service_name:
                if channel_item['transport'] == URL_TYPE.PLAIN_HTTP:
                    return bunchify(channel_item)

# ################################################################################################################################

    def get_path_operation(self, service_name):
        service_name = service_name.split('.') # E.g. my.api.name.get-client -> ['my', 'api', 'name', 'get-client']
        op_name = service_name[-1]

        if op_name.startswith('get'):
            return b'get'
        elif op_name.startswith('delete'):
            return b'delete'
        else:
            return b'post'

# ################################################################################################################################

    def has_path_elem(self, url_path, elem_name):
        pattern = '{%s}' %  elem_name
        return pattern in url_path

# ################################################################################################################################

    def generate(self):
        # Basic information, always available
        out = Bunch()
        out.openapi = b'3.0.0'
        out.info = {
            b'title': b'API spec',
            b'version': b'1.0',
        }
        out.servers = [{b'url': b'http://localhost:11223'}]

        # Responses to refer to in paths
        out.components = Bunch()
        out.components.schemas = Bunch()

        # REST paths
        out.paths = Bunch()

        # Schemas for all services - it is possible that not all of them will be output,
        # for instance, if a service is not exposed through any REST channel.
        schemas = self._get_response_schemas(self.data)

        for item in self.data.services:

            # Container for all the URL paths found for this item (service)
            url_paths = []

            # Generic API invoker, e.g. /zato/api/invoke/{service_name}
            if self.needs_api_invoke and self.api_invoke_path:
                for path in self.api_invoke_path:
                    url_paths.append(path.format(service_name=item.name).encode('utf8'))

            # Per-service specific REST channel
            if self.needs_rest_channels:
                rest_channel = self.get_rest_channel(item.name)
                if rest_channel:
                    url_paths.append(rest_channel.url_path)

            for url_path in url_paths:
                channel_params = []
                response_name = self._get_response_name(item.name)
                path_operation = self.get_path_operation(item.name)
                out.components.schemas[response_name] = schemas.get(response_name)

                if 'openapi_v3' in item.simple_io:
                    input_required = item.simple_io.openapi_v3.input_required
                    input_optional = item.simple_io.openapi_v3.input_optional

                    for sio_elem in chain(input_required, input_optional):

                        is_in_path = self.has_path_elem(url_path, sio_elem.name)
                        is_required = True if is_in_path else sio_elem.is_required

                        channel_params.append({
                            b'name': sio_elem.name.encode('utf8'),
                            b'description': b'',
                            b'in': b'path' if is_in_path else b'query',
                            b'required': is_required,
                            b'schema': {
                                b'type': sio_elem.type.encode('utf8'),
                                b'format': sio_elem.subtype.encode('utf8'),
                            }
                        })

                out.paths[url_path] = {}
                out.paths[url_path][path_operation] = {}
                out.paths[url_path][path_operation][b'parameters'] = channel_params
                out.paths[url_path][path_operation][b'responses'] = {
                    b'200': {
                        b'description': b'',
                        b'content': {
                            b'application/json': {
                                b'schema': {
                                    b'$ref': b'#/components/schemas/{}'.format(response_name),
                                }
                            }
                        }
                    }
                }

        return yaml_dump(out.toDict(), Dumper=YAMLDumper, default_flow_style=False)

# ################################################################################################################################
