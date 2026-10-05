# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from hashlib import sha1
from json import dumps

# Zato
from zato.common.api import Documents
from zato.common.typing_ import cast_
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.documents.model import Document
    from zato.common.typing_ import anylist, stranydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# Where each service appends one line per document it received - the test suite reads it back
_evidence_file = os.environ['Zato_Test_Documents_Evidence']

_xml_types = {'application/xml', 'text/xml', 'application/cda+xml'}

# ################################################################################################################################
# ################################################################################################################################

def describe(document:'Document') -> 'stranydict':
    out = {
        'file_name': document.file_name,
        'mime_type': document.mime_type,
        'size': document.size,
        'source': document.source,
        'title': document.title,
        'patient_id': document.patient_id,
        'class_code': document.class_code,
        'unique_id': document.unique_id,
        'sha1': sha1(document.data).hexdigest(),
    }
    return out

# ################################################################################################################################

def record(line:'stranydict') -> 'None':
    with open(_evidence_file, 'a') as evidence:
        _ = evidence.write(dumps(line) + '\n')

# ################################################################################################################################
# ################################################################################################################################

class DocumentsAttachment(Service):
    """ Behind the each-attachment connection - records each document of the attachment it received and converts
    the clinical ones that came out of an XDM package, the way a referral intake service would.
    """
    name = 'test.documents.attachment'

    def handle(self) -> 'None':
        attachment = self.request.input

        for document in attachment.documents():
            line = describe(document)
            line['subject'] = attachment.subject
            line['attachment'] = attachment.filename
            line['service'] = self.name

            if document.source == Documents.Source.XDM:
                if document.mime_type in _xml_types:
                    bundle = self.ccda.to_fhir(document.data)
                    entries = cast_('anylist', bundle.entry)
                    line['resource_count'] = len(entries)
                    for entry in entries:
                        if entry.resource.resource_type == 'Patient':
                            line['patient_family'] = entry.resource.name[0].family

            record(line)

# ################################################################################################################################
# ################################################################################################################################

class DocumentsMessage(Service):
    """ Behind the message connection - records every document of every attachment of the message it received.
    """
    name = 'test.documents.message'

    def handle(self) -> 'None':
        message = self.request.input

        for document in message.documents():
            line = describe(document)
            line['subject'] = message.data.subject
            line['service'] = self.name

            record(line)

# ################################################################################################################################
# ################################################################################################################################
