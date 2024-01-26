# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from fnmatch import fnmatch

# Zato
from zato.server.apispec.parser.service import ServiceInfo

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import anydict, anylist, anylistnone, dict_, dictlist
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

    def get_info(self) -> 'dictlist':
        """ Returns a list of dicts containing metadata about services in the scope required to generate docs and API clients.
        """

        # This is the call that finds all the services in the server's service store
        # and turns them into a data structure that SIO information is applied to in later steps.
        self.build_service_information()

        if self.query:
            query_items = [elem.strip() for elem in self.query.strip().split()]
        else:
            query_items = []

        out = []

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
            out.append(info.to_dict())

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

            _should_include = self._should_handle(details['name'], self.include)
            _should_exclude = self._should_handle(details['name'], self.exclude)

            if (not _should_include) or _should_exclude:
                continue

            info = ServiceInfo(details['name'], details['service_class'], self.simple_io_config, self.tags, self.needs_sio_desc)
            self.services[info.name] = info

# ################################################################################################################################
# ################################################################################################################################
