# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A conversion through the converter installed for development - the same bundle whether the document arrives as text,
# bytes or base64, a transaction of typed resources with the original document in its DocumentReference, the same IDs
# on every run, no temporary files left behind, and each way the converter can fail reported under its own reason.

# stdlib
import os
from base64 import b64decode, b64encode
from tempfile import gettempdir

# pytest
import pytest

# Zato
from zato.common.api import HL7
from zato.common.hl7.ccda.convert import build_command, convert, to_document_bytes
from zato.common.hl7.ccda.exception import CCDAError
from zato.common.hl7.ccda.paths import get_binary_path, is_converter_installed
from zato.common.typing_ import cast_
from zato.server.commands import CommandsFacade

from conftest import read_sample

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from zato.fhir.r4_0_1.resources import Bundle

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA
_cid = 'cid-convert'

# What a conversion writes to the temporary directory while it runs
_Temp_Marker = '-zato-ccda.'

# What the CCD sample converts to
_CCD_Resource_Types = {'Composition', 'Patient', 'Practitioner', 'Organization', 'DocumentReference', 'AllergyIntolerance',
    'DiagnosticReport', 'Observation', 'Procedure'}

# The one value that differs between two conversions of one document - when the DocumentReference was written
_Document_Reference_Date_Key = 'date'

# The one resource of the CCD sample that is the patient
_CCD_Patient_Family_Name = 'Jones'

pytestmark = pytest.mark.skipif(not is_converter_installed(), reason='The FHIR converter is not installed')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def commands() -> 'CommandsFacade':
    out = CommandsFacade()
    return out

# ################################################################################################################################

def _temp_files() -> 'set':
    out = set()

    for name in os.listdir(gettempdir()):
        if _Temp_Marker in name:
            out.add(name)

    return out

# ################################################################################################################################

def _resources(bundle:'Bundle') -> 'anylist':
    out = []

    entries = cast_('anylist', bundle.entry)
    for entry in entries:
        out.append(entry.resource)

    return out

# ################################################################################################################################

def _one(bundle:'Bundle', resource_type:'str') -> 'any_':
    for resource in _resources(bundle):
        if resource.resource_type == resource_type:
            return resource

    raise AssertionError(f'No {resource_type} in the bundle')

# ################################################################################################################################

def _comparable(bundle:'Bundle') -> 'any_':
    """ The bundle as a dict without the one value that changes from run to run.
    """
    out = bundle.to_dict()

    for entry in out['entry']:
        resource = entry['resource']
        if resource['resourceType'] == 'DocumentReference':
            del resource[_Document_Reference_Date_Key]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_input_takes_text_bytes_and_base64() -> 'None':
    document = read_sample('CCD.ccda')

    assert to_document_bytes(document, _cid) == document
    assert to_document_bytes(document.decode('utf8'), _cid) == document
    assert to_document_bytes(b64encode(document), _cid) == document
    assert to_document_bytes(b64encode(document).decode('ascii'), _cid) == document

    # Leading whitespace and a byte order mark do not make a document base64
    assert to_document_bytes(b'\n  \xef\xbb\xbf' + document, _cid) == b'\n  \xef\xbb\xbf' + document

# ################################################################################################################################

def test_input_that_is_neither_xml_nor_base64_is_refused() -> 'None':
    with pytest.raises(CCDAError) as e:
        _ = to_document_bytes('MSH|^~\\&|SENDER|FACILITY|', _cid)

    assert e.value.reason == _ccda.Reason.Not_CDA
    assert e.value.cid == _cid

# ################################################################################################################################

def test_the_command_runs_the_installed_converter_with_quoted_paths() -> 'None':
    command = build_command("/tmp/in put's.xml", '/tmp/out.json', 'ProgressNote')

    assert command.startswith(get_binary_path() + ' convert -d ')
    assert '-r ProgressNote' in command
    assert "-n '/tmp/in put'\"'\"'s.xml'" in command
    assert command.endswith(' -f /tmp/out.json')

# ################################################################################################################################

