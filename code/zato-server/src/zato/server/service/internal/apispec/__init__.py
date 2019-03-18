# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from io import StringIO
from itertools import chain
from operator import attrgetter
import os

# Bunch
from bunch import bunchify

# Zato
from zato.server.apispec.openapi import OpenAPIGenerator
from zato.server.apispec.wsdl import WSDLGenerator
from zato.server.service import List, Opaque, Service

# Zato
from zato.common.util import aslist, fs_safe_name
from zato.common.util.json_ import dumps
from zato.server.apispec import Generator
from zato.server.service import Bool

# ################################################################################################################################

no_value = '---'
col_sep = ' ' # Column separator
len_col_sep = len(col_sep)

# ################################################################################################################################

class GetAPISpec(Service):
    """ Returns API specifications for all services.
    """
    class SimpleIO:
        input_optional = ('cluster_id', 'query', Bool('return_internal'), 'include', 'exclude', 'needs_sphinx',
            'needs_api_invoke', 'needs_rest_channels', 'api_invoke_path')

    def handle(self):
        cluster_id = self.request.input.get('cluster_id')

        include = aslist(self.request.input.include, ',')
        exclude = aslist(self.request.input.exclude, ',')

        include = [elem for elem in include if elem]
        exclude = [elem for elem in exclude if elem]

        api_invoke_path = aslist(self.request.input.api_invoke_path, ',')
        api_invoke_path = [elem for elem in api_invoke_path if elem]

        if not self.request.input.get('return_internal'):
            if 'zato.*' not in exclude:
                exclude.append('zato.*')

        if cluster_id and cluster_id != self.server.cluster_id:
            raise ValueError('Input cluster ID `%s` different than ours `%s`', cluster_id, self.server.cluster_id)

        # Default to Sphinx output unless explicitly overridden
        if isinstance(self.request.input.needs_sphinx, bool):
            needs_sphinx = self.request.input.needs_sphinx
        else:
            needs_sphinx = True

        data = Generator(self.server.service_store.services, self.server.sio_config,
            include, exclude, self.request.input.query).get_info()

        if needs_sphinx:
            out = self.invoke(GetSphinx.get_name(), {
                'data': data,
                'needs_api_invoke': self.request.input.needs_api_invoke,
                'needs_rest_channels': self.request.input.needs_rest_channels,
                'api_invoke_path':api_invoke_path
            })
        else:
            out = data

        self.response.payload = dumps(out)

# ################################################################################################################################

class GetSphinx(Service):
    """ Generates API docs in Sphinx.
    """
    class SimpleIO:
        input_required = Opaque('data')
        input_optional = 'needs_api_invoke', 'needs_rest_channels', List('api_invoke_path')
        output_required = Opaque('data')

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

    def get_wsdl_spec(self, data):
        services = bunchify(data['services'])
        target_ns = 'urn:zato-apispec'
        return WSDLGenerator(services, target_ns).generate()

# ################################################################################################################################

    def get_openapi_spec(self, data, needs_api_invoke, needs_rest_channels, api_invoke_path):
        data = bunchify(data)
        channel_data = self.server.worker_store.request_dispatcher.url_data.channel_data
        generator = OpenAPIGenerator(data, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path)
        return generator.generate()

# ################################################################################################################################

    def get_service_table_line(self, idx, name, docs, sio):
        name_fs_safe = 'service_{}'.format(fs_safe_name(name))
        file_name = '{}.rst'.format(name_fs_safe)

        return bunchify({
            'ns': str(idx),
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

        buff.write('Services\n')
        buff.write('--------\n\n')

        lines = []

        longest_ns = 2    # len('NS')
        longest_name = 4  # len('Name')
        longest_desc = 11 # len('Description')

        for idx, elem in enumerate(data.services, 1):
            name = elem.name
            docs = elem.docs
            sio = elem.simple_io

            service_line = self.get_service_table_line(idx, name, docs, sio)
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

        buff.write('---'.ljust(longest_ns))
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
        req = self.request.input
        data = bunchify(req.data)
        files = {}

        self.add_default_files(files)
        self.add_services(data, files)

        files['download/api.wsdl'] = self.get_wsdl_spec(data)
        files['download/openapi.yaml'] = self.get_openapi_spec(
            data, req.needs_api_invoke, req.needs_rest_channels, req.api_invoke_path)

        self.response.payload.data = files

# ################################################################################################################################
