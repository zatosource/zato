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
from zato.common import APISPEC
from zato.server.service.reqresp.sio import AsIs, SIO_TYPE_MAP, is_bool, is_int

# ################################################################################################################################

_sio_attrs = ('input_required', 'input_optional', 'output_required', 'output_optional')

_SIO_TYPE_MAP = SIO_TYPE_MAP()

# ################################################################################################################################

class Config(object):
    def __init__(self):
        self.is_module_level = True
        self.ns = ''
        self.services = []

# ################################################################################################################################

class Docstring(object):
    def __init__(self):
        self.summary = ''
        self.description = ''
        self.full = ''

# ################################################################################################################################

class Namespace(object):
    def __init__(self):
        self.name = APISPEC.NAMESPACE_NULL
        self.docs = ''

# ################################################################################################################################

class SimpleIO(object):
    def __init__(self, api_spec_info):
        self.input_required = api_spec_info.param_list.input_required
        self.output_required = api_spec_info.param_list.output_required
        self.input_optional = api_spec_info.param_list.input_optional
        self.output_optional = api_spec_info.param_list.output_optional
        self.request_elem = api_spec_info.request_elem
        self.response_elem = api_spec_info.response_elem
        self.spec_name = api_spec_info.name

    def to_bunch(self):
        out = Bunch()
        for name in _sio_attrs + ('request_elem', 'response_elem', 'spec_name'):
            out[name] = getattr(self, name)

        return out

# ################################################################################################################################

class ServiceInfo(object):
    """ Contains information about a service basing on which documentation is generated.
    """
    def __init__(self, name, service_class, simple_io_config):
        self.name = name
        self.service_class = service_class
        self.simple_io_config = simple_io_config
        self.config = Config()
        self.simple_io = {}
        self.docstring = Docstring()
        self.namespace = Namespace()
        self.invokes = []
        self.invoked_by = []
        self.parse()

# ################################################################################################################################

    def parse(self):
        self.set_config()
        #self.set_simple_io()
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
        sio = getattr(self.service_class, 'SimpleIO', None)

        if sio:
            for api_spec_info in _SIO_TYPE_MAP:

                _api_spec_info = Bunch()
                _api_spec_info.name = api_spec_info.name
                _api_spec_info.param_list = Bunch()
                _api_spec_info.request_elem = getattr(sio, 'request_elem', None)
                _api_spec_info.response_elem = getattr(sio, 'response_elem', None)

                for param_list_name in _sio_attrs:
                    _param_list = []
                    param_list = getattr(sio, param_list_name, [])
                    param_list = param_list if isinstance(param_list, (tuple, list)) else [param_list]

                    for param in param_list:
                        param_name = param if isinstance(param, basestring) else param.name
                        _param_info = Bunch()
                        _param_info.name = param_name
                        _param_info.is_required = 'required' in param_list_name

                        if isinstance(param, AsIs):
                            type_info = api_spec_info.DEFAULT

                        elif is_bool(param, param_name, self.simple_io_config.bool.prefix):
                            type_info = api_spec_info.BOOLEAN

                        elif is_int(param_name, self.simple_io_config.int.exact, self.simple_io_config.int.suffix):
                            type_info = api_spec_info.INTEGER

                        else:
                            try:
                                type_info = api_spec_info.map[param.__class__]
                            except KeyError:
                                type_info = api_spec_info.DEFAULT

                        _param_info.type, _param_info.subtype = type_info
                        _param_list.append(_param_info)

                    _api_spec_info.param_list[param_list_name] = _param_list

                self.simple_io[_api_spec_info.name] = SimpleIO(_api_spec_info).to_bunch()

# ################################################################################################################################

    def set_config(self):
        self._add_services_from_invokes()
        self._add_ns_sio()

# ################################################################################################################################

    def set_summary_desc(self):

        doc = self.service_class.__doc__
        if not doc:
            return

        split = doc.splitlines()
        summary = split[0]

        # format_docstring expects an empty line between summary and description
        if len(split) > 1:
            _doc = []
            _doc.append(split[0])
            _doc.append('')
            _doc.extend(split[1:])
            doc = '\n'.join(_doc)

        # This gives us the full docstring out of which we need to extract description alone.
        full_docstring = format_docstring('', '"{}"'.format(doc), post_description_blank=False)
        full_docstring = full_docstring.lstrip('"""').rstrip('"""')
        description = full_docstring.splitlines()

        # If there are multiple lines and the second one is empty this means it is an indicator of a summary to follow.
        if len(description) > 1 and not description[1]:
            description = '\n'.join(description[2:])
        else:
            description = ''

        # docformatter.normalize_summary adds superfluous period at end docstring.
        if full_docstring:
            if description and full_docstring[-1] == '.' and full_docstring[-1] != description[-1]:
                full_docstring = full_docstring[:-1]

            if summary and full_docstring[-1] == '.' and full_docstring[-1] != summary[-1]:
                full_docstring = full_docstring[:-1]

        summary = summary.strip()
        full_docstring = full_docstring.strip()

        # If we don't have any summary but there is a docstring at all then it must be a single-line one
        # and it becomes our summary.
        if full_docstring and not summary:
            summary = full_docstring

        # If we don't have description but we have summary then summary becomes description
        if summary and not description:
            description = summary

        self.docstring.summary = summary
        self.docstring.description = description
        self.docstring.full = full_docstring

# ################################################################################################################################

class Generator(object):
    def __init__(self, service_store_services, simple_io_config, include, exclude, query=None):
        self.service_store_services = service_store_services
        self.simple_io_config = simple_io_config
        self.include = include or []
        self.exclude = exclude or []
        self.query = query
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

            info = self.services[name]
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

            info = ServiceInfo(details.name, details.service_class, self.simple_io_config)
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
