# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Make this directory importable so that test modules can import helpers from conftest
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.hl7.mappings.config import load_mapping_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from zato.hl7.mappings.config import FHIRMappingConfig
    any_ = any_
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

_here = os.path.dirname(__file__)

# Where all the downloaded proof material lives
Fixtures_Dir = os.path.join(_here, 'fixtures')

# The IG's ConceptMap and CodeSystem JSON files
V2_Mappings_Dir = os.path.join(Fixtures_Dir, 'v2mappings')

# The IG's agreed message-to-Bundle test conversion pairs
Test_Conversions_Dir = os.path.join(Fixtures_Dir, 'test_conversions')

# Sample HL7 v2 messages from the Microsoft FHIR-Converter project
Samples_Dir = os.path.join(Fixtures_Dir, 'messages', 'samples')

# Messages taken from real-world integration reports
Real_World_Dir = os.path.join(Fixtures_Dir, 'messages', 'real_world')

# ################################################################################################################################
# ################################################################################################################################

def load_message(file_path:'str') -> 'str':
    """ Reads an ER7 fixture, preserving the carriage returns HL7 uses as segment delimiters.
    """
    with open(file_path, newline='') as file_object:
        out = file_object.read()

    # Some fixture files carry a byte order mark, which is not part of the message
    out = out.lstrip('\ufeff')

    # Some fixtures use LF or CRLF between segments, the parser expects CR
    out = out.replace('\r\n', '\r')
    out = out.replace('\n', '\r')

    return out

# ################################################################################################################################

def list_messages(dir_path:'str') -> 'anylist':
    """ Returns the full paths of all the .hl7 fixtures in a directory, sorted by name.
    """
    out = []

    for file_name in sorted(os.listdir(dir_path)):
        if file_name.endswith('.hl7'):
            out.append(os.path.join(dir_path, file_name))

    return out

# ################################################################################################################################

def rep(text:'str') -> 'anylist':
    """ Builds one repetition - a list of components, each a list of subcomponents -
    from an ER7-style string like 123^^^MYHOSP&1.2&ISO^MR.
    """
    out = []

    for component in text.split('^'):
        out.append(component.split('&'))

    return out

# ################################################################################################################################

def convert(*segments:'str', config:'str | None'=None) -> 'any_':
    """ Parses ER7 segments into a message and converts it to a typed FHIR bundle.
    """
    from zato.hl7v2 import parse_hl7

    raw = '\r'.join(segments) + '\r'
    msg = parse_hl7(raw, validate=False)

    out = msg.to_fhir(config=config)
    return out

# ################################################################################################################################

def resources_of_type(bundle:'any_', resource_type:'str') -> 'anylist':
    """ Returns the resource dicts of one type from a bundle, in entry order.
    """
    bundle_dict = bundle.to_dict()

    out = []

    for entry in bundle_dict['entry']:
        resource = entry['resource']
        if resource['resourceType'] == resource_type:
            out.append(resource)

    return out

# ################################################################################################################################

def one_resource(bundle:'any_', resource_type:'str') -> 'any_':
    """ Returns the only resource of one type from a bundle, asserting there is exactly one.
    """
    resources = resources_of_type(bundle, resource_type)
    assert len(resources) == 1, f'Expected one {resource_type}, found {len(resources)}'

    out = resources[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def default_config() -> 'FHIRMappingConfig':
    """ The config to_fhir uses when it is called without any.
    """
    out = load_mapping_config(None)
    return out

# ################################################################################################################################
# ################################################################################################################################
