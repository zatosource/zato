# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.util.orders import get_custom_object_order, get_object_order, get_top_level_order

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

    # Add dummy assignments to satisfy type checkers
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# How far the continuation lines of a multi-line scalar are indented, for a field of a mapping-valued section.
_Section_Field_Block_Indent = 4

# The same, for a field of one item of a list-valued section.
_Item_Field_Block_Indent = 6

# ################################################################################################################################
# ################################################################################################################################

_yaml_unsafe_chars = frozenset(',:[]{}&*#?|->!%@`')

# Unquoted, these would be read back by a YAML parser as booleans or nulls instead of strings
_yaml_keyword_scalars = frozenset(('true', 'false', 'yes', 'no', 'on', 'off', 'null', '~'))

# ################################################################################################################################

def _is_ambiguous_scalar(text:'str') -> 'bool':
    """ Returns True if unquoted text would be read back by a YAML parser
    as a number, boolean or null instead of a string.
    """
    text_lower = text.lower()

    if text_lower in _yaml_keyword_scalars:
        return True

    # Anything that parses as a number would lose its string type on a round trip
    try:
        _ = float(text)
    except ValueError:
        out = False
    else:
        out = True

    return out

# ################################################################################################################################

def _yaml_quote(value:'any_') -> 'str':
    """ Wraps a scalar value in single quotes if it contains characters
    that would make the YAML parser misinterpret it.
    """
    text = str(value)

    needs_quoting = False

    if not text:
        needs_quoting = True
    elif text[0] in _yaml_unsafe_chars:
        needs_quoting = True
    else:
        for character in text:
            if character in _yaml_unsafe_chars:
                needs_quoting = True
                break

    # A string that reads back as a number or boolean must keep its string type
    if not needs_quoting:
        if isinstance(value, str):
            if _is_ambiguous_scalar(text):
                needs_quoting = True

    if needs_quoting:
        escaped = text.replace("'", "''")
        out = f"'{escaped}'"
        return out

    out = text
    return out

# ################################################################################################################################
# ################################################################################################################################

def _write_scalar_field(file_handle:'any_', line_prefix:'str', field_name:'str', value:'any_', block_indent:'int') -> 'None':
    """ Writes a single scalar field, using a YAML block scalar for multi-line values
    (e.g. PEM certificates and keys) so that newlines survive a round trip.
    """
    text = str(value)

    if isinstance(value, str) and '\n' in text:

        # A trailing newline needs the clip style, no trailing newline needs the strip style
        if text.endswith('\n'):
            indicator = '|'
            text = text[:-1]
        else:
            indicator = '|-'

        _ = file_handle.write(f'{line_prefix}{field_name}: {indicator}\n')

        pad = ' ' * block_indent
        for line in text.split('\n'):
            if line:
                _ = file_handle.write(f'{pad}{line}\n')
            else:
                _ = file_handle.write('\n')
    else:
        quoted = _yaml_quote(value)
        _ = file_handle.write(f'{line_prefix}{field_name}: {quoted}\n')

# ################################################################################################################################
# ################################################################################################################################

def _write_mapping_entry(
    file_handle:'any_',
    line_prefix:'str',
    key:'str',
    value:'any_',
    content_indent:'int',
    ) -> 'None':
    """ Writes one key of a mapping and whatever it holds. A nested mapping and a list of them
    are written out as YAML structures of their own, no matter how deep they go - written as the
    text they happen to render as they would read back as that text rather than as what they are.
    """
    nested_indent = content_indent + 2
    nested_prefix = ' ' * nested_indent

    # A nested mapping (e.g. the options one destination needs) becomes a block of its own ..
    if isinstance(value, dict):
        _ = file_handle.write(f'{line_prefix}{key}:\n')

        for sub_key, sub_value in value.items():
            _write_mapping_entry(file_handle, nested_prefix, sub_key, sub_value, nested_indent)

    # .. nested lists (e.g. cidr_list, time_range, destinations) get their own sub-items ..
    elif isinstance(value, list):
        _ = file_handle.write(f'{line_prefix}{key}:\n')

        for sub_item in value:
            if isinstance(sub_item, dict):
                _write_dict_list_item(file_handle, sub_item, nested_indent)
            else:
                quoted_sub_item = _yaml_quote(sub_item)
                _ = file_handle.write(f'{nested_prefix}- {quoted_sub_item}\n')

    # .. and everything else is one scalar.
    else:
        quoted_value = _yaml_quote(value)
        _ = file_handle.write(f'{line_prefix}{key}: {quoted_value}\n')

# ################################################################################################################################
# ################################################################################################################################

def _write_dict_list_item(file_handle:'any_', item:'anydict', indent:'int'=_Item_Field_Block_Indent) -> 'None':
    """ Writes a dict as a YAML list item with nested keys.
    """
    prefix = ' ' * indent
    content_indent = indent + 2
    is_first = True

    for key, value in item.items():

        # The first key gets the dash prefix ..
        if is_first:
            line_prefix = f'{prefix}- '
            is_first = False

        # .. subsequent keys are indented to align with the first.
        else:
            line_prefix = f'{prefix}  '

        _write_mapping_entry(file_handle, line_prefix, key, value, content_indent)

