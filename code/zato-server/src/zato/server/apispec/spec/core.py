# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from fnmatch import fnmatch

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common.api import APISPEC
from zato.server.apispec.parser.service import ServiceInfo

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import anydict, anylist, anylistnone, dict_
    from zato.server.service import Service

    Field   = Field
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

class Generator:
    def __init__(
        self,
        service_store_services, # type: anydict
        simple_io_config,       # type: anydict
        include,                # type: anylist
        exclude,                # type: anylist
        query='',               # type: str
        tags=None,              # type: anylistnone
        needs_sio_desc=True     # type: bool
        ) -> 'None':

        self.service_store_services = service_store_services
        self.simple_io_config = simple_io_config
        self.include = include or []
        self.exclude = exclude or []
        self.query = query
        self.tags = tags or []
        self.needs_sio_desc = needs_sio_desc
        self.services = {} # type: dict_[str, ServiceInfo]

# ################################################################################################################################

    def get_info(self) -> 'anydict':
        """ Returns a list of dicts containing metadata about services in the scope required to generate docs and API clients.
        """

        # This is the call that finds all the services in the server's service store
        # and turns them into a data structure that SIO information is applied to in later steps.
        self.build_service_information()

        if self.query:
            query_items = [elem.strip() for elem in self.query.strip().split()]
        else:
            query_items = []

        out = {
            'services': [],
            'namespaces': {'':{'name':APISPEC.NAMESPACE_NULL, 'docs':'', 'docs_md':'', 'services':[]}},
        } # type: anydict

        # Add services
        for name in sorted(self.services):
            proceed = True

            if query_items:
                for query_item in query_items:
                    if query_item not in name:
                        proceed = False

            if not proceed:
                continue

            info = self.services[name] # type: ServiceInfo
            item = Bunch()

            item.name = info.name
            item.simple_io = info.simple_io

            item.docs = Bunch()
            item.docs.summary = info.docstring.data.summary
            item.docs.summary_html = info.docstring.data.summary_html
            item.docs.description = info.docstring.data.description
            item.docs.description_html = info.docstring.data.description_html
            item.docs.full = info.docstring.data.full
            item.docs.full_html = info.docstring.data.full_html
            item.namespace_name = info.namespace.name

            # Add namespaces
            if info.namespace.name:
                ns = out['namespaces'].setdefault(info.namespace.name, {'docs':'', 'docs_md':''})
                ns['name'] = info.namespace.name
                ns['services'] = []

                if info.namespace.docs:
                    ns['docs'] = info.namespace.docs
                    ns['docs_md'] = info.namespace.docs_md

            out['services'].append(item.toDict())

        # For each namespace, add copy of its services
        for ns_name in out['namespaces']:
            for service in out['services']:
                if service['namespace_name'] == ns_name:
                    out['namespaces'][ns_name]['services'].append(deepcopy(service))

        return out

# ################################################################################################################################

    def _should_handle(self, name:'str', list_:'anylist') -> 'bool':
        for match_elem in list_:
            if fnmatch(name, match_elem):
                return True
        else:
            return False

# ################################################################################################################################

    def build_service_information(self) -> 'None':

        for details in self.service_store_services.values():

            details = bunchify(details)
            _should_include = self._should_handle(details.name, self.include)
            _should_exclude = self._should_handle(details.name, self.exclude)

            if (not _should_include) or _should_exclude:
                continue

            info = ServiceInfo(details.name, details.service_class, self.simple_io_config, self.tags, self.needs_sio_desc)
            self.services[info.name] = info

# ################################################################################################################################
# ################################################################################################################################
