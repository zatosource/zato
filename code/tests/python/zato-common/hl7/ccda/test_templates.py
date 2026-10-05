# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The root template a document converts with - read off the template IDs in its header for each kind of document the
# converter knows, the default for a document whose template is not among them, and a refusal of anything that is not
# a CDA document at all.

# pytest
import pytest

# Zato
from zato.common.api import HL7
from zato.common.hl7.ccda.exception import CCDAError
from zato.common.hl7.ccda.templates import get_root_template, Root_Template_By_OID

from conftest import read_sample

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA
_cid = 'cid-templates'

# Each sample and the template its header names
_Samples = [
    ('CCD.ccda', 'CCD'),
    ('Discharge_Summary.ccda', 'DischargeSummary'),
    ('Progress_Note.ccda', 'ProgressNote'),
    ('Referral_Note.ccda', 'ReferralNote'),
    ('Patient-1.ccda', 'CCD'),
    ('Unstructured_Document_embed.ccda', 'CCD'),
]

_Namespace = 'urn:hl7-org:v3'

# ################################################################################################################################
# ################################################################################################################################

def _document(template_ids:'list[str]', *, root_name:'str'='ClinicalDocument') -> 'bytes':
    """ A minimal document with the given template IDs in its header.
    """
    template_lines = []
    for template_id in template_ids:
        template_lines.append(f'<templateId root="{template_id}"/>')

    templates = ''.join(template_lines)

    text = f'<?xml version="1.0"?><{root_name} xmlns="{_Namespace}"><realmCode code="US"/>' + \
        f'<typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>{templates}' + \
        f'<id root="1.2.3"/><component/></{root_name}>'

    out = text.encode('utf8')
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('name, expected', _Samples)
def test_each_sample_names_its_template(name:'str', expected:'str') -> 'None':
    document = read_sample(name)
    assert get_root_template(document, _cid) == expected

# ################################################################################################################################

@pytest.mark.parametrize('oid, expected', sorted(Root_Template_By_OID.items()))
def test_each_known_template_is_recognised(oid:'str', expected:'str') -> 'None':
    document = _document(['2.16.840.1.113883.10.20.22.1.1', oid])
    assert get_root_template(document, _cid) == expected

# ################################################################################################################################

def test_a_document_with_an_unknown_template_converts_as_a_ccd() -> 'None':
    document = _document(['2.16.840.1.113883.10.20.22.1.1', '1.2.3.4.5'])
    assert get_root_template(document, _cid) == _ccda.Default_Root_Template

# ################################################################################################################################

def test_a_document_without_template_ids_converts_as_a_ccd() -> 'None':
    document = _document([])
    assert get_root_template(document, _cid) == _ccda.Default_Root_Template

# ################################################################################################################################

def test_a_root_element_that_is_not_a_clinical_document_is_refused() -> 'None':
    document = _document(['2.16.840.1.113883.10.20.22.1.2'], root_name='Patient')

    with pytest.raises(CCDAError) as e:
        _ = get_root_template(document, _cid)

    assert e.value.reason == _ccda.Reason.Not_CDA
    assert e.value.cid == _cid

# ################################################################################################################################

def test_text_that_is_not_xml_is_refused() -> 'None':
    with pytest.raises(CCDAError) as e:
        _ = get_root_template(b'MSH|^~\\&|SENDER|FACILITY|', _cid)

    assert e.value.reason == _ccda.Reason.Not_CDA

# ################################################################################################################################
# ################################################################################################################################
