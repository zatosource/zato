# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# hl7apy
from hl7apy.parser import parse_message as hl7apy_parse_message

# Zato
from zato.common.api import HL7
from zato.common.hl7 import HL7Exception

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from hl7apy.core import Message
    from zato.common.typing_ import any_, boolnone
    any_ = any_
    boolnone = boolnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')
logger_hl7 = getLogger('zato_hl7')

# ################################################################################################################################
# ################################################################################################################################

# Maps HL7 versions and implementation classes to parse functions.
_parse_func_map = {
    HL7.Const.Version.v2.id: {
        HL7.Const.ImplClass.hl7apy: hl7apy_parse_message
    }
}

_impl_class = HL7.Const.ImplClass.hl7apy

# ################################################################################################################################
# ################################################################################################################################

def get_payload_from_request(
    data,           # type: str
    data_encoding,  # type: str
    hl7_version,    # type: str
    _ignored_json_path,             # type: boolnone
    _ignored_should_parse_on_input, # type: boolnone
    should_validate                 # type: bool
) -> 'Message':
    """ Parses a channel message into an HL7 one.
    """
    try:

        # We always require str objects ..
        if isinstance(data, bytes):
            data = data.decode(data_encoding)

        # .. now, parse and return the result.
        return parse(data, _impl_class, hl7_version, should_validate)

    except Exception as e:
        msg = 'Caught an HL7 exception while handling data:`%s` (%s); e:`%s`'
        logger.warning(msg, repr(data), repr(data_encoding), format_exc())
        raise HL7Exception('HL7 exception', data, e)

# ################################################################################################################################

def parse(
    data,            # type: str
    impl_class,      # type: any_
    hl7_version,     # type: str
    should_validate  # type: bool
) -> 'Message':
    """ Parses input data in the specified HL7 version using implementation pointed to be impl_class.
    """
    impl_dict = _parse_func_map[hl7_version] # type: dict
    parse_func = impl_dict[impl_class]

    return parse_func(data, force_validation=should_validate)

# ################################################################################################################################
# ################################################################################################################################
