# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from io import StringIO
from itertools import chain
from json import dumps
import os

# Bunch
from bunch import bunchify

# Zato
from zato.server.apispec.spec.openapi import OpenAPIGenerator
from zato.server.service import List, Opaque, Service

# Zato
from zato.common.ext.dataclasses import asdict
from zato.common.util.eval_ import as_list
from zato.common.util.file_system import fs_safe_name
from zato.common.util.open_ import open_r
from zato.server.apispec.model import FieldInfo
from zato.server.apispec.spec.core import Generator
from zato.server.service import AsIs, Bool

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# ################################################################################################################################

no_value = '---'
col_sep = ' ' # Column separator
len_col_sep = len(col_sep)

# ################################################################################################################################

def _json_default(value):
    # type: (object) -> object

    if isinstance(value, FieldInfo):
        return asdict(value)
    else:
        return value

# ################################################################################################################################

class GetAPISpec(Service):
    """ Returns API specifications for all services.
    """
    class SimpleIO:
        input_optional = ('cluster_id', 'query', Bool('return_internal'), 'include', 'exclude', 'needs_sphinx',
            'needs_api_invoke', 'needs_rest_channels', 'api_invoke_path', AsIs('tags'))

    def handle(self):

        cluster_id = self.request.input.get('cluster_id')

        include = as_list(self.request.input.include, ',')
        exclude = as_list(self.request.input.exclude, ',')

        include = [elem for elem in include if elem]
        exclude = [elem for elem in exclude if elem]

        api_invoke_path = as_list(self.request.input.api_invoke_path, ',')
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
            include, exclude, self.request.input.query, self.request.input.tags).get_info()

        if needs_sphinx:
            out = self.invoke(GetSphinx.get_name(), {
                'data': data,
                'needs_api_invoke': self.request.input.needs_api_invoke,
                'needs_rest_channels': self.request.input.needs_rest_channels,
                'api_invoke_path':api_invoke_path
            })
        else:
            out = data

        self.response.payload = dumps(out, default=_json_default)

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
        for dir_path, _ignored_dir_names, file_names in os.walk(apispec_dir):
            if dir_path == apispec_dir:
                base_dir = '.'
            else:
                base_dir = os.path.basename(dir_path)

            for file_name in file_names:
                relative_path = os.path.join(base_dir, file_name)

                f = open_r(os.path.join(dir_path, file_name))
                contents = f.read()
                f.close()

                files[relative_path] = contents

# ################################################################################################################################

    def get_openapi_spec(self, data, needs_api_invoke, needs_rest_channels, api_invoke_path):

        data = bunchify(data)
        channel_data = self.server.worker_store.request_dispatcher.url_data.channel_data
        generator = OpenAPIGenerator(data, channel_data, needs_api_invoke, needs_rest_channels, api_invoke_path)
        return generator.generate()

# ################################################################################################################################

    def _make_sphinx_safe(self, data):
        # type: (unicode) -> unicode

        # This is a no-op currently
        return data

# ################################################################################################################################

    def get_service_table_line(self, idx, name, docs, sio):
        name_fs_safe = 'service_{}'.format(fs_safe_name(name))
        file_name = '{}.rst'.format(name_fs_safe)

        summary = docs.summary
        if summary:
            summary = self._make_sphinx_safe(summary)

        return bunchify({
            'ns': unicode(idx),
            'orig_name': name,
            'sphinx_name': name.replace('_', r'\_'), # Needed for Sphinx to ignore undescores # noqa: W605
            'name': name_fs_safe,
            'name_link': """:doc:`{} <./{}>`""".format(name, name_fs_safe),
            'file_name': file_name,
            'description': summary or no_value,
            'docs': docs,
            'sio': sio
        })

# ################################################################################################################################

    def write_separators(self, buff, *borders):

        for border in borders:
            buff.write(border)
            buff.write(col_sep)

        buff.write('\n')

