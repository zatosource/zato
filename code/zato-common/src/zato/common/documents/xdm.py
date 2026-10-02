# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import posixpath
from hashlib import sha1
from xml.etree.ElementTree import fromstring, ParseError

# Zato
from zato.common.api import Documents
from zato.common.documents.model import Document, DocumentError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from xml.etree.ElementTree import Element
    from zipfile import ZipFile
    from zato.common.documents.model import doclist
    from zato.common.typing_ import strdict, strlist

    doclist = doclist
    Element = Element
    strdict = strdict
    strlist = strlist
    ZipFile = ZipFile

# ################################################################################################################################
# ################################################################################################################################

_xdm    = Documents.XDM
_reason = Documents.Reason

_rim = '{' + _xdm.NS_RIM + '}'

# The elements of a document entry
_Extrinsic_Object    = _rim + 'ExtrinsicObject'
_Slot                = _rim + 'Slot'
_Value               = _rim + 'Value'
_Name                = _rim + 'Name'
_Localized_String    = _rim + 'LocalizedString'
_Classification      = _rim + 'Classification'
_External_Identifier = _rim + 'ExternalIdentifier'

# The URI slot of a long location is split into numbered parts, each as `<number>|<part>`
_URI_Part_Separator = '|'

# A location the metadata may give as a file URL rather than a bare path
_File_Scheme = 'file://'

_Encoding = 'utf8'

# ################################################################################################################################
# ################################################################################################################################

def _slot_values(entry:'Element', name:'str') -> 'strlist':
    """ The values of one slot of a document entry, in order, or an empty list when the entry has no such slot.
    """
    out = []

    for slot in entry.iter(_Slot):
        if slot.attrib['name'] == name:
            for value in slot.iter(_Value):
                text = value.text
                if text is None:
                    text = ''
                out.append(text)

    return out

# ################################################################################################################################

def _slot_value(entry:'Element', name:'str') -> 'str':
    values = _slot_values(entry, name)

    if values:
        out = values[0]
    else:
        out = ''

    return out

# ################################################################################################################################

def _title(entry:'Element') -> 'str':
    """ The document's own name - the first localized string of the entry's Name, not of its classifications.
    """
    for child in entry:
        if child.tag == _Name:
            for localized in child.iter(_Localized_String):
                return localized.attrib['value']

    return ''

# ################################################################################################################################

def _classification(entry:'Element', scheme:'str') -> 'str':
    """ The code of one classification of the entry, which the metadata keeps as the node representation.
    """
    for item in entry.iter(_Classification):
        if item.get('classificationScheme') == scheme:
            return item.attrib['nodeRepresentation']

    return ''

# ################################################################################################################################

def _external_identifier(entry:'Element', scheme:'str') -> 'str':
    for item in entry.iter(_External_Identifier):
        if item.attrib['identificationScheme'] == scheme:
            return item.attrib['value']

    return ''

# ################################################################################################################################

def _location(entry:'Element') -> 'str':
    """ Where the entry's document is in the package, relative to the metadata file - a long location arrives
    in numbered parts that are put back together here.
    """
    values = _slot_values(entry, _xdm.Slot.URI)

    if len(values) == 1:
        out = values[0]
    else:
        numbered = []
        for value in values:
            number, _, part = value.partition(_URI_Part_Separator)
            numbered.append((int(number), part))

        numbered.sort()

        parts = []
        for _, part in numbered:
            parts.append(part)

        out = ''.join(parts)

    if out.startswith(_File_Scheme):
        out = out[len(_File_Scheme):]

    return out

# ################################################################################################################################

def _entry_names(zip_file:'ZipFile') -> 'strdict':
    """ The files of the archive by their lower-cased names - XDM comes from media where case does not count.
    """
    out = {}

    for info in zip_file.infolist():
        if not info.is_dir():
            out[info.filename.lower()] = info.filename

    return out

# ################################################################################################################################

def _verify(document:'Document', entry:'Element') -> 'None':
    """ What the metadata says about the document has to match the document itself.
    """
    expected_size = _slot_value(entry, _xdm.Slot.Size)
    if expected_size:
        if int(expected_size) != document.size:
            raise DocumentError(_reason.Size_Mismatch,
                f'Size of `{document.file_name}` is {document.size}, metadata says {expected_size}',
                file_name=document.file_name)

    expected_hash = _slot_value(entry, _xdm.Slot.Hash)
    if expected_hash:
        actual_hash = sha1(document.data).hexdigest()
        if actual_hash.lower() != expected_hash.lower():
            raise DocumentError(_reason.Hash_Mismatch,
                f'Hash of `{document.file_name}` is {actual_hash}, metadata says {expected_hash}',
                file_name=document.file_name)

# ################################################################################################################################

def _read_entry(zip_file:'ZipFile', names:'strdict', subset_dir:'str', entry:'Element') -> 'Document':
    """ One document entry of the metadata read from the package and checked against what the entry says.
    """
    location = _location(entry)
    path = posixpath.normpath(posixpath.join(subset_dir, location))

    if path.lower() not in names:
        raise DocumentError(_reason.Missing_File, f'Metadata names `{location}` but the package has no such file',
            file_name=location)

    name = names[path.lower()]
    data = zip_file.read(name)

    out = Document(
        data=data,
        file_name=posixpath.basename(name),
        mime_type=entry.attrib['mimeType'],
        size=len(data),
        source=Documents.Source.XDM,
        title=_title(entry),
        patient_id=_external_identifier(entry, _xdm.Scheme.Patient_ID),
        class_code=_classification(entry, _xdm.Scheme.Class_Code),
        type_code=_classification(entry, _xdm.Scheme.Type_Code),
        unique_id=_external_identifier(entry, _xdm.Scheme.Unique_ID),
        creation_time=_slot_value(entry, _xdm.Slot.Creation_Time),
        language=_slot_value(entry, _xdm.Slot.Language_Code),
    )

    _verify(out, entry)

    return out

# ################################################################################################################################

def _metadata_files(names:'strdict') -> 'strlist':
    """ The metadata file of each submission set, in the order the sets are named.
    """
    out = []

    prefix = _xdm.Dir.lower() + '/'
    suffix = '/' + _xdm.Metadata_File.lower()

    for lower_name, name in names.items():
        if lower_name.startswith(prefix):
            if lower_name.endswith(suffix):
                out.append(name)

    out.sort()
    return out

# ################################################################################################################################

def read_xdm(zip_file:'ZipFile') -> 'doclist':
    """ Every document that the metadata of every submission set of the package names, in metadata order.
    Anything in the package that no metadata names is left out.
    """
    names = _entry_names(zip_file)
    metadata_files = _metadata_files(names)

    if not metadata_files:
        raise DocumentError(_reason.No_Metadata, f'Package has an {_xdm.Dir} directory but no {_xdm.Metadata_File}')

    out = []

    for metadata_file in metadata_files:
        subset_dir = posixpath.dirname(metadata_file)

        try:
            root = fromstring(zip_file.read(metadata_file).decode(_Encoding))
        except (ParseError, UnicodeDecodeError) as e:
            raise DocumentError(_reason.No_Metadata, f'Cannot parse `{metadata_file}` -> {e}', file_name=metadata_file)

        for entry in root.iter(_Extrinsic_Object):
            out.append(_read_entry(zip_file, names, subset_dir, entry))

    return out

# ################################################################################################################################
# ################################################################################################################################