def test_a_ccd_becomes_a_transaction_of_typed_resources(commands:'CommandsFacade', ccd_document:'bytes') -> 'None':
    result = convert(ccd_document, commands=commands, cid=_cid)

    assert result.root_template == 'CCD'
    assert result.document_size == len(ccd_document)
    assert result.duration_ms > 0

    bundle = result.bundle
    assert bundle.to_dict()['type'] == _ccda.Bundle_Type

    resources = _resources(bundle)
    assert len(resources) == result.resource_count
    assert len(resources) > 20

    # Every resource is a typed object rather than a dict, and every entry is a PUT of it under its own ID ..
    resource_types = set()

    entries = cast_('anylist', bundle.entry)
    for entry in entries:
        resource = entry.resource
        resource_types.add(resource.resource_type)

        request = entry.request
        assert request.method == 'PUT'
        assert request.url == f'{resource.resource_type}/{resource.id}'
        assert entry.fullUrl == f'urn:uuid:{resource.id}'

    assert _CCD_Resource_Types <= resource_types

    # .. and the patient is the one the document is about.
    patient = _one(bundle, 'Patient')
    assert patient.name[0].family == _CCD_Patient_Family_Name

# ################################################################################################################################

def test_the_document_reference_holds_the_original_document(commands:'CommandsFacade', ccd_document:'bytes') -> 'None':
    result = convert(ccd_document, commands=commands, cid=_cid)

    reference = _one(result.bundle, 'DocumentReference')
    attachment = reference.content[0].attachment

    assert attachment.contentType == _ccda.Content_Type
    assert b64decode(attachment.data) == ccd_document

# ################################################################################################################################

def test_text_bytes_and_base64_convert_to_the_same_bundle(commands:'CommandsFacade', ccd_document:'bytes') -> 'None':
    from_bytes  = convert(ccd_document, commands=commands, cid=_cid)
    from_text   = convert(ccd_document.decode('utf8'), commands=commands, cid=_cid)
    from_base64 = convert(b64encode(ccd_document), commands=commands, cid=_cid)

    assert _comparable(from_bytes.bundle) == _comparable(from_text.bundle)
    assert _comparable(from_bytes.bundle) == _comparable(from_base64.bundle)

# ################################################################################################################################

def test_each_kind_of_document_converts_with_its_own_template(commands:'CommandsFacade') -> 'None':
    samples = {
        'Discharge_Summary.ccda': 'DischargeSummary',
        'Progress_Note.ccda': 'ProgressNote',
        'Referral_Note.ccda': 'ReferralNote',
    }

    for name, root_template in samples.items():
        result = convert(read_sample(name), commands=commands, cid=_cid)

        assert result.root_template == root_template
        assert result.resource_count > 0
        assert _one(result.bundle, 'Composition').resource_type == 'Composition'

# ################################################################################################################################

def test_no_temporary_files_are_left_behind(commands:'CommandsFacade', ccd_document:'bytes') -> 'None':
    before = _temp_files()

    _ = convert(ccd_document, commands=commands, cid=_cid)

    assert _temp_files() == before

# ################################################################################################################################

def test_a_document_that_is_not_cda_is_refused_before_the_converter_runs(commands:'CommandsFacade') -> 'None':
    before = _temp_files()

    with pytest.raises(CCDAError) as e:
        _ = convert(b'<Patient xmlns="http://hl7.org/fhir"/>', commands=commands, cid=_cid)

    assert e.value.reason == _ccda.Reason.Not_CDA
    assert _temp_files() == before

# ################################################################################################################################

def test_a_converter_that_fails_is_reported_with_its_output(
    commands:'CommandsFacade', ccd_document:'bytes', monkeypatch:'any_', tmp_path:'any_') -> 'None':

    # The real binary with no templates to read - the converter starts, then fails on the empty directory
    os.symlink(get_binary_path(), str(tmp_path / _ccda.Binary_Name))
    (tmp_path / _ccda.Templates_Dir_Name / _ccda.Templates_Set_Name).mkdir(parents=True)
    monkeypatch.setenv(_ccda.Env_Dir, str(tmp_path))

    before = _temp_files()

    with pytest.raises(CCDAError) as e:
        _ = convert(ccd_document, commands=commands, cid=_cid)

    assert e.value.reason == _ccda.Reason.Converter_Failed
    assert e.value.exit_code != 0
    assert _temp_files() == before

# ################################################################################################################################

def test_a_missing_converter_is_reported_without_writing_anything(
    commands:'CommandsFacade', ccd_document:'bytes', monkeypatch:'any_', tmp_path:'any_') -> 'None':

    monkeypatch.setenv(_ccda.Env_Dir, str(tmp_path))

    before = _temp_files()

    with pytest.raises(CCDAError) as e:
        _ = convert(ccd_document, commands=commands, cid=_cid)

    assert e.value.reason == _ccda.Reason.Not_Installed
    assert str(tmp_path) in e.value.msg
    assert _temp_files() == before

# ################################################################################################################################
# ################################################################################################################################
