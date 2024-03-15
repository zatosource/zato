# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.marshal_.api import extract_model_class, is_list
from zato.common.marshal_.api import Model
from zato.common.marshal_.simpleio import DataClassSimpleIO
from zato.common.typing_ import any_, cast_
from zato.server.apispec.model import APISpecInfo, Config, FieldInfo, SimpleIO
from zato.server.apispec.parser.docstring import DocstringParser

# Zato - Cython
from zato.simpleio import SIO_TYPE_MAP

# ################################################################################################################################
# ################################################################################################################################

_SIO_TYPE_MAP = SIO_TYPE_MAP() # type: ignore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import anydict, anylist, optional, strorlist, type_
    from zato.server.service import Service

    Field   = Field
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

def build_field_list(model:'Model | str', api_spec_info:'any_') -> 'anylist':

    # Response to produce
    out = [] # type: anylist

    # Local variables
    is_any  = model is any_
    is_int  = model is int
    is_str  = model is str
    is_bool = model is bool

    # This is not a true model that we can process ..
    should_ignore = is_int or is_str or is_any or is_bool

    # .. in which case we can return immediately ..
    if should_ignore:
        return out

    # .. handle list models as well ..
    if is_list(model, True): # type: ignore
        model = extract_model_class(model) # type: ignore

    python_field_list = cast_('any_', model).zato_get_fields()

    for _, field in sorted(python_field_list.items()):

        # Parameter details object
        info = FieldInfo.from_python_field(model, field, api_spec_info) # type: ignore
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
        self.needs_sio_desc = needs_sio_desc

        # This is the object that extracts docstrings from services or from their SimpleIO definitions.
        self.docstring = DocstringParser(service_class, tags)

        # Run the parser now
        self.parse()

# ################################################################################################################################

    def to_dict(self) -> 'anydict':

        return {
            'name': self.name,
            'simple_io': self.simple_io,
            'docs': {
                'full':      self.docstring.data.full,
                'full_html': self.docstring.data.full_html,

                'summary':      self.docstring.data.summary,
                'summary_html': self.docstring.data.summary_html,

                'description':      self.docstring.data.description,
                'description_html': self.docstring.data.description_html,
            }
        }

# ################################################################################################################################

    def parse(self) -> 'None':
        self.parse_simple_io()
        self.docstring.set_summary_desc()

# ################################################################################################################################

    def parse_simple_io(self) -> 'None':
        """ Adds metadata about the service's SimpleIO definition.
        """

        # SimpleIO
        sio = getattr(self.service_class, '_sio', None) # type: any_

        if sio and isinstance(sio, DataClassSimpleIO):

            # This can be reused across all the output data formats
            sio_desc = self.docstring.get_sio_desc(sio)

            for api_spec_info in _SIO_TYPE_MAP: # type: ignore

                # A structure that contains an API specification for each major output format, e.g. Zato or OpenAPI
                spec_info = APISpecInfo()
                spec_info.name = api_spec_info.name
                spec_info.field_list = {}
                spec_info.request_elem = getattr(sio, 'request_elem', '')
                spec_info.response_elem = getattr(sio, 'response_elem', '')

                # This is where input and output are assigned based on a service's models ..
                for sio_attr_name in ('input', 'output'):
                    model = getattr(sio.user_declaration, sio_attr_name, None) # type: optional[Model]
                    if model:
                        spec_info.field_list[sio_attr_name] = build_field_list(model, api_spec_info)

                # This is a container for the entire SimpleIO definition ..
                sio_def = SimpleIO(spec_info, sio_desc, self.needs_sio_desc)

                # .. and this is where required and optional arguments
                # .. are extracted and assigned to input_required/optional or output_required/optional,
                # .. based on previously assigned input and output ..
                sio_def.assign_required_optional()

                # .. let's sort every input and output element alphabetically ..
                sio_def.sort_elems()

                # .. now, we can serialise the data structure for external users
                self.simple_io[spec_info.name] = sio_def.to_bunch()

# ################################################################################################################################
# ################################################################################################################################
