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

        if api_invoke_path:
            api_invoke_path = api_invoke_path if isinstance(api_invoke_path, list) else [api_invoke_path]
        else:
            api_invoke_path = []

        self.api_invoke_path = api_invoke_path

# ################################################################################################################################

    def _get_response_name(self, service_name):
        return 'response_{}'.format(fs_safe_name(service_name))

# ################################################################################################################################

    def _get_response_schemas(self, data):

        out = Bunch()

        for item in data.services:

            response_name = self._get_response_name(item.name)
            out[response_name] = {
                'title': 'Response object for {}'.format(item.name),
                'type': 'object',
            }
            properties = {}
            out[response_name]['properties'] = properties

            if 'openapi_v3' not in item.simple_io:
                continue

            output_required_names = [elem.name for elem in item.simple_io.openapi_v3.output_required]

            output_required = item.simple_io.openapi_v3.output_required
            output_optional = item.simple_io.openapi_v3.output_optional

            if output_required or output_optional:
                for sio_elem in chain(output_required, output_optional):
                    properties[sio_elem.name] = {
                        'type': sio_elem.type,
                        'format': sio_elem.subtype,
                    }

                if output_required_names:
                    out[response_name]['required'] = output_required_names

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
            return 'get'
        elif op_name.startswith('delete'):
            return 'delete'
        else:
            return 'post'

# ################################################################################################################################

    def has_path_elem(self, url_path, elem_name):
        pattern = '{%s}' %  elem_name
        return pattern in url_path

# ################################################################################################################################

    def generate(self):
        # Basic information, always available
        out = Bunch()
        out.openapi = '3.0.0'
        out.info = {
            'title': 'API spec',
            'version': '1.0',
        }
        out.servers = [{'url': 'http://localhost:11223'}]

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
                    url_paths.append(path.format(service_name=item.name))

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
                            'name': sio_elem.name,
                            'description': sio_elem.description,
                            'in': 'path' if is_in_path else 'query',
                            'required': is_required,
                            'schema': {
                                'type': sio_elem.type,
                                'format': sio_elem.subtype,
                            }
                        })

                out.paths[url_path] = {}
                out.paths[url_path][path_operation] = {}
                out.paths[url_path][path_operation]['parameters'] = channel_params
                out.paths[url_path][path_operation]['responses'] = {
                    '200': {
                        'description': '',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/{}'.format(response_name),
                                }
                            }
                        }
                    }
                }

        return yaml_dump(out.toDict(), Dumper=YAMLDumper, default_flow_style=False)

# ################################################################################################################################

'''
openapi: 3.0.0
info:
    title: API spec
    version: '1.0'
components:
  schemas:
    request_api_my_service_1:
      title: Request object for api.my.service.1
      type: object
      properties:
        user_id:
          type: integer
          format: int32
        user_name:
          format: string
          type: string
      required:
      - user_id
      - user_name
    response_api_my_service_1:
      title: Response object for api.my.service.1
      type: object
      properties:
        customer_id:
          type: integer
          format: int32
      required:
      - customer_id
paths:
    /zato/api/invoke/api.my.service.1:
        post:
            operationId: post_api_my_service_1
            consumes:
                - application/json
            requestBody:
                required: true
                content:
                    application/json:
                        schema:
                            $ref: '#/components/schemas/request_api_my_service_1'
            responses:
              '200':
                content:
                  application/json:
                    schema:
                      $ref: '#/components/schemas/response_api_my_service_1'
                description: ''

servers:
- url: http://localhost:11223
'''
