# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from json import loads

# Zato
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_, stranydict, strnone

    bytesgen       = generator_[bytes, None, None]
    stranydict_gen = generator_[stranydict, None, None]

    stranydict = stranydict
    strnone    = strnone

# ################################################################################################################################
# ################################################################################################################################

# The keys a file reference travels under between the export program and the deliver service
Key_Job_ID          = 'job_id'
Key_Connection_Name = 'connection_name'
Key_Resource_Type   = 'resource_type'
Key_Count           = 'count'
Key_Path            = 'path'
Key_URL             = 'url'
Key_Is_Error_File   = 'is_error_file'

# The id of a FHIR resource, as its JSON form names it
Key_Resource_ID = 'id'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BulkExportFile:
    """ One NDJSON file of a bulk export, as a service receives it in self.request.input - the metadata
    comes from the export's manifest and nothing is read from disk until a service asks for it.
    """

    # Which export the file belongs to and which connection ran it
    job_id: 'str' = ''
    connection_name: 'str' = ''

    # What the file holds - the resource type, how many resources the server said it has, and whether
    # it lists what the server could not export rather than the exported resources themselves
    resource_type: 'str' = ''
    count: 'int' = 0
    is_error_file: 'bool' = False

    # Where the file is on disk and where it was downloaded from
    path: 'str' = ''
    url: 'str' = ''

# ################################################################################################################################

    def __iter__(self) -> 'stranydict_gen':
        out = self.resources()
        return out

# ################################################################################################################################

    def __len__(self) -> 'int':
        return self.count

# ################################################################################################################################

    @property
    def file_name(self) -> 'str':
        out = os.path.basename(self.path)
        return out

# ################################################################################################################################

    def lines(self) -> 'bytesgen':
        """ Yields the file's lines as they are on disk, one resource per line, without the trailing newline.
        """
        with open(self.path, 'rb') as file:
            for line in file:
                line = line.rstrip(b'\r\n')
                if line:
                    yield line

# ################################################################################################################################

    def resources(self) -> 'stranydict_gen':
        """ Yields the file's resources one at a time, each parsed from its own line.
        """
        for line in self.lines():
            out = loads(line)
            yield out

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':
        out = {
            Key_Job_ID: self.job_id,
            Key_Connection_Name: self.connection_name,
            Key_Resource_Type: self.resource_type,
            Key_Count: self.count,
            Key_Path: self.path,
            Key_URL: self.url,
            Key_Is_Error_File: self.is_error_file,
        }
        return out

# ################################################################################################################################

    @classmethod
    def from_dict(class_, data:'stranydict') -> 'BulkExportFile':
        out = class_()
        out.job_id          = data[Key_Job_ID]
        out.connection_name = data[Key_Connection_Name]
        out.resource_type   = data[Key_Resource_Type]
        out.count           = data[Key_Count]
        out.path            = data[Key_Path]
        out.url             = data[Key_URL]
        out.is_error_file   = data[Key_Is_Error_File]

        return out

# ################################################################################################################################

@dataclass(init=False)
class BulkExportResource:
    """ One resource of a bulk export file on its way to a destination - the line as it is in the file,
    the resource's own id and the file it came from.
    """
    file: 'BulkExportFile'
    data: 'str'
    resource_id: 'str'

    def __init__(self, file:'BulkExportFile', line:'bytes') -> 'None':
        self.file = file
        self.data = line.decode('utf8')

        # The id is optional in FHIR, a resource without one travels under an empty key
        resource = loads(self.data)
        resource_id = resource.get(Key_Resource_ID)
        if resource_id is None:
            resource_id = ''
        self.resource_id = resource_id

# ################################################################################################################################
# ################################################################################################################################

def new_file(
    job_id:'str',
    connection_name:'str',
    resource_type:'str',
    count:'int',
    path:'str',
    url:'str',
    ) -> 'BulkExportFile':
    """ Builds the reference of one downloaded file - an error file is told apart by its resource type.
    """
    out = BulkExportFile()
    out.job_id          = job_id
    out.connection_name = connection_name
    out.resource_type   = resource_type
    out.count           = count
    out.path            = path
    out.url             = url
    out.is_error_file   = resource_type == HL7.BulkExport.Error_Resource_Type

    return out

# ################################################################################################################################
# ################################################################################################################################
