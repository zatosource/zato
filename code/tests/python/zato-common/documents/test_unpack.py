# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What read_documents makes of bytes that arrive as an attachment or a file - the bytes themselves unless they are
# a zip, each file of a plain zip, and the documents an XDM package's metadata names.

# stdlib
from io import BytesIO
from zipfile import ZipFile

# pytest
import pytest

# Zato
from zato.common.api import Documents
from zato.common.documents.model import DocumentError
from zato.common.documents.unpack import is_zip, read_documents
from zato.common.test.xdm_builder import build_ccd_package, read_sample

# ################################################################################################################################
# ################################################################################################################################

_source = Documents.Source
_reason = Documents.Reason

# ################################################################################################################################
# ################################################################################################################################

def _plain_zip() -> 'bytes':
    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zip_file:
        zip_file.writestr('notes/', '')
        zip_file.writestr('notes/Referral_Note.xml', read_sample('Referral_Note.ccda'))
        zip_file.writestr('notes/Progress_Note.xml', read_sample('Progress_Note.ccda'))

    out = buffer.getvalue()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_bare_attachment_is_one_document() -> 'None':
    data = read_sample('CCD.ccda')

    documents = read_documents(data, file_name='CCD.ccda', mime_type='application/xml')

    assert len(documents) == 1

    document = documents[0]
    assert document.data == data
    assert document.file_name == 'CCD.ccda'
    assert document.mime_type == 'application/xml'
    assert document.size == len(data)
    assert document.source == _source.Attachment
    assert document.title == ''
    assert document.patient_id == ''

# ################################################################################################################################

def test_bare_file_without_type_gets_type_from_its_name() -> 'None':
    documents = read_documents(b'%PDF-1.4', file_name='summary.pdf')

    assert documents[0].mime_type == 'application/pdf'

# ################################################################################################################################

def test_bare_file_without_type_or_known_name_is_an_octet_stream() -> 'None':
    documents = read_documents(b'\x00\x01', file_name='payload.unknownext')

    assert documents[0].mime_type == Documents.Default_Mime_Type

# ################################################################################################################################

def test_plain_zip_gives_each_file_and_skips_directories() -> 'None':
    documents = read_documents(_plain_zip(), file_name='notes.zip', mime_type='application/zip')

    assert len(documents) == 2

    assert documents[0].file_name == 'Referral_Note.xml'
    assert documents[0].data == read_sample('Referral_Note.ccda')
    assert documents[0].mime_type == 'application/xml'
    assert documents[0].source == _source.Zip

    assert documents[1].file_name == 'Progress_Note.xml'
    assert documents[1].data == read_sample('Progress_Note.ccda')
    assert documents[1].source == _source.Zip

# ################################################################################################################################

def test_non_zip_with_zip_name_is_a_bare_document() -> 'None':
    data = b'this is not an archive'

    documents = read_documents(data, file_name='archive.zip', mime_type='application/zip')

    assert len(documents) == 1
    assert documents[0].data == data
    assert documents[0].source == _source.Attachment
    assert not is_zip(data)

# ################################################################################################################################

def test_corrupt_zip_raises_bad_zip() -> 'None':
    data = Documents.Zip_Magic + b'\x00' * 40

    with pytest.raises(DocumentError) as ctx:
        _ = read_documents(data, file_name='broken.zip')

    assert ctx.value.reason == _reason.Bad_Zip
    assert ctx.value.file_name == 'broken.zip'

# ################################################################################################################################

def test_xdm_package_gives_the_documents_the_metadata_names() -> 'None':
    documents = read_documents(build_ccd_package(), file_name='package.zip', mime_type='application/zip')

    assert len(documents) == 2

    assert documents[0].file_name == 'CCD.xml'
    assert documents[0].source == _source.XDM
    assert documents[0].data == read_sample('CCD.ccda')
    assert documents[0].title == 'Continuity of Care Document'

    assert documents[1].file_name == 'CCD.pdf'
    assert documents[1].source == _source.XDM
    assert documents[1].mime_type == 'application/pdf'

# ################################################################################################################################
# ################################################################################################################################
