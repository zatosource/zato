# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Builds IHE XDM packages for the tests - a zip with the root manifests and, per submission set, the documents
# and an ebRIM metadata file naming each of them the way a Direct HISP or a USB stick would deliver it.

# stdlib
import os
from dataclasses import dataclass, field
from hashlib import sha1
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

# Zato
from zato.common.api import Documents

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

_xdm = Documents.XDM

# The C-CDA samples are the converter suite's own
Samples_Dir = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'tests', 'python', 'zato-common', 'hl7', 'ccda', 'samples')

# The values the metadata of the test packages describes its documents with
Patient_ID = '998877^^^&amp;1.2.840.114350.1.13.0.1.7.5.737384.14&amp;ISO'

# What the parser gives back for the escaped patient id above
Patient_ID_Parsed = '998877^^^&1.2.840.114350.1.13.0.1.7.5.737384.14&ISO'
Class_Code = '34133-9'
Type_Code = '34133-9'
Language = 'en-US'
Creation_Time = '20260114093000'

Default_Subset = 'SUBSET01'

# The ebRIM object types and nodes the metadata uses
_Object_Type_Prefix = 'urn:oasis:names:tc:ebxml-regrep:ObjectType:RegistryObject:'
_Registry_Package_Type = _Object_Type_Prefix + 'RegistryPackage'
_Classification_Type = _Object_Type_Prefix + 'Classification'
_External_Identifier_Type = _Object_Type_Prefix + 'ExternalIdentifier'
_Document_Entry_Type = 'urn:uuid:7edca82f-054d-47f2-a032-9b2a5b5186c1'
_Submission_Set_Node = 'urn:uuid:a54d6aa5-d40d-43f9-88c5-b4633d873bdd'
_Submission_Set = 'SubmissionSet01'
_LOINC = '2.16.840.1.113883.6.1'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class XDMDocument:
    """ One document to put in a package - what the metadata says about it is what the tests check later.
    """
    file_name: 'str'
    data: 'bytes'
    mime_type: 'str'
    title: 'str'
    unique_id: 'str'

    # The hash and size the metadata states - by default the real ones, a test may state wrong ones or none
    state_hash: 'bool' = True
    state_size: 'bool' = True
    hash_override: 'str' = ''
    size_override: 'str' = ''

    # Where the metadata says the file is, by default its own name
    uri_override: 'str' = ''

# ################################################################################################################################

@dataclass
class XDMSubset:
    name: 'str'
    documents: 'list[XDMDocument]'

    # Files put in the subset directory that the metadata does not name
    extra_files: 'dict[str, bytes]' = field(default_factory=dict)

    # Whether to write the metadata file at all
    with_metadata: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

def read_sample(name:'str') -> 'bytes':
    path = os.path.join(Samples_Dir, name)

    with open(path, 'rb') as sample_file:
        out = sample_file.read()

    return out

# ################################################################################################################################

def _slot(name:'str', value:'str') -> 'str':
    out = f'<rim:Slot name="{name}"><rim:ValueList><rim:Value>{value}</rim:Value></rim:ValueList></rim:Slot>'
    return out

# ################################################################################################################################

def _classification(scheme:'str', code:'str', classified:'str') -> 'str':
    parts = [
        f'<rim:Classification classificationScheme="{scheme}" classifiedObject="{classified}" ',
        f'nodeRepresentation="{code}" id="cl-{code}-{classified}" objectType="{_Classification_Type}">',
        _slot('codingScheme', _LOINC),
        '<rim:Name><rim:LocalizedString value="Summary of episode note"/></rim:Name>',
        '</rim:Classification>',
    ]

    out = ''.join(parts)
    return out

# ################################################################################################################################

def _external_identifier(scheme:'str', value:'str', classified:'str', name:'str') -> 'str':
    parts = [
        f'<rim:ExternalIdentifier identificationScheme="{scheme}" value="{value}" registryObject="{classified}" ',
        f'id="ei-{name}-{classified}" objectType="{_External_Identifier_Type}">',
        f'<rim:Name><rim:LocalizedString value="{name}"/></rim:Name>',
        '</rim:ExternalIdentifier>',
    ]

    out = ''.join(parts)
    return out

# ################################################################################################################################

