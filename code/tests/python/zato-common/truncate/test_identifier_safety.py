# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import scan, scan_json

# Zato
from zato.common.typing_ import anylist, stranydict
from zato.common.util.truncate.api import truncate_json
from zato.common.util.truncate.common import Min_Usable_Cap
from zato.common.util.truncate.measure import get_size, serialize

# ################################################################################################################################
# ################################################################################################################################

# Identifiers seeded into the fixtures - compact IBANs, spaced IBANs and emails from several countries.
_compact_ibans = [
    'DE89370400440532013000',
    'GB29NWBK60161331926819',
    'FR1420041010050500013M02606',
    'NL91ABNA0417164300',
]

_spaced_ibans = [
    'ES91 2100 0418 4502 0005 1332',
    'PL61 1090 1014 0000 0712 1981 2874',
    'IT60 X054 2811 1010 0000 0123 456',
]

_emails = [
    'settlements-desk@example.com',
    'treasury.reports@example.co.uk',
    'payment-operations@example.de',
]

_all_identifiers = _compact_ibans + _spaced_ibans + _emails

# The detectors whose matches the assertions below reason about.
_watched_detectors = {'intl_iban', 'intl_email'}

# Filler prose deliberately free of digits, so trailing-token trimming decisions are driven
# by the identifiers themselves and not by the surrounding text.
_filler = 'the transfer settled without incident and the ledger entries reconciled cleanly across regions '

# How many caps the sweep tries per fixture - a prime step so the cut points land all over the document.
_cap_step = 1013

# ################################################################################################################################
# ################################################################################################################################

def _build_document() -> 'stranydict':
    """ Builds a document that embeds every identifier in long prose, in array records and in nested sections,
    so cuts of every kind land near identifiers during the cap sweep.
    """

    # Long prose with identifiers sprinkled at the start, the middle and near the end.
    description_parts = [
        'payments to ' + _compact_ibans[0] + ' started failing ',
        _filler * 20,
        'the retry went to ' + _spaced_ibans[0] + ' as instructed ',
        _filler * 20,
        'escalations go to ' + _emails[0] + ' from now on ',
        _filler * 20,
        'the final account checked was ' + _compact_ibans[1] + ' late in the day',
    ]
    description = ''.join(description_parts)

    # Records that array truncation removes whole.
    records = []
    for index in range(60):
        identifier_index = index % len(_all_identifiers)
        record = {
            'position': index,
            'account': _all_identifiers[identifier_index],
            'contact': _emails[index % len(_emails)],
            'summary': _filler,
        }
        records.append(record)

    # Nested prose with identifiers close together, so string cuts land between and inside identifier regions.
    audit_trail = (
        'reviewed by ' + _emails[1] + ' with counterparty accounts ' + _spaced_ibans[1] + ' and ' +
        _compact_ibans[2] + ' then countersigned. ' + _filler * 15 +
        'the backup instruction named ' + _spaced_ibans[2] + ' with a copy to ' + _emails[2] + '. ' +
        _filler * 15 +
        'one more account appears at the very end which is ' + _compact_ibans[3]
    )

    out = {
        'status': 'reconciled',
        'description': description,
        'records': records,
        'audit': {'trail': audit_trail},
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _assert_no_partial_identifiers(serialized:'str') -> 'None':
    """ Asserts that every seeded identifier is either fully present or fully absent - no fragment
    of a removed identifier is ever left behind.
    """
    for identifier in _all_identifiers:
        if identifier not in serialized:
            half = len(identifier) // 2
            fragment = identifier[:half]
            assert fragment not in serialized, f'Fragment {fragment!r} of removed identifier {identifier!r} survives'

# ################################################################################################################################

def _assert_all_matches_valid(matches:'anylist', context:'str') -> 'None':
    """ Asserts that every watched detector match carries a valid checksum or shape - a match with
    a broken checksum would mean an identifier was damaged rather than removed.
    """
    for match in matches:
        if match.name in _watched_detectors:
            assert match.valid is True, f'Invalid {match.name} match {match.value!r} in {context}'

# ################################################################################################################################
# ################################################################################################################################

class TestIdentifierSafety:

    def test_fixture_is_sound_before_truncation(self) -> 'None':

        # Every seeded identifier must be detected, valid, in the untruncated document first -
        # otherwise the sweep below would prove nothing.
        document = _build_document()
        serialized = serialize(document)

        matches = scan(serialized)
        _assert_all_matches_valid(matches, 'the untruncated document')

        matched_values = set()
        for match in matches:
            if match.name in _watched_detectors:
                matched_values.add(match.value.replace(' ', ''))

        for identifier in _all_identifiers:
            normalized = identifier.replace(' ', '')
            assert normalized in matched_values, f'Identifier {identifier!r} not detected in the fixture'

    def test_cap_sweep_never_halves_an_identifier(self) -> 'None':

        document = _build_document()
        size_before = get_size(document)

        assert size_before > Min_Usable_Cap

        cap = Min_Usable_Cap

        while cap < size_before:

            result = truncate_json(document, cap)
            serialized = serialize(result.value)

            # Whatever survives parses back and carries only intact identifiers.
            text_matches = scan(serialized)
            _assert_all_matches_valid(text_matches, f'the serialized result at cap {cap}')

            structure_matches = scan_json(result.value)
            _assert_all_matches_valid(structure_matches, f'the structured result at cap {cap}')

            # And whatever was removed left no fragment behind.
            _assert_no_partial_identifiers(serialized)

            cap += _cap_step

# ################################################################################################################################
# ################################################################################################################################
