# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.api import DATA_FORMAT
from zato.input_output import IOProcessor

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

DATA_FORMAT_DICT:str = DATA_FORMAT.DICT
_not_given:object = object()

# ################################################################################################################################
# ################################################################################################################################

class IOPayload:
    """ Represents a payload, i.e. individual response elements, set via I/O declaration.
    """

    def __init__(self, io:IOProcessor, all_output_elem_names:list, cid, data_format):
        self.io = io
        self.all_output_elem_names = all_output_elem_names
        self.output_repeated = self.io.definition.output_repeated
        self.cid = cid
        self.data_format = data_format
        self.user_attrs_dict = {}
        self.user_attrs_list = []
        self.zato_meta = None

# ################################################################################################################################

    def __iter__(self):
        return iter(self.user_attrs_list if self.output_repeated else self.user_attrs_dict)

    def __setitem__(self, key, value):

        if isinstance(key, slice):
            self.user_attrs_list[key.start:key.stop] = value
            self.output_repeated = True
        else:
            setattr(self, key, value)

    def __setattr__(self, key, value):

        # Special-case Zato's own internal attributes
        if key == 'zato_meta':
            self.zato_meta = value
        else:
            self.user_attrs_dict[key] = value

    def __getattr__(self, key):
        try:
            return self.user_attrs_dict[key]
        except KeyError:
            raise KeyError('{}; No such key `{}` among `{}` ({})'.format(
                self.io.service_class, key, self.user_attrs_dict, hex(id(self))))

    def __getitem__(self, key):
        return self.__getattr__(key)

    def get(self, key):
        return self.user_attrs_dict.get(key)

# ################################################################################################################################

    def has_data(self):
        return bool(self.user_attrs_dict or self.user_attrs_list)

# ################################################################################################################################

    def _extract_payload_attrs(self, item:object) -> dict:
        """ Extract response attributes from a single object. Used with items other than dicts.
        """
        extracted:dict = {}
        is_dict = isinstance(item, dict)

        # Use a different function depending on whether the object is dict-like or not.
        # Note that we need .get to be able to provide a default value.
        has_get = hasattr(item, 'get')
        name = None

        for name in self.all_output_elem_names:
            if is_dict:
                value = item.get(name, _not_given)
            elif has_get:
                value = item.get(name, _not_given)
            else:
                value = getattr(item, name, _not_given)
            if value is not _not_given:
                extracted[name] = value

        return extracted

# ################################################################################################################################

    def _extract_payload_attrs_dict(self, item:object) -> dict:
        """ Extract response attributes from a dict.
        """
        extracted:dict = {}
        name = None

        for name in self.all_output_elem_names:
            value = item.get(name, _not_given)
            if value is not _not_given:
                extracted[name] = value

        return extracted

# ################################################################################################################################

    def _is_sqlalchemy(self, item:object):
        return hasattr(item, '_sa_class_manager')

# ################################################################################################################################

    def _preprocess_payload_attrs(self, value):

        # First, check if this is not a response from a Zato service wrapped in a response element.
        # If it is, extract the actual inner response first.
        if isinstance(value, dict) and len(value) == 1:
            response_name:str = list(value.keys())[0]
            if response_name.startswith('zato') and response_name.endswith('_response'):
                return value[response_name]
            else:
                return value
        else:
            return value

# ################################################################################################################################

    def set_payload_attrs(self, value:object):
        """ Assigns user-defined attributes to what will eventually be a response.
        """
        # Clear out anything we might have stored before in case .getvalue() get called more than once
        self.user_attrs_dict.clear()
        self.user_attrs_list.clear()

        value = self._preprocess_payload_attrs(value)
        is_dict = isinstance(value, dict)

        # Shortcut in case we know already this is a dict on input
        if is_dict:
            dict_attrs:dict = self._extract_payload_attrs_dict(value)
            self.user_attrs_dict.update(dict_attrs)
        else:
            # Check if this is something that can be explicitly serialised for our purposes
            if hasattr(value, 'to_zato'):
                value = value.to_zato()

            if isinstance(value, (list, tuple)):
                for item in value:
                    self.user_attrs_list.append(self._extract_payload_attrs(item))
            else:
                self.user_attrs_dict.update(self._extract_payload_attrs(value))

# ################################################################################################################################

    def getvalue(self, serialize:bool=True, force_dict_serialisation:bool=True): # noqa: E252
        """ Returns a service's payload, either serialised or not.
        """
        # If data format is DICT, we force serialisation to that format
        # unless overridden on input.
        if self.data_format == DATA_FORMAT_DICT:
            if force_dict_serialisation:
                serialize = True

        # No data format means no serialization is possible
        if not self.data_format:
            serialize = False

        value = self.user_attrs_list if self.output_repeated else self.user_attrs_dict

        # Special-case internal services that return metadata (e.g GetList-like ones)
        if self.zato_meta:

            # If search is provided, we need to first get output,
            # append the search the metadata and then serialise ..
            search = self.zato_meta.get('search')

            if search:
                output = self.io.get_output(value, self.data_format, False)
                output['_meta'] = search
                result = self.io.serialise(output, self.data_format)
                return result

            # .. otherwise, with no search metadata provided,
            # we can data, serialised or not, immediately.
            result = self.io.get_output(value, self.data_format) if serialize else value
            return result

        else:
            out = self.io.get_output(value, self.data_format) if serialize else value
            return out

    def append(self, value):

        if isinstance(value, dict):
            to_append = value
        elif hasattr(value, '_asdict'):
            to_append = value._asdict()
        elif hasattr(value, 'keys'):
            keys = value.keys()
            to_append = dict(zip(keys, value))
        else:
            to_append = self._extract_payload_attrs(value)

        self.user_attrs_list.append(to_append)
        self.output_repeated = True

# ################################################################################################################################
# ################################################################################################################################
