# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, segment

# ################################################################################################################################
# ################################################################################################################################

MSH_MDM = 'MSH|^~\\&|EHR|EHRFAC|HIM|HIMFAC|20240517143055||MDM^T02|MSG00005|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

Unmapped = 'urn:zato:hl7v2:extension/unmapped'

# ################################################################################################################################
# ################################################################################################################################

def _document_for(presentation:'str') -> 'tuple':
    """ Converts one MDM with the given TXA-3 and returns the DocumentReference with the bundle's warnings.
    """
    txa = segment('TXA', {1: '1', 2: 'DS^Discharge Summary^HL70270', 3: presentation, 12: 'DOC-1^EHR', 17: 'AU', 19: 'AV'})

    bundle = convert(MSH_MDM, PID, txa)
    document = one_resource(bundle, 'DocumentReference')

    return document, get_conversion_warnings(bundle)

# ################################################################################################################################
# ################################################################################################################################

class TestTXAPresentation:
    """ TXA-3 says how the document is presented, which is the content type of its attachment.
    """

    def test_table_code_becomes_a_mime_type(self) -> 'None':
        document, warnings = _document_for('AP')

        assert document['content'][0]['attachment']['contentType'] == 'application/octet-stream'
        assert 'extension' not in document
        assert warnings == []

# ################################################################################################################################

    def test_text_codes(self) -> 'None':
        for presentation in ('TX', 'FT', 'TEXT', 'TX^Text^HL70191'):
            document, warnings = _document_for(presentation)

            assert document['content'][0]['attachment']['contentType'] == 'text/plain'
            assert 'extension' not in document
            assert warnings == []

# ################################################################################################################################

    def test_mime_type_passes_through(self) -> 'None':
        document, warnings = _document_for('application/pdf')

        assert document['content'][0]['attachment']['contentType'] == 'application/pdf'
        assert 'extension' not in document
        assert warnings == []

# ################################################################################################################################

    def test_unknown_presentation_is_preserved(self) -> 'None':
        document, warnings = _document_for('CDA2')

        assert document['content'][0]['attachment']['contentType'] == 'text/plain'
        assert document['extension'] == [{'url': f'{Unmapped}/TXA-3', 'valueString': 'CDA2'}]
        assert warnings == []

# ################################################################################################################################

    def test_text_body_keeps_its_type(self) -> 'None':
        txa = segment('TXA', {1: '1', 2: 'DS^Discharge Summary^HL70270', 3: 'TX', 12: 'DOC-1^EHR', 17: 'AU', 19: 'AV'})
        obx = 'OBX|1|TX|||Patient was discharged in stable condition.||||||F'

        bundle = convert(MSH_MDM, PID, txa, obx)
        document = one_resource(bundle, 'DocumentReference')

        attachment = document['content'][0]['attachment']

        assert attachment['contentType'] == 'text/plain'
        assert 'data' in attachment

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
