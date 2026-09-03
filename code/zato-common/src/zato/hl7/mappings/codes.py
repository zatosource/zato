# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import vocabulary, vocabulary_supplement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist, strnone, strset
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# The base URI of all HL7 v2 table code systems
V2_Code_System_Prefix = 'http://terminology.hl7.org/CodeSystem/v2-'

# Well-known HL7 v2 coding system names and the URIs they stand for
Coding_Systems = {
    'LN':      'http://loinc.org',
    'LOINC':   'http://loinc.org',
    'SCT':     'http://snomed.info/sct',
    'SNM':     'http://snomed.info/sct',
    'SNOMED':  'http://snomed.info/sct',
    'UCUM':    'http://unitsofmeasure.org',
    'CVX':     'http://hl7.org/fhir/sid/cvx',
    'NDC':     'http://hl7.org/fhir/sid/ndc',
    'RXNORM':  'http://www.nlm.nih.gov/research/umls/rxnorm',
    'CPT':     'http://www.ama-assn.org/go/cpt',
    'CPT4':    'http://www.ama-assn.org/go/cpt',
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
    if name.startswith(('http://', 'https://', 'urn:')):

        out = name
        return out

    # .. an HL7 v2 table reference like HL70005 ..
    name_upper = name.upper()

    if name_upper.startswith('HL7'):
        table_number = name_upper[3:]
        if table_number.isdigit():

            out = V2_Code_System_Prefix + table_number
            return out

    # .. or one of the well-known coding system names.
    if uri := Coding_Systems.get(name_upper):

        out = uri
        return out

    return None

# ################################################################################################################################

def _build_vocabulary_maps() -> 'stranydict':
    """ Merges the generated vocabulary with its supplement into the maps lookup reads.
    """

    # Our response to produce
    out = {}

    # The generated maps come first ..
    for map_name in vocabulary.table_sources:
        generated_map = getattr(vocabulary, map_name)
        out[map_name] = dict(generated_map)

    # .. the supplement's additions layer on top of them ..
    for map_name, additions in vocabulary_supplement.Supplement.items():
        out[map_name].update(additions)

    # .. and the supplement-only maps complete the picture.
    for map_name, standalone_map in vocabulary_supplement.Standalone_Maps.items():
        out[map_name] = dict(standalone_map)

    return out

# ################################################################################################################################

# All the vocabulary maps, generated and supplemental, merged once at import time
_vocabulary_maps = _build_vocabulary_maps()

# ################################################################################################################################

def vocabulary_map_names() -> 'strlist':
    """ Returns the names of all the vocabulary maps a config file may override, sorted.
    """
    out = sorted(_vocabulary_maps)
    return out

# ################################################################################################################################

def vocabulary_map_systems(map_name:'str') -> 'strlist':
    """ Returns the distinct code systems the entries of one vocabulary map point to, sorted.
    """
    vocabulary_map = _vocabulary_maps[map_name]

    # The systems our response is sorted from
    systems:'strset' = set()

    for entry in vocabulary_map.values():
        systems.add(entry['system'])

    out = sorted(systems)
    return out

# ################################################################################################################################

def vocabulary_map_targets(map_name:'str', system:'str') -> 'strlist':
    """ Returns the codes one vocabulary map produces under a given system, sorted.
    """
    vocabulary_map = _vocabulary_maps[map_name]

    # The codes our response is sorted from
    targets:'strset' = set()

    for entry in vocabulary_map.values():
        if entry['system'] == system:
            targets.add(entry['code'])

    out = sorted(targets)
    return out

# ################################################################################################################################

def lookup(map_name:'str', code:'strnone', config:'FHIRMappingConfig') -> 'stranydict | None':
    """ Looks a code up in a vocabulary map, letting per-config overrides win over the generated data.
    Returns a dict with 'code' and 'system' keys or None when the code is not mapped anywhere.
    """
    if not code:
        return None

    # Config overrides take precedence over the generated map ..
    if overrides := config.code_mappings.get(map_name):
        if override := overrides.get(code):

            out = override
            return out

    # .. otherwise the generated map decides.
    vocabulary_map = _vocabulary_maps[map_name]

    if entry := vocabulary_map.get(code):

        out = entry
        return out

    return None

# ################################################################################################################################
# ################################################################################################################################
