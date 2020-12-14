# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# hl7apy
from hl7apy.parser import parse_message as hl7apy_parse_message

# Zato
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

# Maps HL7 versions and implementation classes to parse functions.
_parse_func_map = {
    HL7.Const.Version.v2.id: {
        HL7.Const.ImplClass.hl7apy: hl7apy_parse_message
    }
}

# ################################################################################################################################
# ################################################################################################################################

def get_payload_from_request(data:str, version:str, json_path:str, should_parse_on_input:bool):

    print()
    print(111, data)
    print(222, version)
    print(333, json_path)
    print(444, should_parse_on_input)
    print()

# ################################################################################################################################

def parse(data:str, impl_class:str, version:str, should_validate:bool):
    """ Parses input data in the specified HL7 version using implementation pointed to be impl_class.
    """
    impl_dict = _parse_func_map[version] # type: dict
    parse_func = impl_dict[impl_class]

    print(444, data)

    return parse_func(data)

# ################################################################################################################################
# ################################################################################################################################
