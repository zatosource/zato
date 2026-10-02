# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from base64 import b64decode, b64encode
from binascii import Error as Base64Error
from dataclasses import dataclass
from json import loads
from logging import getLogger
from shlex import quote
from tempfile import mkstemp

# Zato
from zato.common.api import HL7
from zato.common.hl7.ccda.exception import CCDAError
from zato.common.hl7.ccda.paths import get_binary_path, get_converter_dir, get_templates_dir, is_converter_installed
from zato.common.hl7.ccda.templates import get_root_template
from zato.common.typing_ import cast_
from zato.fhir.bundle import TransactionBuilder
from zato.fhir.r4_0_1 import resources as fhir_resources

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strbytes
    from zato.fhir.r4_0_1.resources import Bundle
    from zato.server.commands import CommandsFacade

    anylist    = anylist
    Bundle     = Bundle
    stranydict = stranydict
    strbytes   = strbytes

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_ccda = HL7.CCDA

# The suffixes of the temporary files a conversion writes and reads
_Input_Suffix  = '-zato-ccda.xml'
_Output_Suffix = '-zato-ccda.json'

# The converter's verb that converts one document, the key of its output document that holds the bundle
# and the keys of each of the bundle's entries
_Convert_Verb       = 'convert'
_Output_Bundle_Key  = 'FhirResource'
_Entry_Resource_Key = 'resource'
_Entry_Full_URL_Key = 'fullUrl'
_Resource_Type_Key  = 'resourceType'

# The resource that carries the original document, and where in it the document sits
_Document_Resource_Type = 'DocumentReference'
_Content_Key    = 'content'
_Attachment_Key = 'attachment'

# What a document starts with, once leading whitespace and a possible byte order mark are skipped
_XML_Start = b'<'
_BOM       = b'\xef\xbb\xbf'

_Encoding = 'utf8'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConvertResult:
    """ What one conversion produced, with what the audit log records about it.
    """
    bundle: 'Bundle'
    root_template: 'str'
    resource_count: 'int'
    document_size: 'int'
    duration_ms: 'int'

# ################################################################################################################################
# ################################################################################################################################

def to_document_bytes(document:'strbytes', cid:'str') -> 'bytes':
    """ Returns a document as bytes - text is encoded, bytes are kept, and anything that does not
    begin like XML is taken for base64, which is how a FHIR Binary carries its data.
    """
    if isinstance(document, str):
        out = document.encode(_Encoding)
    else:
        out = document

    # Skip what may precede the first tag ..
    head = out.lstrip()
    if head.startswith(_BOM):
        head = head[len(_BOM):]

    # .. and if it is not a tag, the document is base64 ..
    if not head.startswith(_XML_Start):
        try:
            out = b64decode(head, validate=True)
        except Base64Error as e:
            raise CCDAError(cid, _ccda.Reason.Not_CDA, f'Not XML and not base64 -> {e}')

    # .. otherwise it is what it looks like.
    return out

# ################################################################################################################################

def build_command(input_path:'str', output_path:'str', root_template:'str') -> 'str':
    """ Returns the shell command that converts one document.
    """
    parts = [
        get_binary_path(),
        _Convert_Verb,
        '-d', get_templates_dir(),
        '-r', root_template,
        '-n', input_path,
        '-f', output_path,
    ]

    quoted = []
    for part in parts:
        quoted.append(quote(part))

    out = ' '.join(quoted)
    return out

# ################################################################################################################################

def _write_input(document:'bytes') -> 'str':
    """ Writes a document to a temporary file and returns its path.
    """
    input_fd, out = mkstemp(suffix=_Input_Suffix)
    with os.fdopen(input_fd, 'wb') as input_file:
        _ = input_file.write(document)

    return out

# ################################################################################################################################

def _new_output_path() -> 'str':
    """ Returns the path of a temporary file for the converter to write to.
    """
    output_fd, out = mkstemp(suffix=_Output_Suffix)
    os.close(output_fd)

    return out

# ################################################################################################################################

def _remove(path:'str') -> 'None':
    if os.path.exists(path):
        os.remove(path)

# ################################################################################################################################

def _attach_document(resource_data:'stranydict', document:'bytes') -> 'None':
    """ Replaces the compressed copy of the document the converter leaves in the DocumentReference
    with the document itself, as the base64 of its bytes under its own content type.
    """
    attachment = {
        'contentType': _ccda.Content_Type,
        'data': b64encode(document).decode(_Encoding),
    }
    resource_data[_Content_Key] = [{_Attachment_Key: attachment}]

# ################################################################################################################################

def _load_bundle(output_path:'str', document:'bytes') -> 'Bundle':
    """ Reads what the converter wrote and returns it as a typed transaction bundle, with the original
    document in its DocumentReference.
    """
    with open(output_path, 'rb') as output_file:
        data = output_file.read()

    output:'stranydict' = loads(data)
    bundle_data:'stranydict' = output[_Output_Bundle_Key]

    # Each entry of the converter's bundle is a PUT of a resource under its own ID, and the builder
    # writes the same kind of entry, with the resource typed by its resourceType ..
    builder = TransactionBuilder()

    for entry in bundle_data['entry']:
        resource_data:'stranydict' = entry[_Entry_Resource_Key]

        if resource_data[_Resource_Type_Key] == _Document_Resource_Type:
            _attach_document(resource_data, document)

        resource_class = getattr(fhir_resources, resource_data[_Resource_Type_Key])
        resource = resource_class.from_dict(resource_data)
        _ = builder.update(resource, full_url=entry.get(_Entry_Full_URL_Key))

    # .. and the result is a transaction bundle of them.
    out = cast_('Bundle', builder.build())
    return out

# ################################################################################################################################

def convert(document:'strbytes', *, commands:'CommandsFacade', cid:'str') -> 'ConvertResult':
    """ Converts one C-CDA document to a FHIR bundle by running the converter once.
    """
    # The converter has to be there before anything is written ..
    if not is_converter_installed():
        converter_dir = get_converter_dir()
        raise CCDAError(cid, _ccda.Reason.Not_Installed, f'FHIR converter not found in `{converter_dir}`')

    # .. the document must be a CDA document, and its header says which template converts it ..
    document = to_document_bytes(document, cid)
    root_template = get_root_template(document, cid)

    input_path  = _write_input(document)
    output_path = _new_output_path()

    try:
        command = build_command(input_path, output_path, root_template)

        # .. one run of the converter is one conversion ..
        result = commands.invoke(command, cid=cid, timeout=_ccda.Timeout, command_logger=logger)

        # .. a run that did not finish is reported as such ..
        if result.is_timeout:
            raise CCDAError(cid, _ccda.Reason.Timeout, f'FHIR converter did not finish in {_ccda.Timeout}s')

        # .. and so is one that finished with an error ..
        if not result.is_ok:
            raise CCDAError(cid, _ccda.Reason.Converter_Failed, f'FHIR converter exited with {result.exit_code}',
                exit_code=result.exit_code, stderr=result.stderr)

        # .. otherwise the output file holds the bundle.
        bundle = _load_bundle(output_path, document)
        entries = cast_('anylist', bundle.entry)

        out = ConvertResult(
            bundle=bundle,
            root_template=root_template,
            resource_count=len(entries),
            document_size=len(document),
            duration_ms=int(result.total_time_sec * 1000),
        )

    finally:
        _remove(input_path)
        _remove(output_path)

    return out

# ################################################################################################################################
# ################################################################################################################################
