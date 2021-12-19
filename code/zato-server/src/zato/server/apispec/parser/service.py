# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from inspect import getmodule

# Zato
from zato.common.api import APISPEC
from zato.common.marshal_.api import Model
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.server.apispec.model import APISpecInfo, Config, FieldInfo, Namespace, SimpleIO
from zato.server.apispec.parser.docstring import DocstringParser

# Zato - Cython
from zato.simpleio import SIO_TYPE_MAP

# ################################################################################################################################
# ################################################################################################################################

_SIO_TYPE_MAP = SIO_TYPE_MAP()

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import any_, anydict, anylist, optional, strorlist, type_
    from zato.server.service import Service

    Field   = Field
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

def build_field_list(model:'Model', api_spec_info:'any_') -> 'anylist':

    # Response to produce
    out = []

    # All the fields of this dataclass
    python_field_list = model.zato_get_fields()

    for _, field in sorted(python_field_list.items()): # type: (str, Field)

        # Parameter details object
        info = FieldInfo.from_python_field(field, api_spec_info)
        out.append(info)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ServiceInfo:
    """ Contains information about a service basing on which documentation is generated.
    """
    def __init__(
        self,
        name,               # type: str
        service_class,      # type: type_[Service]
        simple_io_config,   # type: anydict
        tags='public',      # type: strorlist
        needs_sio_desc=True # type: bool
        ) -> 'None':

        self.name = name
        self.service_class = service_class
        self.simple_io_config = simple_io_config
        self.config = Config()
        self.simple_io = {} # type: anydict

        self.namespace = Namespace()
        self.needs_sio_desc = needs_sio_desc

        # This is the object that extracts docstrings from services or from their SimpleIO definitions.
        self.docstring = DocstringParser(service_class, tags)

        # Run the parser now
        self.parse()

# ################################################################################################################################

    def parse(self) -> 'None':
        self.parse_simple_io()
        self.docstring.set_summary_desc()

# ################################################################################################################################

    def parse_simple_io(self) -> 'None':
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
        sio = getattr(self.service_class, '_sio', None) # type: optional[DataClassSimpleIO]

        if sio:

            # This can be reused across all the output data formats
            sio_desc = self.docstring.get_sio_desc(sio)

            for api_spec_info in _SIO_TYPE_MAP:

                _api_spec_info = APISpecInfo()
                _api_spec_info.name = api_spec_info.name
                _api_spec_info.field_list = {}
                _api_spec_info.request_elem = getattr(sio, 'request_elem', '')
                _api_spec_info.response_elem = getattr(sio, 'response_elem', '')

                for sio_attr_name in ('input', 'output'): # type: str
                    model = getattr(sio.user_declaration, sio_attr_name, None) # type: optional[Model]
                    if model:
                        _api_spec_info.field_list[sio_attr_name] = build_field_list(model, api_spec_info)

                self.simple_io[_api_spec_info.name] = SimpleIO(_api_spec_info, sio_desc, self.needs_sio_desc).to_bunch()

# ################################################################################################################################
# ################################################################################################################################
