# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from fnmatch import fnmatch
from inspect import getmodule

# Bunch
from bunch import Bunch, bunchify

# docformatter
from docformatter import format_docstring

# markdown
from markdown import markdown

# Python 2/3 compatibility
from future.utils import iteritems
from past.builtins import basestring

# Zato
from zato.common.api import APISPEC

# Zato - Cython
from zato.simpleio import AsIs, is_sio_bool, is_sio_int, SIO_TYPE_MAP

# ################################################################################################################################

if 0:
    from zato.server.service import Service
    from zato.cy.simpleio import CySimpleIO

    CySimpleIO = CySimpleIO
    Service = Service

# ################################################################################################################################

_sio_attrs = (
    'input_required',
    'input_optional',
    'output_required',
    'output_optional'
)

_SIO_TYPE_MAP = SIO_TYPE_MAP()

# ################################################################################################################################

tag_internal = ('@classified', '@confidential', '@internal', '@private', '@restricted', '@secret')
tag_html_internal = """
.. raw:: html

    <span class="zato-tag-name-highlight">{}</span>
"""

not_public = 'INFORMATION IN THIS SECTION IS NOT PUBLIC'

# ################################################################################################################################

class Config(object):
    def __init__(self):
        self.is_module_level = True
        self.ns = ''
        self.services = []

# ################################################################################################################################

class Docstring(object):
    __slots__ = 'summary', 'description', 'full', 'tags', 'by_tag'

    def __init__(self, tags):
        # type: (list)
        self.summary = ''
        self.description = ''
        self.full = ''
        self.tags = tags
        self.by_tag = {} # Keys are tags used, values are documentation for key

# ################################################################################################################################

class Namespace(object):
    def __init__(self):
        self.name = APISPEC.NAMESPACE_NULL
        self.docs = ''

# ################################################################################################################################

class _DocstringSegment(object):
    __slots__ = 'tag', 'summary', 'description', 'full'

    def __init__(self):
        self.tag = None         # type: str
        self.summary = None     # type: str
        self.description = None # type: str
        self.full = None        # type: str

    def to_dict(self):
        return {
            'tag': self.tag,
            'summary': self.summary,
            'description': self.description,
            'full': self.full,
        }

# ################################################################################################################################

class SimpleIO(object):
    __slots__ = 'input_required', 'output_required', 'input_optional', 'output_optional', 'request_elem', 'response_elem', \
        'spec_name', 'description', 'needs_sio_desc'

    def __init__(self, api_spec_info, description, needs_sio_desc=True):
        # type: (Bunch, SimpleIODescription)
        self.input_required = api_spec_info.param_list.input_required
        self.output_required = api_spec_info.param_list.output_required
        self.input_optional = api_spec_info.param_list.input_optional
        self.output_optional = api_spec_info.param_list.output_optional
        self.request_elem = api_spec_info.request_elem
        self.response_elem = api_spec_info.response_elem
        self.spec_name = api_spec_info.name
        self.description = description
        self.needs_sio_desc = needs_sio_desc

    def to_bunch(self):
        out = Bunch()
        for name in _sio_attrs + ('request_elem', 'response_elem', 'spec_name'):
            out[name] = getattr(self, name)

        if self.needs_sio_desc:
            out.description = self.description.to_bunch()

        return out

# ################################################################################################################################

class SimpleIODescription(object):
    __slots__ = 'input', 'output'

    def __init__(self):
        self.input = {}
        self.output = {}

    def to_bunch(self):
        out = Bunch()
        out.input = self.input
        out.output = self.output

        return out

# ################################################################################################################################

class ServiceInfo(object):
    """ Contains information about a service basing on which documentation is generated.
    """
    def __init__(self, name, service_class, simple_io_config, tags='public', needs_sio_desc=True):
        # type: (str, Service, SimpleIO, object, bool)
        self.name = name
        self.service_class = service_class
        self.simple_io_config = simple_io_config
        self.config = Config()
        self.simple_io = {}
        self.docstring = Docstring(tags if isinstance(tags, list) else [tags])

        self.namespace = Namespace()
        self.invokes = []
        self.invoked_by = []
        self.needs_sio_desc = needs_sio_desc
        self.parse()

# ################################################################################################################################

    def parse(self):
        self.set_config()
        self.set_summary_desc()

