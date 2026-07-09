# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from zato.hl7.mappings.config import FHIRMappingConfig as FHIRMappingConfig
from zato.hl7.mappings.config import add_config_location as add_config_location
from zato.hl7.mappings.config import load_mapping_config as load_mapping_config
from zato.hl7.mappings.context import get_conversion_warnings as get_conversion_warnings
from zato.hl7.mappings.messages import convert_to_fhir as convert_to_fhir
