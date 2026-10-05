# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Documents through a live server and the demo IMAP server - two IMAP connections created by enmasse, one invoking its
# service per attachment and one per message, each service reading self.request.input.documents(), with a bare CCD,
# an IHE XDM package, a plain zip and a two-attachment message in the mailbox, the messages marked seen once their
# documents were handled, and a package with a bad hash leaving its message unseen for the next run.

# stdlib
import time
from hashlib import sha1
from io import BytesIO
from json import loads
from zipfile import ZipFile

# pytest
import pytest

# Zato
from zato.common.api import Documents, EMAIL
from zato.common.hl7.ccda.paths import is_converter_installed
from zato.common.test import xdm_builder as builder
from zato.common.test.client import AdminClient
from zato.common.test.xdm_builder import XDMSubset, build_ccd_package, build_package, ccd_document, read_sample

from conftest import Attachment_Conn_Name, Attachment_Service_Name, Mailbox_User, Message_Conn_Name, Message_Service_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

_scheduler = EMAIL.IMAP.Scheduler
_source = Documents.Source

_sender = 'clinic@direct.example.com'

# How long a newly created connection is given to reach the server's connection store
_dispatch_wait_seconds = 60
_dispatch_poll_interval = 1

# What the CCD sample is about
_ccd_patient_family = 'Jones'

pytestmark = pytest.mark.skipif(not is_converter_installed(), reason='The FHIR converter is not installed')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def client(zato_server:'stranydict') -> 'AdminClient':
    out = AdminClient(zato_server['base_url'], zato_server['invoke_password'])
    return out

# ################################################################################################################################

@pytest.fixture(autouse=True)
def empty_mailbox(imap_test_server:'any_') -> 'any_':
    """ Both connections read the same demo mailbox, so each test starts with it empty.
    """
    imap_test_server.clear()
    yield
    imap_test_server.clear()

# ################################################################################################################################
# ################################################################################################################################

def _dispatch(client:'AdminClient', conn_name:'str', service:'str', invoke_with:'str') -> 'None':
    """ Runs the connection's job the way the scheduler does it - by invoking the dispatch service with the job's extra,
    retrying until the connection has propagated to the server.
    """
    payload = {
        _scheduler.Extra_Conn_Name: conn_name,
        _scheduler.Extra_Service: service,
        _scheduler.Extra_Invoke_With: invoke_with,
    }

    deadline = time.monotonic() + _dispatch_wait_seconds
    last_error = None

    while time.monotonic() < deadline:
        try:
            _ = client.invoke(_scheduler.Dispatch_Service, payload)
        except Exception as e:
            last_error = e
            time.sleep(_dispatch_poll_interval)
            continue
        else:
            return

    raise AssertionError(f'Could not invoke the dispatch service, last error: {last_error}')

# ################################################################################################################################

def _dispatch_attachments(client:'AdminClient') -> 'None':
    _dispatch(client, Attachment_Conn_Name, Attachment_Service_Name, _scheduler.InvokeWith.EachAttachment)

# ################################################################################################################################

def _dispatch_messages(client:'AdminClient') -> 'None':
    _dispatch(client, Message_Conn_Name, Message_Service_Name, _scheduler.InvokeWith.Message)

# ################################################################################################################################

def _recorded(zato_server:'stranydict', subject:'str') -> 'anylist':
    """ The lines a service recorded for the message with this subject, in the order they were written.
    """
    out = []

    with open(zato_server['evidence_file']) as evidence:
        for line in evidence:
            line = line.strip()
            if line:
                entry = loads(line)
                if entry['subject'] == subject:
                    out.append(entry)

    return out

# ################################################################################################################################

def _attachment(file_name:'str', content_type:'str', data:'bytes') -> 'stranydict':
    out = {'filename': file_name, 'content_type': content_type, 'payload': data}
    return out

# ################################################################################################################################

def _plain_zip() -> 'bytes':
    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zip_file:
        zip_file.writestr('Referral_Note.xml', read_sample('Referral_Note.ccda'))
        zip_file.writestr('Progress_Note.xml', read_sample('Progress_Note.ccda'))

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def _sha1(data:'bytes') -> 'str':
    out = sha1(data).hexdigest()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_bare_ccd_attachment_is_one_document(client:'AdminClient', imap_test_server:'any_', zato_server:'stranydict') -> 'None':

    subject = 'Referral for Mary Jones'
    ccd = read_sample('CCD.ccda')

    uid = imap_test_server.add_message(_sender, Mailbox_User, subject, 'Please see the attached summary.',
        [_attachment('CCD.xml', 'application/xml', ccd)])

    _dispatch_attachments(client)

    entries = _recorded(zato_server, subject)
    assert len(entries) == 1

    entry = entries[0]
    assert entry['service'] == Attachment_Service_Name
    assert entry['attachment'] == 'CCD.xml'
    assert entry['file_name'] == 'CCD.xml'
    assert entry['mime_type'] == 'application/xml'
    assert entry['size'] == len(ccd)
    assert entry['source'] == _source.Attachment
    assert entry['sha1'] == _sha1(ccd)
    assert entry['title'] == ''

    assert imap_test_server.is_seen(uid)