# ################################################################################################################################

    def _add_services_from_invokes(self):
        """ Populates the list of services that this services invokes.

        class MyService(Service):
          invokes = 'foo'

        class MyService(Service):
          invokes = ['foo', 'bar']
        """
        invokes = getattr(self.service_class, 'invokes', None)
        if invokes:
            if isinstance(invokes, basestring):
                self.invokes.append(invokes)
            else:
                if isinstance(invokes, (list, tuple)):
                    self.invokes.extend(list(invokes))

# ################################################################################################################################

    def _add_ns_sio(self):
        """ Adds metadata about the service's namespace and SimpleIO definition.
        """
        # Namespace can be declared as a service-level attribute of a module-level one. Former takes precedence.
        service_ns = getattr(self.service_class, 'namespace', APISPEC.NAMESPACE_NULL)
        mod = getmodule(self.service_class)
        mod_ns = getattr(mod, 'namespace', APISPEC.NAMESPACE_NULL)

        self.namespace.name = service_ns if service_ns else mod_ns

        # Set namespace's documentation but only if it was declared top-level and is equal to our own
        if self.namespace.name and self.namespace.name == mod_ns:
            self.namespace.docs = getattr(mod, 'namespace_docs', '')

        # SimpleIO
        sio = getattr(self.service_class, '_sio', None) # type: CySimpleIO

        if sio:

            # This can be reused across all the output data formats
            sio_desc = self.get_sio_desc(sio)

            for api_spec_info in _SIO_TYPE_MAP:

                _api_spec_info = Bunch()
                _api_spec_info.name = api_spec_info.name
                _api_spec_info.param_list = Bunch()
                _api_spec_info.request_elem = getattr(sio, 'request_elem', None)
                _api_spec_info.response_elem = getattr(sio, 'response_elem', None)

                for param_list_name in _sio_attrs: # type: str

                    _param_list = []

                    param_func_name = 'get_{}'.format(param_list_name)
                    param_func = getattr(sio.definition, param_func_name)
                    param_list = param_func()

                    for param in param_list:

                        # Actual parameter name
                        param_name = param if isinstance(param, basestring) else param.name # type: str

                        # To look up description based on parameter's name
                        desc_dict = sio_desc.input if param_list_name.startswith('input') else sio_desc.output # type: dict

                        # Parameter details object
                        _param_info = Bunch()
                        _param_info.name = param_name
                        _param_info.is_required = 'required' in param_list_name
                        _param_info.description = desc_dict.get(param_name) or '' # Always use a string, even if an empty one

                        if isinstance(param, AsIs):
                            type_info = api_spec_info.DEFAULT

                        elif is_sio_bool(param):
                            type_info = api_spec_info.BOOLEAN

                        elif is_sio_int(param_name):
                            type_info = api_spec_info.INTEGER

                        else:
                            try:
                                type_info = api_spec_info.map[param.__class__]
                            except KeyError:
                                type_info = api_spec_info.DEFAULT

                        _param_info.type, _param_info.subtype = type_info
                        _param_list.append(_param_info)

                    _api_spec_info.param_list[param_list_name] = _param_list

                self.simple_io[_api_spec_info.name] = SimpleIO(_api_spec_info, sio_desc, self.needs_sio_desc).to_bunch()

# ################################################################################################################################

    def set_config(self):
        self._add_services_from_invokes()
        self._add_ns_sio()

