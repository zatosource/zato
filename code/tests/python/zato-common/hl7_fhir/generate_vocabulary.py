# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Regenerates zato/hl7/mappings/vocabulary.py from the ConceptMap fixtures in fixtures/v2mappings.
# Run it after refreshing the fixtures with download_fixtures.sh.

# stdlib
import json
import os

# ################################################################################################################################
# ################################################################################################################################

# Where the ConceptMap fixtures live, relative to this file
_fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'v2mappings')

# Where the generated module goes, relative to this file
_output_path = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..',
    'zato-common', 'src', 'zato', 'hl7', 'mappings', 'vocabulary.py')

# Which vocabulary maps to generate - attribute name to the ConceptMap fixture it comes from
_map_sources = {
    'administrative_sex':        'table-hl70001-to-administrative-gender',
    'marital_status':            'table-hl70002-to-v3-maritalstatus',
    'patient_class':             'table-hl70004-to-v3-actcode',
    'patient_class_status':      'table-hl70004-to-encounter-status',
    'name_type':                 'table-hl70200-to-name-use',
    'address_type':              'table-hl70190-to-address-use',
    'telecom_use':               'table-hl70201-to-contact-point-use',
    'telecom_equipment_type':    'table-hl70202-to-contact-point-system',
    'diagnosis_type':            'table-hl70052-to-diagnosis-role',
    'abnormal_flags':            'table-hl70078-to-v3-observationinterpretation',
    'observation_result_status': 'table-hl70085-to-observation-status',
    'result_status':             'table-hl70123-queries-to-diagnostic-report-status',
    'allergy_category':          'table-hl70127-to-allergy-intolerance-category',
    'allergy_type':              'table-hl70127-to-allergy-intolerance-type',
    'allergy_criticality':       'table-hl70128-to-allergy-intolerance-criticality',
    'allergy_severity':          'table-hl70128-to-reaction-event-severity',
    'filler_status':             'table-hl70278-to-appointmentstatus',
    'completion_status':         'table-hl70322-to-event-status',
    'order_status':              'table-hl70119-to-request-status',
    'order_priority':            'table-hl70485-to-request-priority',
}

_header = '''# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module is generated from the HL7 v2-to-FHIR ConceptMap files
# by tests/python/zato-common/hl7_fhir/generate_vocabulary.py - do not edit it by hand.

# ################################################################################################################################
# ################################################################################################################################
'''

_footer = '''
# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

def extract_map(concept_map:'dict') -> 'dict':
    """ Pulls the code-to-code pairs out of one ConceptMap, keeping each target's system URI.
    Only groups with a target system carry mapped codes, the target-less group holds the unmapped ones.
    """
    codes = {}

    for group in concept_map['group']:
        group_target = group.get('target')
        if not group_target:
            continue

        for element in group['element']:
            source_code = element['code']

            for target in element.get('target', []):
                target_code = target.get('code')
                if target_code:
                    codes[source_code] = {'code': target_code, 'system': group_target}
                    break

    return codes

# ################################################################################################################################

def main() -> 'None':

    parts = [_header]

    # Build one dict and one system constant per configured map ..
    for map_name in sorted(_map_sources):
        fixture_id = _map_sources[map_name]
        fixture_path = os.path.join(_fixtures_dir, f'ConceptMap-{fixture_id}.json')

        with open(fixture_path) as fixture_file:
            concept_map = json.load(fixture_file)

        codes = extract_map(concept_map)

        source_uri = concept_map['group'][0]['source']

        lines = []
        lines.append(f'\n# {concept_map["title"]}')
        lines.append(f'# Source: {source_uri}')
        lines.append(f'{map_name} = {{')

        for source_code in codes:
            target = codes[source_code]
            lines.append(f'    {source_code!r}: {{\'code\': {target["code"]!r}, \'system\': {target["system"]!r}}},')

        lines.append('}')
        lines.append('')
        lines.append('# ' + 128 * '#')

        parts.append('\n'.join(lines))

    # .. record which fixture each map came from so tests can prove the module matches the spec ..
    source_lines = ['\n# Which ConceptMap fixture each map above was generated from']
    source_lines.append('table_sources = {')

    for map_name in sorted(_map_sources):
        fixture_id = _map_sources[map_name]
        source_lines.append(f'    {map_name!r}: {fixture_id!r},')

    source_lines.append('}')
    parts.append('\n'.join(source_lines))

    parts.append(_footer)

    # .. and write the module out.
    output = '\n'.join(parts)

    with open(_output_path, 'w') as output_file:
        _ = output_file.write(output)

    print(f'Wrote {os.path.normpath(_output_path)}')

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