def _entry(index:'int', document:'XDMDocument') -> 'str':
    """ The ExtrinsicObject of one document.
    """
    entry_id = f'Document{index:02d}'

    if document.uri_override:
        uri = document.uri_override
    else:
        uri = document.file_name

    slots:'strlist' = [_slot(_xdm.Slot.Creation_Time, Creation_Time), _slot(_xdm.Slot.Language_Code, Language)]

    if document.state_hash:
        if document.hash_override:
            hash_value = document.hash_override
        else:
            hash_value = sha1(document.data).hexdigest()
        slots.append(_slot(_xdm.Slot.Hash, hash_value))

    if document.state_size:
        if document.size_override:
            size_value = document.size_override
        else:
            size_value = str(len(document.data))
        slots.append(_slot(_xdm.Slot.Size, size_value))

    slots.append(_slot(_xdm.Slot.URI, uri))

    parts = [
        f'<rim:ExtrinsicObject id="{entry_id}" mimeType="{document.mime_type}" objectType="{_Document_Entry_Type}">',
        ''.join(slots),
        f'<rim:Name><rim:LocalizedString value="{document.title}"/></rim:Name>',
        '<rim:Description/>',
        _classification(_xdm.Scheme.Class_Code, Class_Code, entry_id),
        _classification(_xdm.Scheme.Type_Code, Type_Code, entry_id),
        _external_identifier(_xdm.Scheme.Patient_ID, Patient_ID, entry_id, 'XDSDocumentEntry.patientId'),
        _external_identifier(_xdm.Scheme.Unique_ID, document.unique_id, entry_id, 'XDSDocumentEntry.uniqueId'),
        '</rim:ExtrinsicObject>',
    ]

    out = ''.join(parts)
    return out

# ################################################################################################################################

def build_metadata(documents:'list[XDMDocument]') -> 'bytes':
    """ A SubmitObjectsRequest with one document entry per document and the submission set they belong to.
    """
    entries = []
    for index, document in enumerate(documents, 1):
        entries.append(_entry(index, document))

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<lcm:SubmitObjectsRequest xmlns:lcm="{_xdm.NS_LCM}" xmlns:rim="{_xdm.NS_RIM}">',
        '<rim:RegistryObjectList>',
        ''.join(entries),
        f'<rim:RegistryPackage id="{_Submission_Set}" objectType="{_Registry_Package_Type}">',
        _slot('submissionTime', Creation_Time),
        '<rim:Name><rim:LocalizedString value="Referral documents"/></rim:Name>',
        '</rim:RegistryPackage>',
        f'<rim:Classification classifiedObject="{_Submission_Set}" classificationNode="{_Submission_Set_Node}" ',
        f'id="cl-{_Submission_Set}" objectType="{_Classification_Type}"/>',
        '</rim:RegistryObjectList>',
        '</lcm:SubmitObjectsRequest>',
    ]

    out = ''.join(parts).encode('utf8')
    return out

# ################################################################################################################################

def build_package(subsets:'list[XDMSubset]') -> 'bytes':
    """ The zip bytes of a package with the given submission sets.
    """
    buffer = BytesIO()

    with ZipFile(buffer, 'w', ZIP_DEFLATED) as zip_file:
        zip_file.writestr('INDEX.HTM', '<html><body>Open IHE_XDM to find the documents.</body></html>')
        zip_file.writestr('README.TXT', 'Built by the Zato test suite.')

        for subset in subsets:
            directory = f'{_xdm.Dir}/{subset.name}'

            for document in subset.documents:
                zip_file.writestr(f'{directory}/{document.file_name}', document.data)

            for name, data in subset.extra_files.items():
                zip_file.writestr(f'{directory}/{name}', data)

            if subset.with_metadata:
                zip_file.writestr(f'{directory}/{_xdm.Metadata_File}', build_metadata(subset.documents))

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def ccd_document(**overrides:'object') -> 'XDMDocument':
    """ The CCD sample as a package document - the overrides change what the metadata states about it.
    """
    out = XDMDocument(
        file_name='CCD.xml',
        data=read_sample('CCD.ccda'),
        mime_type='text/xml',
        title='Continuity of Care Document',
        unique_id='1.2.840.114350.1.13.0.1.7.8.688883.1001',
    )

    for name, value in overrides.items():
        setattr(out, name, value)

    return out

# ################################################################################################################################

def pdf_document() -> 'XDMDocument':
    """ A small PDF standing in for the human-readable rendering that travels next to the CCD.
    """
    data = b'%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\ntrailer << /Root 1 0 R >>\n%%EOF\n'

    out = XDMDocument(
        file_name='CCD.pdf',
        data=data,
        mime_type='application/pdf',
        title='Continuity of Care Document (PDF)',
        unique_id='1.2.840.114350.1.13.0.1.7.8.688883.1002',
    )
    return out

# ################################################################################################################################

def build_ccd_package() -> 'bytes':
    """ The package most tests use - one subset with the CCD and its PDF rendering.
    """
    out = build_package([XDMSubset(Default_Subset, [ccd_document(), pdf_document()])])
    return out

# ################################################################################################################################
# ################################################################################################################################