# ################################################################################################################################

    def _parse_split_segment(self, tag, split, is_tag_internal, prefix_with_tag):
        # type: (str, list, bool, bool) -> _DocstringSegment

        if is_tag_internal:
            split.insert(0, not_public)

        # For implicit tags (e.g. public), the summary will be under index 0,
        # but for tags named explicitly, index 0 may be an empty element
        # and the summary will be under index 1.
        summary = split[0] or split[1]

        # format_docstring expects an empty line between summary and description
        if len(split) > 1:
            _doc = []
            _doc.append(split[0])
            _doc.append('')
            _doc.extend(split[1:])
            doc = '\n'.join(_doc)
        else:
            doc = ''

        # This gives us the full docstring out of which we need to extract description alone.
        full_docstring = format_docstring('', '"{}"'.format(doc), post_description_blank=False)
        full_docstring = full_docstring.lstrip('"""').rstrip('"""')
        description = full_docstring.splitlines()

        # If there are multiple lines and the second one is empty this means it is an indicator of a summary to follow.
        if len(description) > 1 and not description[1]:
            description = '\n'.join(description[2:])
        else:
            description = ''

        # Function docformatter.normalize_summary adds a superfluous period at the end of docstring.
        if full_docstring:
            if description and full_docstring[-1] == '.' and full_docstring[-1] != description[-1]:
                full_docstring = full_docstring[:-1]

            if summary and full_docstring[-1] == '.' and full_docstring[-1] != summary[-1]:
                full_docstring = full_docstring[:-1]

        # If we don't have any summary but there is a docstring at all then it must be a single-line one
        # and it becomes our summary.
        if full_docstring and not summary:
            summary = full_docstring

        # If we don't have description but we have summary then summary becomes description and full docstring as well
        if summary and not description:
            description = summary
            full_docstring = summary

        summary = summary.lstrip()

        # This is needed in case we have one of the tags
        # that need a highlight because they contain information
        # that is internal to users generating the specification.
        tag_html = tag

        if is_tag_internal:
            tag_html = tag_html_internal.format(tag)
        else:
            tag_html = tag

        if prefix_with_tag:
            description = '\n\n{}\n{}'.format(tag_html, description)
            full_docstring = '\n{}\n\n{}'.format(tag_html, full_docstring)

        out = _DocstringSegment()
        out.tag = tag.replace('@', '', 1)
        out.summary = summary
        out.description = description
        out.full = full_docstring

        return out

# ################################################################################################################################

    def _get_next_split_segment(self, lines, tag_indicator='@'):
        # type: (list) -> (str, list)

        current_lines = []
        len_lines = len(lines) -1 # type: int # Substract one because enumerate counts from zero

        # The very first line must contain tag name(s),
        # otherwise we assume that it is the implicit name, called 'public'.
        first_line = lines[0] # type: str
        current_tag = first_line.strip().replace(tag_indicator, '', 1) if \
            first_line.startswith(tag_indicator) else APISPEC.DEFAULT_TAG # type: str

        # Indicates that we are currently processing the very first line,
        # which is needed because if it starts with a tag name
        # then we do not want to immediately yield to our caller.
        in_first_line = True

        for idx, line in enumerate(lines): # type: (int, str)

            line_stripped = line.strip()
            if line_stripped.startswith(tag_indicator):
                if not in_first_line:
                    yield current_tag, current_lines
                    current_tag = line_stripped
                    current_lines[:] = []
            else:
                in_first_line = False
                current_lines.append(line)
                if idx == len_lines:
                    yield current_tag, current_lines
                    break
        else:
            yield current_tag, current_lines

# ################################################################################################################################

    def extract_segments(self, doc):
        """ Makes a pass over the docstring to extract all of its tags and their text.
        """
        # type: (str) -> list

        # Response to produce
        out = []

        # Nothing to parse
        if not doc:
            return out

        # All lines in the docstring, possibly containing multiple tags
        all_lines = doc.strip().splitlines() # type: list

        # Again, nothing to parse
        if not all_lines:
            return out

        # Contains all lines still to be processed - function self._get_next_split_segment will update it in place.
        current_lines = all_lines[:]

        for tag, tag_lines in self._get_next_split_segment(current_lines):

            # All non-public tags are shown explicitly
            prefix_with_tag = tag != 'public'

            # A flag indicating whether we are processing a public or an internal tag,
            # e.g. public vs. @internal or @confidential.
            for name in tag_internal:
                if name in tag:
                    is_tag_internal = True
                    break
            else:
                is_tag_internal = False

            segment = self._parse_split_segment(tag, tag_lines, is_tag_internal, prefix_with_tag)

            if segment.tag in self.docstring.tags:
                out.append(segment)

        return out

# ################################################################################################################################

    def set_summary_desc(self):

        segments = self.extract_segments(self.service_class.__doc__)

        for segment in segments: # type: _DocstringSegment

            # The very first summary found will set the whole docstring's summary
            if segment.summary:
                if not self.docstring.summary:
                    self.docstring.summary = segment.summary

            if segment.description:
                self.docstring.description += segment.description

            if segment.full:
                self.docstring.full += segment.full