# ################################################################################################################################

    def write_sio(self, buff, input, output):

        # Reusable
        list_suffix = ' (list)'
        len_list_suffix = len(list_suffix)

        sio_lines = []
        longest_name        = 4  # len('Name')
        longest_datatype    = 8  # len('Datatype')
        longest_required    = 8  # len('Required')
        longest_description = 11 # len('Description')

        # The table is within a 'table' block which is why it needs to be indented
        len_table_indent = 3

        # Find the longest elements for each column
        for elem in chain(input, output):
            elem.name_sphinx = elem.name.replace('_', r'\_') # Sphinx treats _ as hyperlinks # noqa: W605

            len_elem_name_sphinx = len(elem.name_sphinx)
            len_elem_subtype     = len(elem.subtype)
            len_elem_description = len(elem.description)

            longest_name        = max(longest_name, len_elem_name_sphinx)
            longest_datatype    = max(longest_datatype, len_elem_subtype + len_list_suffix)
            longest_description = max(longest_description, len_elem_description)

        # We need to know how much to indent multi-line descriptions,
        # this includes all the preceding headers and 1 for each single space.
        description_indent    = ' ' * (
            len_table_indent + \
            longest_name     + \
            len_col_sep      + \
            1                + \
            longest_datatype + \
            len_col_sep      + \
            1                + \
            longest_required + \
            1
        )
        new_line_with_indent = '\n\n' + description_indent

        for elem in chain(input, output):

            elem.description = elem.description.replace('\n', new_line_with_indent)

            sio_lines.append(bunchify({
                'name': elem.name_sphinx,
                'datatype': elem.subtype + (list_suffix if elem.is_list else ''),
                'is_required': elem.is_required,
                'is_required_str': 'Yes' if elem.is_required else no_value,
                'description': elem.description,
            }))

        longest_name += len_col_sep
        longest_datatype += len_col_sep

        name_border = '=' * longest_name
        datatype_border = '=' * longest_datatype
        required_border = '=' * longest_required
        description_border = '=' * longest_description

        table_indent = ' ' * len_table_indent

        # Left-align the table
        buff.write('.. table::\n')
        buff.write(table_indent) # Note no \n here
        buff.write(':align: left\n\n')

        buff.write(table_indent)
        self.write_separators(buff, name_border, datatype_border, required_border, description_border)

        buff.write(table_indent)
        buff.write('Name'.ljust(longest_name))
        buff.write(col_sep)

        buff.write('Datatype'.ljust(longest_datatype))
        buff.write(col_sep)

        buff.write('Required'.ljust(longest_required))
        buff.write(col_sep)

        buff.write('Description'.ljust(longest_description))
        buff.write(col_sep)
        buff.write('\n')

        buff.write(table_indent)
        self.write_separators(buff, name_border, datatype_border, required_border, description_border)

        for item in sio_lines:

            buff.write(table_indent)

            # First, add the services to the main table
            buff.write(item.name.ljust(longest_name))
            buff.write(col_sep)

            buff.write(item.datatype.ljust(longest_datatype))
            buff.write(col_sep)

            buff.write(item.is_required_str.ljust(longest_required))
            buff.write(col_sep)

            buff.write((item.description or '---').ljust(longest_description))
            buff.write(col_sep)

            buff.write('\n')

        buff.write(table_indent)
        self.write_separators(buff, name_border, datatype_border, required_border, description_border)
        buff.write('\n')

# ################################################################################################################################

    def get_service_page(self, item):
        buff = StringIO()

        input_title = 'Input'
        len_input_title = len(input_title)

        output_title = 'Output'
        len_output_title = len(output_title)

        _ = buff.write(item.sphinx_name)
        _ = buff.write('\n')

        _ = buff.write('=' * len(item.sphinx_name))
        _ = buff.write('\n')
        _ = buff.write('\n')

        docs_full = self._make_sphinx_safe(item.docs.full)

        _ = buff.write(docs_full)
        _ = buff.write('\n')
        _ = buff.write('\n')

        # No SimpleIO for that services
        if 'zato' not in item.sio or (not item.sio.zato):
            return buff

        input_required = item.sio.zato.input_required
        input_optional = item.sio.zato.input_optional

        output_required = item.sio.zato.output_required
        output_optional = item.sio.zato.output_optional

        # Input
        _ = buff.write(input_title)
        _ = buff.write('\n')
        _ = buff.write('-' * len_input_title)
        _ = buff.write('\n' * 2)

        if input_required or input_optional:
            self.write_sio(buff, input_required, input_optional)
        else:
            _ = buff.write('(None)')
            _ = buff.write('\n')
            _ = buff.write('\n')

        # Output
        _ = buff.write(output_title)
        _ = buff.write('\n')
        _ = buff.write('-' * len_output_title)
        _ = buff.write('\n' * 2)

        if output_required or output_optional:
            self.write_sio(buff, output_required, output_optional)
        else:
            _ = buff.write('(None)')
            _ = buff.write('\n')

        return buff

# ################################################################################################################################

    def add_services(self, data, files):

        buff = StringIO()

        _ = buff.write('Services\n')
        _ = buff.write('--------\n\n')

        lines = []

        longest_ns = 2    # len('NS')
        longest_name = 4  # len('Name')
        longest_desc = 11 # len('Description')

        for idx, elem in enumerate(data, 1):
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

        _ = buff.write('---'.ljust(longest_ns))
        _ = buff.write(col_sep)

        _ = buff.write('Name'.ljust(longest_name))
        _ = buff.write(col_sep)

        _ = buff.write('Description'.ljust(longest_desc))
        _ = buff.write(col_sep)
        _ = buff.write('\n')

        self.write_separators(buff, ns_border, name_border, desc_border)

        for item in lines:

            # First, add the services to the main table
            _ = buff.write(item.ns.ljust(longest_ns))
            _ = buff.write(col_sep)

            _ = buff.write(item.name_link.ljust(longest_name))
            _ = buff.write(col_sep)

            _ = buff.write((item.description or '---').ljust(longest_desc))
            _ = buff.write(col_sep)

            _ = buff.write('\n')

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

        files['download/openapi.yaml'] = self.get_openapi_spec(
            data, req.needs_api_invoke, req.needs_rest_channels, req.api_invoke_path)

        self.response.payload.data = files

# ################################################################################################################################
