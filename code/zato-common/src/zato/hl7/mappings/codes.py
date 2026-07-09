# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import vocabulary

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strnone
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# The base all HL7 v2 table code systems live under
V2_Code_System_Prefix = 'http://terminology.hl7.org/CodeSystem/v2-'

# Well-known HL7 v2 coding system names and the URIs they stand for
coding_systems = {
    'LN':      'http://loinc.org',
    'LOINC':   'http://loinc.org',
    'SCT':     'http://snomed.info/sct',
    'SNM':     'http://snomed.info/sct',
    'SNOMED':  'http://snomed.info/sct',
    'UCUM':    'http://unitsofmeasure.org',
    'CVX':     'http://hl7.org/fhir/sid/cvx',
    'NDC':     'http://hl7.org/fhir/sid/ndc',
    'CPT':     'http://www.ama-assn.org/go/cpt',
    'C4':      'http://www.ama-assn.org/go/cpt',
    'I10':     'http://hl7.org/fhir/sid/icd-10',
    'ICD10':   'http://hl7.org/fhir/sid/icd-10',
    'I9':      'http://hl7.org/fhir/sid/icd-9-cm',
    'I9C':     'http://hl7.org/fhir/sid/icd-9-cm',
    'ICD9':    'http://hl7.org/fhir/sid/icd-9-cm',
    'ISO3166': 'urn:iso:std:iso:3166',
    'ISO639':  'urn:ietf:bcp:47',
}

# ################################################################################################################################
# ################################################################################################################################

def coding_system_to_uri(name:'strnone') -> 'strnone':
    """ Translates an HL7 v2 coding system name (CWE-3 and friends) to a canonical URI.
    Table names like HL70005 become terminology.hl7.org URIs, URLs pass through unchanged.
    """
    if not name:
        return None

    name = name.strip()
    if not name:
        return None

    # Already a URI - use it as-is ..
    if name.startswith('http://'):
        return name

    if name.startswith('https://'):
        return name

    if name.startswith('urn:'):
        return name

    # .. an HL7 v2 table reference like HL70005 ..
    name_upper = name.upper()

    if name_upper.startswith('HL7'):
        table_number = name_upper[3:]
        if table_number.isdigit():

            out = V2_Code_System_Prefix + table_number
            return out

    # .. or one of the well-known coding system names.
    if name_upper in coding_systems:

        out = coding_systems[name_upper]
        return out

    return None

# ################################################################################################################################

def lookup(map_name:'str', code:'strnone', config:'FHIRMappingConfig') -> 'stranydict | None':
    """ Looks a code up in a vocabulary map, letting per-config overrides win over the generated data.
    Returns a dict with 'code' and 'system' keys or None when the code is not mapped anywhere.
    """
    if not code:
        return None

    vocabulary_map = getattr(vocabulary, map_name)

    # Config overrides take precedence over the generated map ..
    if overrides := config.code_mappings.get(map_name):
        if code in overrides:

            # .. an override carries only the target code, so the system comes from the map itself -
            # .. from the entry the code replaces or, for new codes, from the map's first entry.
            if code in vocabulary_map:
                system = vocabulary_map[code]['system']
            else:
                first_entry = next(iter(vocabulary_map.values()))
                system = first_entry['system']

            out = {'code': overrides[code], 'system': system}
            return out

    # .. otherwise the generated map decides.
    if code in vocabulary_map:

        out = vocabulary_map[code]
        return out

    return None

# ################################################################################################################################
# ################################################################################################################################
