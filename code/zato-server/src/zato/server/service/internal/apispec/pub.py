# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json
import pkg_resources
import re

# Paste
from paste.util.converters import asbool

# Zato
from zato.common.match import Matcher
from zato.common.util import get_brython_js
from zato.server.connection.http_soap import NotFound
from zato.server.service import Service

# ################################################################################################################################

class _Base(Service):

    def validate_input(self):
        if not asbool(self.server.fs_server_config.apispec.pub_enabled):

            # Note that we are using the same format that regular 404 does
            raise NotFound(self.cid, '[{}] Unknown URL:[{}] or SOAP action:[]'.format(
                self.cid, self.wsgi_environ['zato.channel_item']['url_path']))

# ################################################################################################################################

class Main(_Base):
    """ Returns public version of API specifications.
    """
    def filter_services(self, matcher, services):
        return [svc for svc in services if matcher.is_allowed(svc['name'])]

# ################################################################################################################################

    def get_filtered_apispec_response(self):
        """Return zato.apispec.get-api-spec response filtered according to apispec_services_allowed config."""
        matcher = Matcher()
        matcher.read_config(self.server.fs_server_config.apispec_services_allowed)

        response = json.loads(self.invoke('zato.apispec.get-api-spec', {'return_internal': True}))
        response['services'] = self.filter_services(matcher, response['services'])

        # Remove any namespace definitions for which no service matched.
        for namespace, info in list(response['namespaces'].items()):
            info['services'] = self.filter_services(matcher, info['services'])
            if not info['services']:
                del response['namespaces'][namespace]

        return json.dumps(response)

# ################################################################################################################################

    def handle(self):
        replace_with = {
            'ZATO_BASE_CSS': pkg_resources.resource_string(__name__, 'data/style.css').decode('utf-8'),
            'ZATO_CLUSTER_ID': str(self.server.cluster_id),
            'ZATO_DATA': self.get_filtered_apispec_response(),
            'ZATO_LOGO': pkg_resources.resource_string(__name__, 'data/logo.png').encode('base64'),
            'ZATO_PUB_CSS_STYLE': self.server.fs_server_config.apispec.pub_css_style,
            'ZATO_PUB_NAME': self.server.fs_server_config.apispec.pub_name,
        }

        page_template = pkg_resources.resource_string(__name__, 'data/index.html').decode('utf-8')
        replace = lambda match: replace_with[match.group(1)]
        self.response.payload = re.sub('{{([^}]+)}}', replace, page_template)
        self.response.headers['Content-Type'] = 'text/html'

# ################################################################################################################################

class BrythonJS(_Base):
    """ Returns Brython's main source code module.
    """
    def handle(self):
        self.response.payload = get_brython_js()
        self.response.headers['Content-Type'] = 'text/javascript'

# ################################################################################################################################

class BrythonJSON(_Base):
    """ Brython's 'json' module.
    """
    def handle(self):
        _json = """var $module = (function($B){

return  {
    loads : function(json_obj){
        return $B.jsobject2pyobject(JSON.parse(json_obj))
    },
    load : function(file_obj){
        return $module.loads(file_obj.$content);
    },
    dumps : function(obj){return JSON.stringify($B.pyobject2jsobject(obj))},
}

})(__BRYTHON__)
"""
        self.response.payload = _json
        self.response.headers['Content-Type'] = 'text/javascript'

# ################################################################################################################################

class Frontend(_Base):
    """ Returns Brython frontend code to display API specifications.
    """
    def handle(self):
        self.response.payload = pkg_resources.resource_string(__name__, 'data/docs.py')
        self.response.headers['Content-Type'] = 'text/python'

# ################################################################################################################################

class GetDefaultAuthType(Service):
    """ Returns default authentication method to use for clients (browsers) accessing public API specifications.
    """
    class SimpleIO:
        output_required = ('auth_type',)

    def handle(self):
        self.response.payload.auth_type = 'Basic realm="{}"'.format(self.server.fs_server_config.apispec.pub_name)


