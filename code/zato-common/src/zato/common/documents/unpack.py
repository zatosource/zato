# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import posixpath
from io import BytesIO
from mimetypes import guess_type
from os.path import splitext
from zipfile import BadZipFile, ZipFile

# Zato
from zato.common.api import Documents
from zato.common.documents.model import Document, DocumentError
from zato.common.documents.xdm import read_xdm

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.documents.model import doclist
    doclist = doclist

# ################################################################################################################################
# ################################################################################################################################

_xdm    = Documents.XDM
_reason = Documents.Reason
_source = Documents.Source

# ################################################################################################################################
# ################################################################################################################################

def is_zip(data:'bytes') -> 'bool':
    """ Whether the bytes are a zip archive, which is told by what they begin with rather than by any name.
    """
    out = data.startswith(Documents.Zip_Magic)
    return out

# ################################################################################################################################

def is_xdm(zip_file:'ZipFile') -> 'bool':
    """ Whether the archive is an IHE XDM package, which is any archive with an IHE_XDM directory at its root.
    """
    prefix = _xdm.Dir.lower() + '/'

    for name in zip_file.namelist():
        if name.lower().startswith(prefix):
            return True

    return False

# ################################################################################################################################

def _mime_type(file_name:'str', mime_type:'str') -> 'str':
    """ The type we were told about the data if there was one, otherwise what the file's name says.
    """
    if mime_type:
        out = mime_type
    else:
        _, extension = splitext(file_name)
        extension = extension.lower()

        if extension in Documents.Mime_Types:
            out = Documents.Mime_Types[extension]
        else:
            guessed, _ = guess_type(file_name)
            if guessed is None:
                out = Documents.Default_Mime_Type
            else:
                out = guessed

    return out

# ################################################################################################################################

def _read_zip(zip_file:'ZipFile') -> 'doclist':
    """ Each file of a plain archive as a document, directories left out, in archive order.
    """
    out = []

    for info in zip_file.infolist():
        if info.is_dir():
            continue

        data = zip_file.read(info)
        file_name = posixpath.basename(info.filename)

        out.append(Document(
            data=data,
            file_name=file_name,
            mime_type=_mime_type(file_name, ''),
            size=len(data),
            source=_source.Zip,
        ))

    return out

# ################################################################################################################################

def read_documents(data:'bytes', *, file_name:'str'='', mime_type:'str'='') -> 'doclist':
    """ The documents the bytes carry - the bytes themselves as one document unless they are a zip archive,
    in which case each file inside, or each document the metadata names if the archive is an IHE XDM package.
    """
    if not is_zip(data):
        out = [Document(
            data=data,
            file_name=file_name,
            mime_type=_mime_type(file_name, mime_type),
            size=len(data),
            source=_source.Attachment,
        )]
        return out

    try:
        zip_file = ZipFile(BytesIO(data))
    except BadZipFile as e:
        raise DocumentError(_reason.Bad_Zip, f'Cannot open archive `{file_name}` -> {e}', file_name=file_name)

    with zip_file:
        if is_xdm(zip_file):
            out = read_xdm(zip_file)
        else:
            out = _read_zip(zip_file)

    return out

# ################################################################################################################################
# ################################################################################################################################
