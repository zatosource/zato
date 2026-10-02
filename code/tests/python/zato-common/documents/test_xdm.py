# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What read_xdm makes of an IHE XDM package - the documents each submission set's metadata names, with what the metadata
# says about them, checked against the files themselves, and nothing that the metadata does not name.

# stdlib
from io import BytesIO
from zipfile import ZipFile

# pytest
import pytest

# Zato
from zato.common.api import Documents
from zato.common.documents.model import DocumentError
from zato.common.documents.xdm import read_xdm
from zato.common.hl7.ccda.convert import convert
from zato.common.hl7.ccda.paths import is_converter_installed
from zato.common.test import xdm_builder as builder
from zato.common.test.xdm_builder import XDMSubset, build_package, ccd_document, pdf_document, read_sample
from zato.server.commands import CommandsFacade

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.documents.model import doclist

# ################################################################################################################################
# ################################################################################################################################

_source = Documents.Source
_reason = Documents.Reason

_cid = 'cid-xdm'

# ################################################################################################################################
# ################################################################################################################################

def _read(package:'bytes') -> 'doclist':
    with ZipFile(BytesIO(package)) as zip_file:
        out = read_xdm(zip_file)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_package_gives_its_documents_in_metadata_order_with_their_metadata() -> 'None':
    documents = _read(build_package([XDMSubset(builder.Default_Subset, [ccd_document(), pdf_document()])]))

    assert len(documents) == 2

    ccd = documents[0]
    assert ccd.file_name == 'CCD.xml'
    assert ccd.mime_type == 'text/xml'
    assert ccd.source == _source.XDM
    assert ccd.title == 'Continuity of Care Document'
    assert ccd.patient_id == builder.Patient_ID_Parsed
    assert ccd.class_code == builder.Class_Code
    assert ccd.type_code == builder.Type_Code
    assert ccd.unique_id == '1.2.840.114350.1.13.0.1.7.8.688883.1001'
    assert ccd.creation_time == builder.Creation_Time
    assert ccd.language == builder.Language
    assert ccd.size == len(ccd.data)

    pdf = documents[1]
    assert pdf.file_name == 'CCD.pdf'
    assert pdf.mime_type == 'application/pdf'
    assert pdf.title == 'Continuity of Care Document (PDF)'
    assert pdf.unique_id == '1.2.840.114350.1.13.0.1.7.8.688883.1002'

# ################################################################################################################################

def test_the_ccd_inside_is_byte_identical_to_the_sample() -> 'None':
    documents = _read(build_package([XDMSubset(builder.Default_Subset, [ccd_document()])]))

    assert documents[0].data == read_sample('CCD.ccda')

# ################################################################################################################################

@pytest.mark.skipif(not is_converter_installed(), reason='The FHIR converter is not installed')
def test_the_ccd_inside_converts_to_fhir() -> 'None':
    documents = _read(build_package([XDMSubset(builder.Default_Subset, [ccd_document()])]))

    result = convert(documents[0].data, commands=CommandsFacade(), cid=_cid)

    assert result.root_template == 'CCD'
    assert result.resource_count > 20

# ################################################################################################################################

def test_files_the_metadata_does_not_name_are_left_out() -> 'None':
    subset = XDMSubset(builder.Default_Subset, [ccd_document()], extra_files={'Thumbs.db': b'\x00', 'notes.txt': b'hi'})

    documents = _read(build_package([subset]))

    assert len(documents) == 1
    assert documents[0].file_name == 'CCD.xml'

# ################################################################################################################################

def test_two_subsets_give_the_documents_of_both() -> 'None':
    first = XDMSubset('SUBSET01', [ccd_document()])
    second = XDMSubset('SUBSET02', [pdf_document()])

    documents = _read(build_package([first, second]))

    assert len(documents) == 2
    assert documents[0].file_name == 'CCD.xml'
    assert documents[1].file_name == 'CCD.pdf'

# ################################################################################################################################

def test_a_package_without_metadata_raises_no_metadata() -> 'None':
    subset = XDMSubset(builder.Default_Subset, [ccd_document()], with_metadata=False)

    with pytest.raises(DocumentError) as ctx:
        _ = _read(build_package([subset]))

    assert ctx.value.reason == _reason.No_Metadata

# ################################################################################################################################

def test_a_uri_naming_a_missing_file_raises_missing_file() -> 'None':
    subset = XDMSubset(builder.Default_Subset, [ccd_document(uri_override='Elsewhere.xml')])

    with pytest.raises(DocumentError) as ctx:
        _ = _read(build_package([subset]))

    assert ctx.value.reason == _reason.Missing_File
    assert ctx.value.file_name == 'Elsewhere.xml'

# ################################################################################################################################

def test_a_wrong_hash_raises_hash_mismatch() -> 'None':
    subset = XDMSubset(builder.Default_Subset, [ccd_document(hash_override='0' * 40)])

    with pytest.raises(DocumentError) as ctx:
        _ = _read(build_package([subset]))

    assert ctx.value.reason == _reason.Hash_Mismatch
    assert ctx.value.file_name == 'CCD.xml'

# ################################################################################################################################

def test_a_wrong_size_raises_size_mismatch() -> 'None':
    subset = XDMSubset(builder.Default_Subset, [ccd_document(size_override='1')])

    with pytest.raises(DocumentError) as ctx:
        _ = _read(build_package([subset]))

    assert ctx.value.reason == _reason.Size_Mismatch

# ################################################################################################################################

def test_metadata_without_hash_or_size_is_accepted() -> 'None':
    subset = XDMSubset(builder.Default_Subset, [ccd_document(state_hash=False, state_size=False)])

    documents = _read(build_package([subset]))

    assert len(documents) == 1
    assert documents[0].data == read_sample('CCD.ccda')

# ################################################################################################################################
# ################################################################################################################################