# ################################################################################################################################

    def get_sio_desc(self, sio, io_separator='/', new_elem_marker='*'):
        # type: (object) -> SimpleIODescription

        out = SimpleIODescription()
        doc = sio.service_class.SimpleIO.__doc__

        # No description to parse
        if not doc:
            return out

        doc = doc.strip() # type: str

        lines = []

        # Strip leading whitespace but only from lines containing element names
        for line in doc.splitlines(): # type: str
            orig_line = line
            line = line.lstrip()
            if line.startswith(new_elem_marker):
                lines.append(line)
            else:
                lines.append(orig_line)

        # Now, replace all the leading whitespace left with endline characters,
        # but instead of replacing them in place, they will be appending to the preceding line.

        # This will contain all lines with whitespace replaced with newlines
        with_new_lines = []

        for idx, line in enumerate(lines):

            # By default, assume that do not need to append the new line
            append_new_line = False

            # An empty line is interpreted as a new line marker
            if not line:
                append_new_line = True

            if line.startswith(' '):
                line = line.lstrip()

            with_new_lines.append(line)

            # Alright, this line started with whitespace which we removed above,
            # so now we need to append the new line character. But first we need to
            # find an index of any previous line that is not empty in case there
            # are multiple empty lines in succession in the input string.
            if append_new_line:

                line_found = False
                line_idx = idx

                while not line_found or (idx == 0):
                    line_idx -= 1
                    current_line = with_new_lines[line_idx]
                    if current_line.strip():
                        break

                with_new_lines[line_idx] += '\n'

        # We may still have some empty lines left over which we remove now
        lines = [elem for elem in with_new_lines[:] if elem]

        input_lines = []
        output_lines = []

        # If there is no empty line, the docstring will describe either input or output (we do not know yet).
        # If there is only one empty line, it constitutes a separator between input and output.
        # If there is more than one empty line, we need to look up the separator marker instead.
        # If the separator is not found, it again means that the docstring describes either input or output.
        empty_line_count = 0

        # Line that separates input from output in the list of arguments
        input_output_sep_idx = None

        # To indicate whether we have found a separator in the docstring
        has_separator = False

        for idx, line in enumerate(lines):
            if not line:
                empty_line_count += 1
                input_output_sep_idx = idx

            if line == io_separator:
                has_separator = True
                input_output_sep_idx = idx

        # No empty line separator = we do not know if it is input or output so we need to populate both structures ..
        if empty_line_count == 0:
            input_lines[:] = lines[:]
            output_lines[:] = lines[:]

        # .. a single empty line separator = we know where input and output are.
        elif empty_line_count == 1:
            input_lines[:] = lines[:input_output_sep_idx]
            output_lines[:] = lines[input_output_sep_idx+1:]

        else:
            # If we have a separator, this is what indicates where input and output are ..
            if has_separator:
                input_lines[:] = lines[:input_output_sep_idx-1]
                output_lines[:] = lines[input_output_sep_idx-1:]

            # .. otherwise, we treat it as a list of arguments and we do not know if it is input or output.
            else:
                input_lines[:] = lines[:]
                output_lines[:] = lines[:]

        input_lines = [elem for elem in input_lines if elem and elem != io_separator]
        output_lines = [elem for elem in output_lines if elem and elem != io_separator]

        out.input.update(self._parse_sio_desc_lines(input_lines))
        out.output.update(self._parse_sio_desc_lines(output_lines))

        return out

# ################################################################################################################################

    def _parse_sio_desc_lines(self, lines, new_elem_marker='*'):
        # type: (list) -> dict
        out = {}
        current_elem = None

        for line in lines: # type: str
            if line.startswith(new_elem_marker):

                # We will need it later below
                orig_line = line

                # Remove whitespace, skip the new element marker and the first string left over will be the element name.
                line = [elem for elem in line.split()]
                line.remove(new_elem_marker)
                current_elem = line[0]

                # We have the element name so we can now remove it from the full line
                to_remove = '{} {} - '.format(new_elem_marker, current_elem)
                after_removal = orig_line.replace(to_remove, '', 1)
                out[current_elem] = [after_removal]

            else:
                if current_elem:
                    out[current_elem].append(line)

        # Joing all the lines into a single string, preprocessing them along the way.
        for key, value in out.items():

            # We need to strip the trailing new line characters from the last element  in the list of lines
            # because it is redundant and our callers would not want to render it anyway.
            last = value[-1]
            last = last.rstrip()
            value[-1] = last

            # Joing the lines now, honouring new line characters. Also, append whitespace
            # but only to elements that are not the last in the list because they end a sentence.
            new_value = []
            len_value = len(value)
            for idx, elem in enumerate(value, 1): # type: str
                if idx != len_value and not elem.endswith('\n'):
                    elem += ' '
                new_value.append(elem)

            # Everything is preprocesses so we can create a new string now ..
            new_value = ''.join(new_value)

            # .. and set it for that key.
            out[key] = new_value

        return out

