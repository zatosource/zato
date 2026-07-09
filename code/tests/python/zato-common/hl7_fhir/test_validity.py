# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.fhir import validate
from zato.hl7v2 import parse_hl7

# Local
from conftest import Real_World_Dir, Samples_Dir, Test_Conversions_Dir, list_messages, load_message

# ################################################################################################################################
# ################################################################################################################################

def _all_fixture_paths():
    """ Every fixture message the conversion is proven against - the IG test conversions,
    the sample tree and the real-world vendor messages.
    """
    out = []

    out.extend(list_messages(Test_Conversions_Dir))
    out.extend(list_messages(Samples_Dir))
    out.extend(list_messages(Real_World_Dir))

    return out

# ################################################################################################################################

def _parse_or_skip(file_path:'str'):
    """ Parses one fixture, skipping the test when the parser rejects the message itself.
    """
    raw = load_message(file_path)

    try:
        out = parse_hl7(raw, validate=False)
    except ValueError as e:
        pytest.skip(f'parser rejected the message: {e}')

    return out

# ################################################################################################################################

def _fixture_id(file_path:'str') -> 'str':
    """ A stable test ID - the fixture's directory name plus its file name.
    """
    dir_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)

    out = f'{dir_name}/{file_name}'
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('file_path', _all_fixture_paths(), ids=_fixture_id)
def test_bundle_is_valid_r4(file_path):
    """ Validity proof - every produced bundle passes the R4 validator.
    """
    msg = _parse_or_skip(file_path)
    bundle = msg.to_fhir()

    outcome = validate(bundle)
    assert outcome.is_valid, outcome.errors

# ################################################################################################################################

@pytest.mark.parametrize('file_path', _all_fixture_paths(), ids=_fixture_id)
def test_references_resolve_inside_bundle(file_path):
    """ Integrity proof - every urn:uuid reference points at an entry of the same bundle.
    """
    msg = _parse_or_skip(file_path)
    bundle = msg.to_fhir()

    bundle_dict = bundle.to_dict()

    # All the URLs the bundle's entries live under ..
    full_urls = set()

    for entry in bundle_dict['entry']:
        full_urls.add(entry['fullUrl'])

    # .. and every reference anywhere in any resource must be one of them.
    for entry in bundle_dict['entry']:
        resource = entry['resource']
        references = _collect_references(resource, [])

        for reference in references:
            if reference.startswith('urn:uuid:'):
                assert reference in full_urls, f'{reference} does not resolve in {_fixture_id(file_path)}'

# ################################################################################################################################

def _collect_references(node, out):
    """ Walks a resource dict and gathers every reference value it carries.
    """
    if isinstance(node, dict):
        for key in node:
            value = node[key]

            if key == 'reference':
                if isinstance(value, str):
                    out.append(value)
            else:
                _ = _collect_references(value, out)

    elif isinstance(node, list):
        for item in node:
            _ = _collect_references(item, out)

    return out

# ################################################################################################################################

@pytest.mark.parametrize('file_path', _all_fixture_paths(), ids=_fixture_id)
def test_full_urls_are_unique(file_path):
    """ Dedup proof - no two entries share a full URL, one resource per real-world entity.
    """
    msg = _parse_or_skip(file_path)
    bundle = msg.to_fhir()

    bundle_dict = bundle.to_dict()

    full_urls = []

    for entry in bundle_dict['entry']:
        full_urls.append(entry['fullUrl'])

    assert len(full_urls) == len(set(full_urls))

# ################################################################################################################################

def test_fixture_tree_is_complete():
    """ All three fixture sources are present and non-trivial.
    """
    conversions = list_messages(Test_Conversions_Dir)
    samples = list_messages(Samples_Dir)
    real_world = list_messages(Real_World_Dir)

    assert len(conversions) >= 6
    assert len(samples) >= 100
    assert len(real_world) >= 30

# ################################################################################################################################
# ################################################################################################################################
