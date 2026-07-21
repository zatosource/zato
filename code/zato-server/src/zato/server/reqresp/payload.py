# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.message import has_content, Message
from zato.input_output import IOProcessor

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################

_not_given:object = object()

# ################################################################################################################################
# ################################################################################################################################

class IOPayload:
    """ Represents a payload, i.e. individual response elements, set via I/O declaration.
    """
    _internal_attrs = frozenset({
        'io', 'all_output_elem_names', 'output_repeated',
        'cid', 'data_format', 'user_attrs_dict', 'user_attrs_list',
    })

    def __init__(self, io:IOProcessor, all_output_elem_names:list, cid, data_format):
        _set = object.__setattr__
        _set(self, 'user_attrs_dict', {})
        _set(self, 'user_attrs_list', [])
        _set(self, 'io', io)
        _set(self, 'all_output_elem_names', all_output_elem_names)
        _set(self, 'output_repeated', False)
        _set(self, 'cid', cid)
        _set(self, 'data_format', data_format)

# ################################################################################################################################

    def __iter__(self):
        return iter(self.user_attrs_list if self.output_repeated else self.user_attrs_dict)

    def __setitem__(self, key, value):

        if isinstance(key, slice):
            self.user_attrs_list[key.start:key.stop] = value
            object.__setattr__(self, 'output_repeated', True)
        else:
            setattr(self, key, value)

    def __setattr__(self, key:'str', value:'any_') -> 'None':

        if key in IOPayload._internal_attrs:
            object.__setattr__(self, key, value)
        else:
            # Only declared names may become part of the response - anything else
            # is a typo or a name that is missing from the service's output declaration.
            if key in self.all_output_elem_names:
                self.user_attrs_dict[key] = value
            else:
                raise KeyError('{}; No such output element `{}` among `{}` ({})'.format(
                    self.io.service_class, key, self.all_output_elem_names, hex(id(self))))

    def __getattr__(self, key:'str') -> 'any_':
        try:
            return self.user_attrs_dict[key]
        except KeyError:
            # A declared name that was not assigned yet vivifies a message subtree,
            # which is what lets payload.abc.hello = 123 build the whole path in one go.
            if key in self.all_output_elem_names:
                out = Message()
                self.user_attrs_dict[key] = out
                return out
            else:
                raise KeyError('{}; No such output element `{}` among `{}` ({})'.format(
                    self.io.service_class, key, self.all_output_elem_names, hex(id(self))))

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
        self.user_attrs_dict.clear()
        self.user_attrs_list.clear()

        value = self._preprocess_payload_attrs(value)

        is_dict = isinstance(value, dict)

        if is_dict:
            dict_attrs:dict = self._extract_payload_attrs_dict(value)
            self.user_attrs_dict.update(dict_attrs)
        else:
            if hasattr(value, 'to_zato'):
                value = value.to_zato()

            if isinstance(value, (list, tuple)):
                for item in value:
                    self.user_attrs_list.append(self._extract_payload_attrs(item))
            else:
                self.user_attrs_dict.update(self._extract_payload_attrs(value))

# ################################################################################################################################

    def getvalue(self) -> 'any_':
        """ Returns a service's payload as a raw Python dict or list.
        """
        if self.output_repeated:
            return self.user_attrs_list

        out = {}

        for key, value in self.user_attrs_dict.items():

            # A message subtree turns into a plain dict - unless it was vivified
            # by a read alone, in which case it carries no content and is pruned.
            if isinstance(value, Message):
                if has_content(value):
                    out[key] = value.to_dict()
            else:
                out[key] = value

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