# ################################################################################################################################

class Generator(object):
    def __init__(self, service_store_services, simple_io_config, include, exclude, query=None, tags=None, needs_sio_desc=True):
        self.service_store_services = service_store_services
        self.simple_io_config = simple_io_config
        self.include = include or []
        self.exclude = exclude or []
        self.query = query
        self.tags = tags
        self.needs_sio_desc = needs_sio_desc
        self.services = {}

        # Service name -> list of services this service invokes
        self.invokes = {}

        # Service name -> list of services this service is invoked by
        self.invoked_by = {}

    def to_html(self, value):
        return markdown(value).lstrip('<p>').rstrip('</p>')

    def get_info(self):
        """ Returns a list of dicts containing metadata about services in the scope required to generate docs and API clients.
        """
        self.parse()

        if self.query:
            query_items = [elem.strip() for elem in self.query.strip().split()]
        else:
            query_items = []

        out = {
            'services': [],
            'namespaces': {'':{'name':APISPEC.NAMESPACE_NULL, 'docs':'', 'docs_md':'', 'services':[]}},
        }

        # Add services
        for name in sorted(self.services):
            proceed = True

            if query_items:
                for item in query_items:
                    if item not in name:
                        proceed = False

            if not proceed:
                continue

            info = self.services[name] # type: ServiceInfo
            item = Bunch()

            item.name = info.name
            item.invokes = sorted(info.invokes)
            item.invoked_by = sorted(info.invoked_by)
            item.simple_io = info.simple_io

            item.docs = Bunch()
            item.docs.summary = info.docstring.summary
            item.docs.summary_html = self.to_html(info.docstring.summary)
            item.docs.description = info.docstring.description
            item.docs.description_html = self.to_html(info.docstring.description)
            item.docs.full = info.docstring.full
            item.docs.full_html = self.to_html(info.docstring.full)
            item.namespace_name = info.namespace.name

            # Add namespaces
            if info.namespace.name:
                ns = out['namespaces'].setdefault(info.namespace.name, {'docs':'', 'docs_md':''})
                ns['name'] = info.namespace.name
                ns['services'] = []

                if info.namespace.docs:
                    ns['docs'] = info.namespace.docs
                    ns['docs_md'] = markdown(info.namespace.docs)

            out['services'].append(item.toDict())

        # For each namespace, add copy of its services
        for ns_name, ns_info in iteritems(out['namespaces']):
            for service in out['services']:
                if service['namespace_name'] == ns_name:
                    out['namespaces'][ns_name]['services'].append(deepcopy(service))

        return out

# ################################################################################################################################

    def _should_handle(self, name, list_):
        for match_elem in list_:
            if fnmatch(name, match_elem):
                return True

# ################################################################################################################################

    def parse(self):

        for impl_name, details in iteritems(self.service_store_services):

            details = bunchify(details)
            _should_include = self._should_handle(details.name, self.include)
            _should_exclude = self._should_handle(details.name, self.exclude)

            if (not _should_include) or _should_exclude:
                continue

            info = ServiceInfo(details.name, details.service_class, self.simple_io_config, self.tags, self.needs_sio_desc)
            self.services[info.name] = info

        for name, info in iteritems(self.services):
            self.invokes[name] = info.invokes

        for source, targets in iteritems(self.invokes):
            for target in targets:
                sources = self.invoked_by.setdefault(target, [])
                sources.append(source)

        for name, info in iteritems(self.services):
            info.invoked_by = self.invoked_by.get(name, [])

# ################################################################################################################################
