# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7MLLPChannelConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    service: strnone = None
    security_name: strnone = None

    # The channel's destination list as it is stored, plus how many destinations that comes to -
    # a channel that declares none keeps the empty string and the count of zero.
    destinations: str = ''
    destination_count: int = 0

    # The MSH fields the channel matches incoming messages on, a field left empty matching
    # anything, plus the one line the whole match comes to when it is written out.
    msh3_sending_app: str = ''
    msh4_sending_facility: str = ''
    msh5_receiving_app: str = ''
    msh6_receiving_facility: str = ''
    msh9_message_type: str = ''
    msh9_trigger_event: str = ''
    msh11_processing_id: str = ''
    msh12_version_id: str = ''
    match_label: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7MLLPOutconnConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    address: str = ''
    security_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7RESTChannelConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    hl7_version: str = ''
    url_path: str = ''
    service_name: strnone = None
    security_id: strnone = None
    security_name: strnone = None
    sec_type: strnone = None
    sec_type_name: strnone = None
    data_format: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7FHIRConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    address: str = ''
    security_id: strnone = None
    security_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################
