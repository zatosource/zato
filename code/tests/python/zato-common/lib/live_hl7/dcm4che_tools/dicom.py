# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from struct import pack
from time import time_ns
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone

# ################################################################################################################################
# ################################################################################################################################

# Explicit VR Little Endian, the one transfer syntax the instances are written in
Transfer_Syntax = '1.2.840.10008.1.2.1'

# CT Image Storage
CT_SOP_Class = '1.2.840.10008.5.1.4.1.1.2'

# The root every generated UID starts with - the UUID-derived arc of the ISO tree
UID_Root = '2.25.'

# What the writer calls itself in the file meta information
Implementation_Class_UID = '2.25.4142400182'
Implementation_Version   = 'ZATO_LIVE_HL7'

# The image is a small square of this many pixels a side
Image_Side = 4

# Value representations whose length field is four bytes wide after two reserved bytes
_long_vrs = ('OB', 'OW', 'UN', 'SQ', 'UT')

# ################################################################################################################################
# ################################################################################################################################

class Element(NamedTuple):
    group: int
    element: int
    vr: str
    value: bytes

# ################################################################################################################################

class Instance(NamedTuple):
    patient_id: str
    patient_name: str
    accession: str
    study_uid: str
    series_uid: str
    sop_instance_uid: str
    path: str

# ################################################################################################################################
# ################################################################################################################################

# One counter per process so UIDs generated in the same nanosecond still differ
_uid_counter = 0

# ################################################################################################################################

def new_uid() -> 'str':
    """ A UID under the 2.25 root built from the clock, the process and a counter.
    """
    global _uid_counter
    _uid_counter += 1

    now = time_ns()
    pid = os.getpid()

    out = f'{UID_Root}{now}{pid}{_uid_counter}'
    return out

# ################################################################################################################################

def _even(value:'bytes', padding:'bytes') -> 'bytes':
    """ Pads a value to an even length, as every DICOM value must be.
    """
    if len(value) % 2 == 1:
        out = value + padding
    else:
        out = value

    return out

# ################################################################################################################################

def _text(value:'str') -> 'bytes':
    encoded = value.encode('ascii')

    out = _even(encoded, b' ')
    return out

# ################################################################################################################################

def _uid(value:'str') -> 'bytes':
    encoded = value.encode('ascii')

    out = _even(encoded, b'\x00')
    return out

# ################################################################################################################################

def _encode(element:'Element') -> 'bytes':
    """ One data element in explicit VR little endian.
    """
    header = pack('<HH', element.group, element.element) + element.vr.encode('ascii')
    length = len(element.value)

    if element.vr in _long_vrs:
        out = header + b'\x00\x00' + pack('<I', length) + element.value
    else:
        out = header + pack('<H', length) + element.value

    return out

# ################################################################################################################################

def _file_meta(sop_instance_uid:'str') -> 'bytes':
    """ The file meta information group, its own length first.
    """
    elements = [
        Element(0x0002, 0x0001, 'OB', b'\x00\x01'),
        Element(0x0002, 0x0002, 'UI', _uid(CT_SOP_Class)),
        Element(0x0002, 0x0003, 'UI', _uid(sop_instance_uid)),
        Element(0x0002, 0x0010, 'UI', _uid(Transfer_Syntax)),
        Element(0x0002, 0x0012, 'UI', _uid(Implementation_Class_UID)),
        Element(0x0002, 0x0013, 'SH', _text(Implementation_Version)),
    ]

    body = b''

    for element in elements:
        body += _encode(element)

    group_length = Element(0x0002, 0x0000, 'UL', pack('<I', len(body)))

    out = _encode(group_length) + body
    return out

# ################################################################################################################################

def _dataset(instance:'Instance', now:'datetime') -> 'bytes':
    """ The data set of a small CT image carrying the identifiers a worklist and a study are matched on.
    """
    study_date = now.strftime('%Y%m%d')
    study_time = now.strftime('%H%M%S')
    pixel_count = Image_Side * Image_Side
    pixel_data = pack('<H', 0) * pixel_count

    elements = [
        Element(0x0008, 0x0016, 'UI', _uid(CT_SOP_Class)),
        Element(0x0008, 0x0018, 'UI', _uid(instance.sop_instance_uid)),
        Element(0x0008, 0x0020, 'DA', _text(study_date)),
        Element(0x0008, 0x0030, 'TM', _text(study_time)),
        Element(0x0008, 0x0050, 'SH', _text(instance.accession)),
        Element(0x0008, 0x0060, 'CS', _text('CT')),
        Element(0x0010, 0x0010, 'PN', _text(instance.patient_name)),
        Element(0x0010, 0x0020, 'LO', _text(instance.patient_id)),
        Element(0x0020, 0x000D, 'UI', _uid(instance.study_uid)),
        Element(0x0020, 0x000E, 'UI', _uid(instance.series_uid)),
        Element(0x0020, 0x0010, 'SH', _text('1')),
        Element(0x0020, 0x0011, 'IS', _text('1')),
        Element(0x0020, 0x0013, 'IS', _text('1')),
        Element(0x0028, 0x0002, 'US', pack('<H', 1)),
        Element(0x0028, 0x0004, 'CS', _text('MONOCHROME2')),
        Element(0x0028, 0x0010, 'US', pack('<H', Image_Side)),
        Element(0x0028, 0x0011, 'US', pack('<H', Image_Side)),
        Element(0x0028, 0x0100, 'US', pack('<H', 16)),
        Element(0x0028, 0x0101, 'US', pack('<H', 16)),
        Element(0x0028, 0x0102, 'US', pack('<H', 15)),
        Element(0x0028, 0x0103, 'US', pack('<H', 0)),
        Element(0x7FE0, 0x0010, 'OW', pixel_data),
    ]

    out = b''

    for element in elements:
        out += _encode(element)

    return out

# ################################################################################################################################

def build_instance(
    directory:'str',
    *,
    patient_id:'str',
    patient_name:'str',
    accession:'str',
    study_uid:'strnone' = None,
    ) -> 'Instance':
    """ Writes one CT instance into the directory and returns where it is and what it carries.
    """
    if study_uid is None:
        study_uid = new_uid()

    series_uid = new_uid()
    sop_instance_uid = new_uid()
    path = os.path.join(directory, f'{sop_instance_uid}.dcm')

    instance = Instance(patient_id, patient_name, accession, study_uid, series_uid, sop_instance_uid, path)
    now = datetime.now()

    preamble = b'\x00' * 128 + b'DICM'
    file_meta = _file_meta(sop_instance_uid)
    dataset = _dataset(instance, now)

    with open(path, 'wb') as dicom_file:
        _ = dicom_file.write(preamble + file_meta + dataset)

    return instance

# ################################################################################################################################
# ################################################################################################################################
