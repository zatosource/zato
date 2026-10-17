# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Date      = '2026-01-15'
    Date_Time = '2026-01-15T09:30:00+00:00'
    Email     = 'john.smith@example.com'
    Phone     = '+1 555 0100'
    URL       = 'https://example.com'
    Text      = 'Sample text'
    Id_Number = '1001'
    Code      = '01'

    # The length of the prefix that identifiers and codes take from the property name, e.g. PAT-1001 for patient_id
    Prefix_Length = 3

    Count   = 10
    Integer = 1

# ################################################################################################################################
# ################################################################################################################################

# Sample values of string properties whose whole name is known
_example_by_exact_name = {
    'id': ModuleCtx.Id_Number,
    'username': 'john.smith',
    'postal_code': '62704',
    'zip_code': '62704',
    'status': 'active',
    'state': 'IL',
    'country': 'US',
    'language': 'en',
    'currency': 'USD',
    'sex': 'female',
    'gender': 'female',
    'limit': '10',
    'page': '1',
    'page_size': '10',
    'max_results': '10',
    'period': '2026-Q1',
    'content_type': 'application/pdf',
    'content_base64': 'U2FtcGxlIGRvY3VtZW50',
}

# Sample values of string properties by how their names end, matched in this order
_example_by_name_suffix = [
    ('given_name',  'John'),
    ('first_name',  'John'),
    ('family_name', 'Smith'),
    ('last_name',   'Smith'),
    ('surname',     'Smith'),
    ('file_name',   'document.pdf'),
    ('birth_date',  '1980-05-17'),
    ('email',       ModuleCtx.Email),
    ('phone',       ModuleCtx.Phone),
    ('phone_number', ModuleCtx.Phone),
    ('street',      '1452 Maple Avenue'),
    ('city',        'Springfield'),
    ('url',         ModuleCtx.URL),
    ('date',        ModuleCtx.Date),
    ('_on',         ModuleCtx.Date),
    ('_at',         ModuleCtx.Date_Time),
    ('_time',       ModuleCtx.Date_Time),
    ('timestamp',   ModuleCtx.Date_Time),
    ('reason',      ModuleCtx.Text),
    ('text',        ModuleCtx.Text),
    ('note',        ModuleCtx.Text),
    ('comment',     ModuleCtx.Text),
    ('message',     ModuleCtx.Text),
    ('description', ModuleCtx.Text),
    ('summary',     ModuleCtx.Text),
]

# Integer properties whose names contain any of these words are counts or sizes
_count_words = ['count', 'limit', 'max', 'size', 'total', 'minutes', 'seconds', 'days', 'number']

# ################################################################################################################################
# ################################################################################################################################

def _get_prefixed_value(stem:'str', suffix:'str') -> 'str':
    """ Returns a value made of the uppercase start of a property name and a suffix, e.g. PAT-1001 for patient_id.
    """
    prefix = stem[:ModuleCtx.Prefix_Length]
    prefix = prefix.upper()

    out = f'{prefix}-{suffix}'
    return out

# ################################################################################################################################

def get_string_example(property_name:'str') -> 'strnone':
    """ Returns a sample value for a string property by its name, or None if the name says nothing about its values.
    """
    # Names known in full come first ..
    if out := _example_by_exact_name.get(property_name):
        return out

    # .. then identifiers and codes, which are derived from the rest of the name ..
    if property_name.endswith('_id'):
        stem = property_name.removesuffix('_id')
        out = _get_prefixed_value(stem, ModuleCtx.Id_Number)
        return out

    if property_name.endswith('_code'):
        stem = property_name.removesuffix('_code')
        out = _get_prefixed_value(stem, ModuleCtx.Code)
        return out

    # .. and then the endings that say what kind of value a property has.
    for suffix, value in _example_by_name_suffix:
        if property_name.endswith(suffix):
            out = value
            break
    else:
        out = None

    return out

# ################################################################################################################################

def get_integer_example(property_name:'str') -> 'int':
    """ Returns a sample value for an integer property by its name.
    """
    for word in _count_words:
        if word in property_name:
            out = ModuleCtx.Count
            break
    else:
        out = ModuleCtx.Integer

    return out

# ################################################################################################################################
# ################################################################################################################################
