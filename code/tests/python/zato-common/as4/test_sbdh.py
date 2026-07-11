# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import NS
from zato.common.util.xml_.core import qname
from zato.common.as4.sbdh import build_sbdh, parse_sbdh

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_document_type_prefix = 'busdox-docid-qns::urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
_document_type_suffix = '::Invoice##urn:cen.eu:en16931:2017#compliant#urn:fdc:peppol.eu:2017:poacc:billing:3.0::2.1'
Document_Type = _document_type_prefix + _document_type_suffix
Process_ID = 'urn:fdc:peppol.eu:2017:poacc:billing:01:1.0'

# ################################################################################################################################
# ################################################################################################################################

def _build() -> 'any_':
    invoice = etree.fromstring(b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"/>')

    out = build_sbdh(
        sender_scheme='iso6523-actorid-upis',
        sender_id='0192:991825827',
        receiver_scheme='iso6523-actorid-upis',
        receiver_id='0192:810418052',
        document_type=Document_Type,
        process_id=Process_ID,
        process_scheme='cenbii-procid-ubl',
        document_standard='urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
        document_type_version='2.1',
        instance_identifier='instance-1234',
        business_document=invoice,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSBDH:

    def test_header_validates_against_official_schema(self, sbdh_schema:'any_') -> 'None':
        wire = _build()
        root = etree.fromstring(wire)

        header = root.find(qname(NS.SBDH, 'StandardBusinessDocumentHeader'))
        sbdh_schema.assertValid(header)

# ################################################################################################################################

    def test_parse_roundtrip(self) -> 'None':
        wire = _build()

        info, business_document = parse_sbdh(wire)

        assert info.sender_id == '0192:991825827'
        assert info.sender_scheme == 'iso6523-actorid-upis'
        assert info.receiver_id == '0192:810418052'
        assert info.receiver_scheme == 'iso6523-actorid-upis'
        assert info.document_type == Document_Type
        assert info.process_id == Process_ID
        assert info.instance_identifier == 'instance-1234'

        assert business_document.tag.endswith('Invoice')

# ################################################################################################################################
# ################################################################################################################################
