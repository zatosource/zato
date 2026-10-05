# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a service invoked by the IMAP or file transfer scheduler finds in self.request.input - the message, attachment
# or file itself, and what each one's documents() gives back.

# stdlib
from io import BytesIO

# Zato
from zato.common.api import Documents, IMAPAttachment, IMAPMessage
from zato.common.ext.imbox.parser import Struct
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.test.xdm_builder import build_ccd_package, read_sample
from zato.common.typing_ import cast_
from zato.server.service.reqresp import Request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_source = Documents.Source

_cid = 'cid-documents-input'

# ################################################################################################################################
# ################################################################################################################################

def _attachment_dict(file_name:'str', content_type:'str', data:'bytes') -> 'any_':
    out = {
        'filename': file_name,
        'size': len(data),
        'content': BytesIO(data),
        'content-type': content_type,
    }
    return out

# ################################################################################################################################

def _message(attachments:'anylist') -> 'IMAPMessage':
    """ A message the way the IMAP connection yields it - the data is what the email parser builds.
    """
    data = Struct(subject='Referral for Mary Jones', sent_from=[{'email': 'clinic@direct.example.com'}],
        attachments=attachments)

    out = IMAPMessage('42', cast_('any_', None), data)
    return out

# ################################################################################################################################

def _attachment(file_name:'str', content_type:'str', data:'bytes') -> 'IMAPAttachment':
    message = _message([_attachment_dict(file_name, content_type, data)])

    out = IMAPAttachment(message, file_name, content_type, len(data), data, None)
    return out

# ################################################################################################################################

def _file(file_name:'str', data:'bytes') -> 'FileTransferItem':
    out = FileTransferItem('sftp', 'Clinic Drop', 'Nightly', '/inbound', file_name, f'/inbound/{file_name}',
        len(data), '2026-01-14T09:30:00', data)
    return out

# ################################################################################################################################

def _init_request(payload:'any_') -> 'Request':
    request = Request(cast_('any_', None))
    request.payload = payload
    request.init(True, _cid, None, 'json', 'scheduler', {}, cast_('any_', None))

    return request

# ################################################################################################################################
# ################################################################################################################################

def test_an_attachment_is_the_input_untouched() -> 'None':
    attachment = _attachment('CCD.ccda', 'application/xml', read_sample('CCD.ccda'))

    request = _init_request(attachment)

    assert request.input is attachment

# ################################################################################################################################

def test_a_message_is_the_input_untouched() -> 'None':
    message = _message([])

    request = _init_request(message)

    assert request.input is message

# ################################################################################################################################

def test_a_file_is_the_input_untouched() -> 'None':
    item = _file('CCD.ccda', read_sample('CCD.ccda'))

    request = _init_request(item)

    assert request.input is item

# ################################################################################################################################

def test_an_attachment_unpacks_a_package() -> 'None':
    attachment = _attachment('package.zip', 'application/zip', build_ccd_package())

    documents = attachment.documents()

    assert len(documents) == 2
    assert documents[0].file_name == 'CCD.xml'
    assert documents[0].source == _source.XDM
    assert documents[0].data == read_sample('CCD.ccda')
    assert documents[1].file_name == 'CCD.pdf'

# ################################################################################################################################

def test_an_attachment_gives_a_bare_document() -> 'None':
    data = read_sample('Referral_Note.ccda')
    attachment = _attachment('Referral_Note.ccda', 'application/xml', data)

    documents = attachment.documents()

    assert len(documents) == 1
    assert documents[0].data == data
    assert documents[0].file_name == 'Referral_Note.ccda'
    assert documents[0].mime_type == 'application/xml'
    assert documents[0].source == _source.Attachment

# ################################################################################################################################

def test_a_file_unpacks_a_package() -> 'None':
    item = _file('package.zip', build_ccd_package())

    documents = item.documents()

    assert len(documents) == 2
    assert documents[0].source == _source.XDM
    assert documents[0].title == 'Continuity of Care Document'

# ################################################################################################################################

def test_a_file_gives_a_bare_document() -> 'None':
    data = read_sample('Discharge_Summary.ccda')
    item = _file('Discharge_Summary.xml', data)

    documents = item.documents()

    assert len(documents) == 1
    assert documents[0].data == data
    assert documents[0].mime_type == 'application/xml'
    assert documents[0].source == _source.Attachment

# ################################################################################################################################

def test_a_message_gives_the_documents_of_all_its_attachments_in_order() -> 'None':
    referral = read_sample('Referral_Note.ccda')
    message = _message([
        _attachment_dict('Referral_Note.ccda', 'application/xml', referral),
        _attachment_dict('package.zip', 'application/zip', build_ccd_package()),
        _attachment_dict('cover.txt', 'text/plain', b'Please see the attached referral.'),
    ])

    documents = message.documents()

    assert len(documents) == 4

    assert documents[0].file_name == 'Referral_Note.ccda'
    assert documents[0].source == _source.Attachment
    assert documents[0].data == referral

    assert documents[1].file_name == 'CCD.xml'
    assert documents[1].source == _source.XDM

    assert documents[2].file_name == 'CCD.pdf'
    assert documents[2].source == _source.XDM

    assert documents[3].file_name == 'cover.txt'
    assert documents[3].mime_type == 'text/plain'
    assert documents[3].source == _source.Attachment

# ################################################################################################################################
# ################################################################################################################################