# ################################################################################################################################

def test_an_xdm_package_gives_its_documents_and_the_ccd_converts(
    client:'AdminClient', imap_test_server:'any_', zato_server:'stranydict') -> 'None':

    subject = 'XDM/1.0/DDM/Referral documents'
    package = build_ccd_package()

    uid = imap_test_server.add_message(_sender, Mailbox_User, subject, 'Documents attached as an XDM package.',
        [_attachment('IHE_XDM.zip', 'application/zip', package)])

    _dispatch_attachments(client)

    entries = _recorded(zato_server, subject)
    assert len(entries) == 2

    ccd = entries[0]
    assert ccd['attachment'] == 'IHE_XDM.zip'
    assert ccd['file_name'] == 'CCD.xml'
    assert ccd['mime_type'] == 'text/xml'
    assert ccd['source'] == _source.XDM
    assert ccd['title'] == 'Continuity of Care Document'
    assert ccd['patient_id'] == builder.Patient_ID_Parsed
    assert ccd['class_code'] == builder.Class_Code
    assert ccd['unique_id'] == '1.2.840.114350.1.13.0.1.7.8.688883.1001'
    assert ccd['sha1'] == _sha1(read_sample('CCD.ccda'))

    # The service converted the CCD it found in the package with self.ccda.to_fhir
    assert ccd['resource_count'] > 20
    assert ccd['patient_family'] == _ccd_patient_family

    pdf = entries[1]
    assert pdf['file_name'] == 'CCD.pdf'
    assert pdf['mime_type'] == 'application/pdf'
    assert pdf['source'] == _source.XDM
    assert 'resource_count' not in pdf

    assert imap_test_server.is_seen(uid)

# ################################################################################################################################

def test_a_plain_zip_gives_each_file(client:'AdminClient', imap_test_server:'any_', zato_server:'stranydict') -> 'None':

    subject = 'Notes for John Smith'

    uid = imap_test_server.add_message(_sender, Mailbox_User, subject, 'Two notes attached.',
        [_attachment('notes.zip', 'application/zip', _plain_zip())])

    _dispatch_attachments(client)

    entries = _recorded(zato_server, subject)
    assert len(entries) == 2

    assert entries[0]['file_name'] == 'Referral_Note.xml'
    assert entries[0]['source'] == _source.Zip
    assert entries[0]['mime_type'] == 'application/xml'
    assert entries[0]['sha1'] == _sha1(read_sample('Referral_Note.ccda'))

    assert entries[1]['file_name'] == 'Progress_Note.xml'
    assert entries[1]['source'] == _source.Zip
    assert entries[1]['sha1'] == _sha1(read_sample('Progress_Note.ccda'))

    assert imap_test_server.is_seen(uid)

# ################################################################################################################################

def test_a_message_gives_the_documents_of_all_its_attachments(
    client:'AdminClient', imap_test_server:'any_', zato_server:'stranydict') -> 'None':

    subject = 'Discharge of Robert Williams'
    summary = read_sample('Discharge_Summary.ccda')

    uid = imap_test_server.add_message(_sender, Mailbox_User, subject, 'Summary and the package.', [
        _attachment('Discharge_Summary.xml', 'application/xml', summary),
        _attachment('IHE_XDM.zip', 'application/zip', build_ccd_package()),
    ])

    _dispatch_messages(client)

    entries = _recorded(zato_server, subject)
    assert len(entries) == 3

    for entry in entries:
        assert entry['service'] == Message_Service_Name

    assert entries[0]['file_name'] == 'Discharge_Summary.xml'
    assert entries[0]['source'] == _source.Attachment
    assert entries[0]['sha1'] == _sha1(summary)

    assert entries[1]['file_name'] == 'CCD.xml'
    assert entries[1]['source'] == _source.XDM
    assert entries[1]['title'] == 'Continuity of Care Document'

    assert entries[2]['file_name'] == 'CCD.pdf'
    assert entries[2]['source'] == _source.XDM

    assert imap_test_server.is_seen(uid)

# ################################################################################################################################

def test_a_package_with_a_bad_hash_leaves_its_message_unseen(
    client:'AdminClient', imap_test_server:'any_', zato_server:'stranydict') -> 'None':

    subject = 'XDM/1.0/DDM/Damaged package'
    package = build_package([XDMSubset(builder.Default_Subset, [ccd_document(hash_override='0' * 40)])])

    uid = imap_test_server.add_message(_sender, Mailbox_User, subject, 'This package does not match its metadata.',
        [_attachment('IHE_XDM.zip', 'application/zip', package)])

    _dispatch_attachments(client)

    # Nothing was recorded because documents() refused the package ..
    assert _recorded(zato_server, subject) == []

    # .. and the message stays unseen so the next run receives it again.
    assert not imap_test_server.is_seen(uid)

# ################################################################################################################################
# ################################################################################################################################
