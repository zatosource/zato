# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from functools import cache

# PyYAML
from yaml import safe_load

# Zato
from zato.common.util.open_ import open_r
from zato.common.util.truncate.common import Max_Node_Count, Max_Recursion_Depth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist, strset
    dictlist = dictlist

    # The masked value and how many fields were masked in it
    masked_tuple = tuple[any_, int]

# ################################################################################################################################
# ################################################################################################################################

# What the value of every masked field is replaced with.
Masked_Value = '********'

# Whether a gateway's custom fields are masked when its configuration does not say.
Default_Masking_Custom_Enabled = True

# The directory holding one file per industry set, each named after its set.
_sets_directory = os.path.join(os.path.dirname(__file__), 'masking_sets')
_sets_suffix    = '.yaml'

# ################################################################################################################################
# ################################################################################################################################

@cache
def get_masking_config() -> 'dictlist':
    """ Returns every industry set as a dict of its name, label, position and fields, ordered by position.
    The files are read once per process.
    """

    # Our response to produce
    out:'dictlist' = []

    for file_name in os.listdir(_sets_directory):

        # Only the set files are read, anything else in the directory is not a set.
        if not file_name.endswith(_sets_suffix):
            continue

        full_path = os.path.join(_sets_directory, file_name)

        with open_r(full_path) as opened:
            data = safe_load(opened.read())

        masking_set = {
            'name': file_name.removesuffix(_sets_suffix),
            'label': data['label'],
            'position': data['position'],
            'fields': data['fields'],
        }

        out.append(masking_set)

    out.sort(key=lambda item: item['position'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def resolve_masked_fields(
    sets:'strlist',
    excluded:'strlist',
    custom_fields:'strlist',
    is_custom_enabled:'bool',
    ) -> 'strset':
    """ Returns the lowercase names of every field a gateway masks - the fields of its sets less the excluded ones,
    plus its custom fields unless they are switched off. Names are compared without regard to case.
    """

    # The fields of every set, by the set's name ..
    fields_by_set = {item['name']: item['fields'] for item in get_masking_config()}

    # .. the fields of the sets picked ..
    out:'strset' = set()

    for set_name in sets:
        if set_name not in fields_by_set:
            raise Exception(f'Unknown data masking set `{set_name}`')

        for field_name in fields_by_set[set_name]:
            out.add(field_name.lower())

    # .. less the ones left out one by one ..
    for field_name in excluded:
        out.discard(field_name.lower())

    # .. plus the custom fields, which can be switched off as a whole.
    if is_custom_enabled:
        for field_name in custom_fields:
            out.add(field_name.lower())

    return out

# ################################################################################################################################
# ################################################################################################################################

def _mask(value:'any_', field_names:'strset', depth:'int', counts:'anydict') -> 'None':
    """ Masks one container in place and descends into the containers it holds.
    """

    # Every visited container spends one unit of the walk budget ..
    counts['nodes'] += 1

    # .. once the budget is gone, the walk stops so pathological documents stay cheap ..
    if counts['nodes'] > Max_Node_Count:
        return

    # .. and containers below this depth are not descended into.
    if depth > Max_Recursion_Depth:
        return

    child_depth = depth + 1

    # A masked key has its whole value replaced, whatever it holds, and is not descended into -
    # a service may return keys other than strings, which never name a field ..
    if isinstance(value, dict):
        for key, child_value in value.items():
            if isinstance(key, str) and key.lower() in field_names:
                value[key] = Masked_Value
                counts['masked'] += 1
            else:
                _mask(child_value, field_names, child_depth, counts)

    # .. while arrays only lead to the containers they hold.
    elif isinstance(value, list):
        child_list:'anylist' = value
        for child_value in child_list:
            _mask(child_value, field_names, child_depth, counts)

# ################################################################################################################################
# ################################################################################################################################

def mask_fields(value:'any_', field_names:'strset') -> 'masked_tuple':
    """ Replaces the value of every dict key whose lowercase form is among the field names, at any depth and through lists.
    The value is modified in place and returned along with how many fields were masked.
    """
    counts = {'nodes': 0, 'masked': 0}

    _mask(value, field_names, 0, counts)

    out = (value, counts['masked'])
    return out

# ################################################################################################################################
# ################################################################################################################################
