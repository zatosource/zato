# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.exception import ZatoException

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Document:
    """ One document read out of a container - an attachment on its own, a file of an archive or an entry of an
    IHE XDM package. The metadata fields are filled in from the package's metadata and are empty otherwise.
    """
    data: 'bytes'
    file_name: 'str'
    mime_type: 'str'
    size: 'int'
    source: 'str'

    title: 'str' = ''
    patient_id: 'str' = ''
    class_code: 'str' = ''
    type_code: 'str' = ''
    unique_id: 'str' = ''
    creation_time: 'str' = ''
    language: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

doclist = list[Document]

# ################################################################################################################################
# ################################################################################################################################

class DocumentError(ZatoException):
    """ Raised when a container cannot be read - the reason says whether the archive is broken, the package has no
    metadata, the metadata names a file that is not there or a file does not match what the metadata says about it.
    """
    msg: 'str'

    def __init__(self, reason:'str', msg:'str', *, file_name:'str'='') -> 'None':
        super().__init__(None, msg)
        self.reason = reason
        self.file_name = file_name

# ################################################################################################################################
# ################################################################################################################################
