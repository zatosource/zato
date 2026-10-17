# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# ################################################################################################################################
# ################################################################################################################################

# The schema of a value of any type
Any_Type_Schema = {'description': 'Any type'}

# The OpenAPI schemas of the type names that annotations of models and services resolve to
Basic_Types = {

    # Any type
    'any_': Any_Type_Schema,
    'Any': Any_Type_Schema,
    'anynone': {'description': 'Any type, including null'},

    # No value
    'NoneType': {'type': 'null'},

    # Strings
    'str': {'type': 'string'},
    'str_': {'type': 'string'},
    'strnone': {'type': ['string', 'null']},
    'path_': {'type': 'string'},
    'Path': {'type': 'string'},
    'PosixPath': {'type': 'string'},
    'UUID': {'type': 'string', 'format': 'uuid'},

    # Integers
    'int': {'type': 'integer', 'format': 'int32'},
    'intnone': {'type': ['integer', 'null'], 'format': 'int32'},

    # Floating-point and decimal numbers
    'float': {'type': 'number', 'format': 'float'},
    'floatnone': {'type': ['number', 'null'], 'format': 'float'},
    'decimal_': {'type': 'number'},
    'decnone': {'type': ['number', 'null']},
    'Decimal': {'type': 'number'},

    # Booleans
    'bool': {'type': 'boolean'},
    'boolnone': {'type': ['boolean', 'null']},

    # Bytes
    'bytes': {'type': 'string', 'format': 'binary'},
    'bytesnone': {'type': ['string', 'null'], 'format': 'binary'},
    'bytearray': {'type': 'string', 'format': 'binary'},
    'strbytes': {'type': 'string'},

    # Dates and times
    'datetime': {'type': 'string', 'format': 'date-time'},
    'datetime_': {'type': 'string', 'format': 'date-time'},
    'datetimez': {'type': 'string', 'format': 'date-time'},
    'isotimestamp': {'type': 'string', 'format': 'date-time'},
    'dtnone': {'type': ['string', 'null'], 'format': 'date-time'},
    'date': {'type': 'string', 'format': 'date'},
    'date_': {'type': 'string', 'format': 'date'},
    'time': {'type': 'string', 'format': 'time'},
    'timedelta': {'type': 'string'},

    # Dicts
    'dict': {'type': 'object'},
    'dict_': {'type': 'object'},
    'Dict': {'type': 'object'},
    'Mapping': {'type': 'object'},
    'anydict': {'type': 'object'},
    'anydictnone': {'type': ['object', 'null']},
    'dictnone': {'type': ['object', 'null']},
    'stranydict': {'type': 'object'},
    'strdict': {'type': 'object'},
    'strdictnone': {'type': ['object', 'null']},
    'commondict': {'type': 'object'},
    'object': {'type': 'object'},

    # Dicts with typed values
    'strstrdict': {'type': 'object', 'additionalProperties': {'type': 'string'}},
    'strintdict': {'type': 'object', 'additionalProperties': {'type': 'integer'}},
    'strbooldict': {'type': 'object', 'additionalProperties': {'type': 'boolean'}},
    'strfloatdict': {'type': 'object', 'additionalProperties': {'type': 'number'}},
    'strdictdict': {'type': 'object', 'additionalProperties': {'type': 'object'}},
    'strlistdict': {'type': 'object', 'additionalProperties': {'type': 'array', 'items': {'type': 'object'}}},
    'strcalldict': {'type': 'object'},

    # Lists
    'list': {'type': 'array', 'items': {'type': 'object'}},
    'List': {'type': 'array', 'items': {'type': 'object'}},
    'strlist': {'type': 'array', 'items': {'type': 'string'}},
    'strlistnone': {'type': ['array', 'null'], 'items': {'type': 'string'}},
    'strlistempty': {'type': 'array', 'items': {'type': ['string', 'null']}},
    'intlist': {'type': 'array', 'items': {'type': 'integer'}},
    'intlistnone': {'type': ['array', 'null'], 'items': {'type': 'integer'}},
    'intlistempty': {'type': 'array', 'items': {'type': ['integer', 'null']}},
    'byteslist': {'type': 'array', 'items': {'type': 'string', 'format': 'binary'}},
    'pathlist': {'type': 'array', 'items': {'type': 'string'}},
    'anylist': {'type': 'array', 'items': {'type': 'object'}},
    'anylistnone': {'type': ['array', 'null'], 'items': {'type': 'object'}},
    'listnone': {'type': ['array', 'null'], 'items': {'type': 'object'}},
    'dictlist': {'type': 'array', 'items': {'type': 'object'}},
    'strdictlist': {'type': 'array', 'items': {'type': 'object'}},
    'strdictlistnone': {'type': ['array', 'null'], 'items': {'type': 'object'}},

    # Tuples are documented as arrays
    'tuple': {'type': 'array', 'items': {'type': 'object'}},
    'Tuple': {'type': 'array', 'items': {'type': 'object'}},
    'strtuple': {'type': 'array', 'items': {'type': 'string'}},
    'anytuple': {'type': 'array', 'items': {'type': 'object'}},
    'tuplist': {'type': 'array', 'items': {'type': 'object'}},

    # Sets are documented as arrays with unique items
    'set': {'type': 'array', 'items': {'type': 'object'}, 'uniqueItems': True},
    'Set': {'type': 'array', 'items': {'type': 'object'}, 'uniqueItems': True},
    'frozenset': {'type': 'array', 'items': {'type': 'object'}, 'uniqueItems': True},
    'FrozenSet': {'type': 'array', 'items': {'type': 'object'}, 'uniqueItems': True},
    'strset': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True},
    'intset': {'type': 'array', 'items': {'type': 'integer'}, 'uniqueItems': True},
    'anyset': {'type': 'array', 'items': {'type': 'object'}, 'uniqueItems': True},

    # Unions of scalar types
    'union': {'type': 'object'},
    'strint': {'type': ['string', 'integer']},
    'strintnone': {'type': ['string', 'integer', 'null']},
    'strintbool': {'type': ['string', 'integer', 'boolean']},
    'strorfloat': {'type': ['string', 'number']},
    'strordict': {'type': ['string', 'object']},
    'strordictnone': {'type': ['string', 'object', 'null']},
    'strorlist': {'type': ['string', 'array'], 'items': {'type': 'object'}},
    'listorstr': {'type': ['string', 'array'], 'items': {'type': 'object'}},
    'strorlistnone': {'type': ['string', 'array', 'null'], 'items': {'type': 'object'}},
    'dictorlist': {'type': ['object', 'array'], 'items': {'type': 'object'}},
}

# ################################################################################################################################
# ################################################################################################################################