# ################################################################################################################################
# ################################################################################################################################

# The markers a pub/sub permission is stored with, which are not part of the pattern itself
_pubsub_prefixes_to_remove = ['pub=', 'sub=']

# ################################################################################################################################

def _write_list_field(file_handle:'any_', element:'str', field_name:'str', value:'anylist') -> 'None':
    """ Writes one list-valued field of a top-level item, its items being either dicts of their
    own or scalars.
    """
    _ = file_handle.write(f'    {field_name}:\n')

    for list_item in value:

        if isinstance(list_item, dict):
            _write_dict_list_item(file_handle, list_item)

        else:
            cleaned_item = str(list_item)

            # A permission is stored with the direction it applies to prefixed, which the
            # section it is written to already says
            if element == 'pubsub_permission':
                if field_name in ['pub', 'sub']:
                    for prefix in _pubsub_prefixes_to_remove:
                        if cleaned_item.startswith(prefix):
                            cleaned_item = cleaned_item[len(prefix):]
                            break

            quoted_cleaned = _yaml_quote(cleaned_item)
            _ = file_handle.write(f'      - {quoted_cleaned}\n')

# ################################################################################################################################
# ################################################################################################################################

def _write_dict_field(file_handle:'any_', field_name:'str', value:'anydict', indent:'int'=_Section_Field_Block_Indent) -> 'None':
    """ Writes a dict-valued field as a nested YAML mapping, with list values inside it
    rendered as YAML lists (e.g. the response_cache block of a channel).
    """
    prefix = ' ' * indent
    _ = file_handle.write(f'{prefix}{field_name}:\n')

    content_indent = indent + 2
    content_prefix = ' ' * content_indent

    for key, sub_value in value.items():
        _write_mapping_entry(file_handle, content_prefix, key, sub_value, content_indent)

# ################################################################################################################################
# ################################################################################################################################

class FileWriter:
    """ Writes an enmasse export to a YAML file, its sections and their fields in the canonical order.
    """

    def __init__(self, path:'str') -> 'None':
        self.path = path

# ################################################################################################################################

    def write(self, data_dict:'anydict') -> 'None':

        top_level = get_top_level_order()

        # Custom connector sections are dynamic, so any of them present on input goes last, in a stable order.
        custom_keys:'strlist' = []

        for key in data_dict:
            if key.startswith(ModuleCtx.Custom_Key_Prefix):
                custom_keys.append(key)

        custom_keys.sort()
        top_level.extend(custom_keys)

        with open(self.path, 'w') as file_handle:

            previous_had_data = False

            for element in top_level:

                if element in data_dict:

                    _ = file_handle.write(f'\n{element}:\n')
                    previous_had_data = True

                    section = data_dict[element]

                    # A mapping-valued section (e.g. alert_notifications) is one flat mapping
                    # of scalar fields rather than a list of items ..
                    if isinstance(section, dict):
                        fields = get_object_order(element)

                        for field in fields:
                            if field in section:
                                field_value = section[field]
                                _write_scalar_field(file_handle, '  ', field, field_value, _Section_Field_Block_Indent)

                        continue

                    # .. custom connector sections build their field order from the fields
                    # their items actually carry ..
                    if element.startswith(ModuleCtx.Custom_Key_Prefix):
                        fields = get_custom_object_order(section)
                    else:
                        fields = get_object_order(element)

                    # .. and each item of the section is written out field by field.
                    for item in section:

                        # The first field gets the dash prefix ..
                        first_field = fields[0]

                        if first_field in item:
                            first_value = item[first_field]
                            quoted_first = _yaml_quote(first_value)
                            _ = file_handle.write(f'  - {first_field}: {quoted_first}\n')

                        # .. and the remaining fields align under it.
                        for field in fields[1:]:

                            # A field marked :dict in the order is a nested mapping ..
                            if ':dict' in field:
                                field_parts = field.split(':')
                                actual_field = field_parts[0]

                                if actual_field in item:
                                    field_value = item[actual_field]
                                    _write_dict_field(file_handle, actual_field, field_value)

                            # .. a field marked :list is a YAML list ..
                            elif ':list' in field:
                                field_parts = field.split(':')
                                actual_field = field_parts[0]

                                if actual_field in item:
                                    field_value = item[actual_field]
                                    _write_list_field(file_handle, element, actual_field, field_value)

                            # .. and an unmarked field is written by whatever shape its value has.
                            elif field in item:
                                field_value = item[field]

                                if isinstance(field_value, list):
                                    _write_list_field(file_handle, element, field, field_value)
                                elif isinstance(field_value, dict):
                                    _write_dict_field(file_handle, field, field_value)
                                else:
                                    _write_scalar_field(file_handle, '    ', field, field_value, _Item_Field_Block_Indent)

                else:
                    # An empty section still gets its header so the file lists every section there is
                    if previous_had_data:
                        _ = file_handle.write(f'\n{element}:\n')
                    else:
                        _ = file_handle.write(f'{element}:\n')

                    previous_had_data = False

# ################################################################################################################################
# ################################################################################################################################
