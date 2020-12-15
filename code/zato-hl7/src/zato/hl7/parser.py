# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

def get_payload_from_request(data, data_encoding, hl7_version, json_path, should_parse_on_input, should_validate):
    """ Parses a channel message into an HL7 one.
    """
    # type: (str, str, str, bool, bool)
    try:

        # We always require str objects ..
        if isinstance(data, bytes):
            data = data.decode(data_encoding)

        # .. now, parse and return the result.
        return parse(data, _impl_class, hl7_version, should_validate)

    except Exception as e:
        msg = 'Caught an HL7 exception while handling data:`%s` (%s); e:`%s`'
        logger.warn(msg, repr(data), repr(data_encoding), format_exc())
        raise HL7Exception('HL7 exception', data, e)

# ################################################################################################################################

def parse(data, impl_class, hl7_version, should_validate):
    """ Parses input data in the specified HL7 version using implementation pointed to be impl_class.
    """
    impl_dict = _parse_func_map[hl7_version] # type: dict
    parse_func = impl_dict[impl_class]

    return parse_func(data, force_validation=should_validate)

# ################################################################################################################################
# ################################################################################################################################