"""
# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from itertools import chain
from operator import attrgetter
import os

# Bunch
from bunch import Bunch, bunchify

# PyYAML
from yaml import dump as yaml_dump, Dumper as YAMLDumper

# Zato
from zato.common.util import fs_safe_name
from zato.server.apispec import Generator
from zato.server.apispec.wsdl import WSDLGenerator
from zato.server.service import Int, Float, Opaque, Service

# ################################################################################################################################

no_value = '---'
col_sep = ' ' # Column separator
len_col_sep = len(col_sep)

# ################################################################################################################################

class GetSphinx(Service):
    """ Generates API docs in Sphinx.

    It may also embolden things otherwise unheard of to come into existence.
    """
    name = 'apispec.get-sphinx'

    class SimpleIO:
        input_required = Opaque('data'),
        input_optional = (Int('aaa'), Int('bbbb.zzzz'), 'aaa', 'ggg')
        output_required = Opaque('data'),
        output_optional = (Int('ccc'), Int('ddd.eee'))

# ################################################################################################################################

    def add_default_files(self, files):
        """ Returns default static files that always exist.
        """
        apispec_dir = os.path.join(self.server.static_dir, 'sphinxdoc', 'apispec')
        for dir_path, dir_names, file_names in os.walk(apispec_dir):
            if dir_path == apispec_dir:
                base_dir = '.'
            else:
                base_dir = os.path.basename(dir_path)

            for file_name in file_names:
                relative_path = os.path.join(base_dir, file_name)

                f = open(os.path.join(dir_path, file_name))
                contents = f.read()
                f.close()

                files[relative_path] = contents

# ################################################################################################################################

    def get_wsdl(self, data):
        services = bunchify(data['services'])
        target_ns = 'urn:zato-apispec'
        return WSDLGenerator(services, target_ns).generate()

# ################################################################################################################################

    def get_service_table_line(self, ns, name, docs, sio):
        name_fs_safe = 'service_{}'.format(fs_safe_name(name))
        file_name = '{}.rst'.format(name_fs_safe)

        return bunchify({
            'ns': ns or no_value,
            'orig_name': name,
            'sphinx_name': name.replace('_', '\_'), # Needed for Sphinx to ignore undescores
            'name': name_fs_safe,
            'name_link': """:doc:`{} <./{}>`""".format(name, name_fs_safe),
            'file_name': file_name,
            'description': docs.summary or no_value,
            'docs': docs,
            'sio': sio
        })

# ################################################################################################################################

    def write_separators(self, buff, border1, border2, border3):
        buff.write(border1)
        buff.write(col_sep)

        buff.write(border2)
        buff.write(col_sep)

        buff.write(border3)
        buff.write(col_sep)

        buff.write('\n')

# ################################################################################################################################

    def write_sio(self, buff, elems):

        sio_lines = []
        longest_name = 4     # len('Name')
        longest_datatype = 8 # len('Datatype')
        longest_required = 8 # len('Required')

        for elem in elems:
            elem_name = elem.name.replace('_', '\_') # Sphinx treats _ as hyperlinks
            longest_name = max(longest_name, len(elem_name))
            longest_datatype = max(longest_datatype, len(elem.subtype))

            sio_lines.append(bunchify({
                'name': elem_name,
                'datatype': elem.subtype,
                'is_required': elem.is_required,
                'is_required_str': 'Yes' if elem.is_required else no_value,
            }))

        longest_name += len_col_sep
        longest_datatype += len_col_sep

        name_border = '=' * longest_name
        datatype_border = '=' * longest_datatype
        required_border = '=' * longest_required

        self.write_separators(buff, name_border, datatype_border, required_border)

        buff.write('Name'.ljust(longest_name))
        buff.write(col_sep)

        buff.write('Datatype'.ljust(longest_datatype))
        buff.write(col_sep)

        buff.write('Required'.ljust(longest_required))
        buff.write(col_sep)
        buff.write('\n')

        self.write_separators(buff, name_border, datatype_border, required_border)

        for item in sio_lines:

            # First, add the services to the main table
            buff.write(item.name.ljust(longest_name))
            buff.write(col_sep)

            buff.write(item.datatype.ljust(longest_datatype))
            buff.write(col_sep)

            buff.write(item.is_required_str.ljust(longest_required))
            buff.write(col_sep)

            buff.write('\n')

        self.write_separators(buff, name_border, datatype_border, required_border)
        buff.write('\n')

# ################################################################################################################################

    def get_service_page(self, item):
        buff = StringIO()

        input_title = 'Input'
        len_input_title = len(input_title)

        output_title = 'Output'
        len_output_title = len(output_title)

        buff.write(item.sphinx_name)
        buff.write('\n')

        buff.write('=' * len(item.sphinx_name))
        buff.write('\n')
        buff.write('\n')

        buff.write(item.docs.full)
        buff.write('\n')
        buff.write('\n')

        # No SimpleIO for that services
        if 'zato' not in item.sio:
            return buff

        input_required = sorted(item.sio.zato.input_required, key=attrgetter('name'))
        input_optional = sorted(item.sio.zato.input_optional, key=attrgetter('name'))
        output_required = sorted(item.sio.zato.output_required, key=attrgetter('name'))
        output_optional = sorted(item.sio.zato.output_optional, key=attrgetter('name'))

        # Input
        buff.write(input_title)
        buff.write('\n')
        buff.write('-' * len_input_title)
        buff.write('\n' * 2)

        if input_required or input_optional:
            self.write_sio(buff, chain(input_required, input_optional))
        else:
            buff.write('(None)')
            buff.write('\n')

        # Output
        buff.write(output_title)
        buff.write('\n')
        buff.write('-' * len_output_title)
        buff.write('\n' * 2)

        if output_required or output_optional:
            self.write_sio(buff, chain(output_required, output_optional))
        else:
            buff.write('(None)')
            buff.write('\n')

        return buff

# ################################################################################################################################

    def add_services(self, data, files):

        buff = StringIO()
        lines = []

        longest_ns = 2    # len('NS')
        longest_name = 4  # len('Name')
        longest_desc = 11 # len('Description')

        for elem in data.services:
            name = elem.name
            ns = elem.namespace_name
            docs = elem.docs
            sio = elem.simple_io

            service_line = self.get_service_table_line(ns, name, docs, sio)
            lines.append(service_line)

            longest_ns = max(longest_ns, len(service_line.ns))
            longest_name = max(longest_name, len(service_line.name_link))
            longest_desc = max(longest_desc, len(service_line.description))

        longest_ns += len_col_sep
        longest_name += len_col_sep

        ns_border = '=' * longest_ns
        name_border = '=' * longest_name
        desc_border = '=' * longest_desc

        self.write_separators(buff, ns_border, name_border, desc_border)

        buff.write('NS'.ljust(longest_ns))
        buff.write(col_sep)

        buff.write('Name'.ljust(longest_name))
        buff.write(col_sep)

        buff.write('Description'.ljust(longest_desc))
        buff.write(col_sep)
        buff.write('\n')

        self.write_separators(buff, ns_border, name_border, desc_border)

        for item in lines:

            # First, add the services to the main table
            buff.write(item.ns.ljust(longest_ns))
            buff.write(col_sep)

            buff.write(item.name_link.ljust(longest_name))
            buff.write(col_sep)

            buff.write(item.description.ljust(longest_desc))
            buff.write(col_sep)

            buff.write('\n')

            # Now, create a description file for each service
            files[item.file_name] = self.get_service_page(item).getvalue()

        # Finish the table
        self.write_separators(buff, ns_border, name_border, desc_border)

        # Save the table's contents
        files['services.rst'] = buff.getvalue()

# ################################################################################################################################

    def handle(self):
        data = bunchify(self.request.input.data)
        files = {}

        self.add_default_files(files)
        self.add_services(data, files)
        files['download/api.wsdl'] = self.get_wsdl(data)

        self.response.payload.data = files

# ################################################################################################################################

class GetOpenAPI(Service):
    """ Generates OpenAPI specifications

    Possibly other things too.
    """
    name = 'apispec.get-openapi'

    class SimpleIO:
        input_optional = ('data',)

# ################################################################################################################################

    def _get_response_name(self, service_name):
        return b'response_{}'.format(fs_safe_name(service_name))

# ################################################################################################################################

    def _get_response_schemas(self, data):

        out = Bunch()

        for item in data.services:

            response_name = self._get_response_name(item.name)
            output_required_names = [elem.name.encode('utf8') for elem in item.simple_io.openapi_v3.output_required]

            output_required = item.simple_io.openapi_v3.output_required
            output_optional = item.simple_io.openapi_v3.output_optional

            properties = {}
            if output_required or output_optional:
                for out_elem in chain(output_required, output_optional):
                    properties[out_elem.name.encode('utf8')] = {
                        b'type': out_elem.type.encode('utf8'),
                        b'format': out_elem.subtype.encode('utf8'),
                    }

            out[response_name] = {
                b'title': b'Response object for {}'.format(item.name),
                b'type': b'object',
            }

            if output_required_names:
                out[response_name][b'required'] = output_required_names

            if properties:
                out[response_name][b'properties'] = properties

        return out

# ################################################################################################################################

    def handle(self):
        data = Generator(self.server.service_store.services, self.server.sio_config, '').get_info(ignore_prefix='zato')
        data = bunchify(data)

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
        out.components.schemas = self._get_response_schemas(data)

        _yaml = yaml_dump(out.toDict(), Dumper=YAMLDumper, default_flow_style=False)

        print(_yaml)

# ################################################################################################################################

'''
openapi: '3.0.0'
info:
  title: API spec
  version: '1.0'

servers:
- url: http://localhost:11223

paths:
  /zzz:
    get:
      parameters:
        - name: q
          description: ''
          in: query
          required: true
          schema:
            type: string

      responses:
        200:
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/zzz_response'

components:
  schemas:
    zzz_response:
      title: ''
      type: object
      required:
        - qqq
      properties:
        qqq:
          type: string
        aaa:
          type: string'''

# ################################################################################################################################
"""
