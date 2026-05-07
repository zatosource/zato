# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The standard HL7 v2 encoding characters
_Standard_Encoding_Characters = '^~\\&'

# Minimum number of encoding characters in a well-formed MSH-2
_Minimum_Encoding_Characters_Length = 4

# MSH field separator position in MSH|...|
_MSH_Prefix = 'MSH|'

# Encoding map from MSH-18 values to Python codec names
_encoding_map:'dict[str, str]' = {
    '':          'utf-8',
    'ASCII':     'ascii',
    'UNICODE':   'utf-8',
    'UTF-8':     'utf-8',
    '8859/1':    'iso-8859-1',
    'ISO IR6':   'ascii',
    'ISO IR100': 'iso-8859-1',
    'ISO IR101': 'iso-8859-2',
    'ISO IR144': 'iso-8859-5',
    'ISO IR127': 'iso-8859-6',
    'ISO IR126': 'iso-8859-7',
}

# ################################################################################################################################
# ################################################################################################################################

def normalize_line_endings(data:'str') -> 'str':
    """ Converts CRLF and LF line endings to CR (the HL7 segment separator).
    CRLF must be replaced first so that the LF inside it does not get replaced independently.
    """

    # Replace CRLF first ..
    out = data.replace('\r\n', '\r')

    # .. then any remaining bare LF.
    out = out.replace('\n', '\r')

    return out

# ################################################################################################################################
# ################################################################################################################################

def repair_truncated_msh(data:'str') -> 'str':
    """ Repairs messages with truncated or prefixed MSH segment.
    Handles 'SH|...' (missing leading M) and junk before 'MSH|' (e.g. 'ORU_R01|MSH|...').
    """

    # Check for the 'SH|' prefix (missing M) ..
    if data.startswith('SH|'):
        out = 'M' + data
        logger.warning('Repaired truncated MSH: prepended M to SH|')
        return out

    # Check for junk before the first 'MSH|' ..
    msh_position = data.find(_MSH_Prefix)

    if msh_position > 0:
        stripped_prefix = data[:msh_position]
        logger.warning('Stripped %d bytes before MSH: %r', msh_position, stripped_prefix)

        out = data[msh_position:]
        return out

    out = data
    return out

# ################################################################################################################################
# ################################################################################################################################

def split_concatenated_messages(data:'str') -> 'list[str]':
    """ Splits a payload that contains multiple HL7 messages concatenated without batch wrapping.
    Returns a list of individual messages. If only one MSH is found, returns a single-element list.
    """

    # Split on the MSH prefix ..
    parts = data.split(_MSH_Prefix)

    # .. the first element is whatever was before the first MSH (usually empty) ..
    messages:'list[str]' = []

    for part in parts:
        if not part:
            continue
        message = _MSH_Prefix + part
        messages.append(message)

    if len(messages) > 1:
        logger.warning('Split %d concatenated messages from a single MLLP frame', len(messages))

    return messages

# ################################################################################################################################
# ################################################################################################################################

def force_standard_delimiters(data:'str') -> 'str':
    """ Rewrites non-standard MSH-2 encoding characters to the standard ^~\\&.
    Also pads short MSH-2 (fewer than 4 chars) to the full standard set.
    """

    # MSH-2 starts at position 4 (after 'MSH|') and extends until the next '|' ..
    if not data.startswith(_MSH_Prefix):
        return data

    after_msh_pipe = data[4:]
    next_pipe = after_msh_pipe.find('|')

    if next_pipe == -1:
        return data

    original_encoding_characters = after_msh_pipe[:next_pipe]
    rest_of_message = after_msh_pipe[next_pipe:]

    # .. if already standard, nothing to do ..
    if original_encoding_characters == _Standard_Encoding_Characters:
        out = data
        return out

    # .. pad short encoding characters ..
    if len(original_encoding_characters) < _Minimum_Encoding_Characters_Length:
        logger.warning(
            'MSH-2 has only %d encoding characters (%r), padding to standard',
            len(original_encoding_characters),
            original_encoding_characters,
        )
        out = _MSH_Prefix + _Standard_Encoding_Characters + rest_of_message
        return out

    # .. rewrite non-standard delimiters ..
    logger.warning(
        'Rewriting non-standard MSH-2 encoding characters %r to %r',
        original_encoding_characters,
        _Standard_Encoding_Characters,
    )

    # Build a translation table from the original to the standard delimiters
    old_component_separator    = original_encoding_characters[0]
    old_repetition_separator   = original_encoding_characters[1]
    old_escape_character       = original_encoding_characters[2]
    old_subcomponent_separator = original_encoding_characters[3]

    new_component_separator    = _Standard_Encoding_Characters[0]
    new_repetition_separator   = _Standard_Encoding_Characters[1]
    new_escape_character       = _Standard_Encoding_Characters[2]
    new_subcomponent_separator = _Standard_Encoding_Characters[3]

    translation_table = str.maketrans(
        old_component_separator + old_repetition_separator + old_escape_character + old_subcomponent_separator,
        new_component_separator + new_repetition_separator + new_escape_character + new_subcomponent_separator,
    )

    translated_rest = rest_of_message.translate(translation_table)

    out = _MSH_Prefix + _Standard_Encoding_Characters + translated_rest
    return out

# ################################################################################################################################
# ################################################################################################################################

def decode_with_msh18(raw_bytes:'bytes', default_encoding:'str' = 'utf-8') -> 'str':
    """ Decodes raw bytes into a string using the encoding specified in MSH-18,
    or the default encoding if MSH-18 is empty or not recognized.
    """

    # First, do a preliminary ASCII decode of just the MSH line to read MSH-18 ..
    preliminary = raw_bytes.decode('ascii', errors='replace')

    first_cr = preliminary.find('\r')

    if first_cr == -1:
        msh_line = preliminary
    else:
        msh_line = preliminary[:first_cr]

    # .. extract MSH-18 (character set).
    # When splitting MSH on '|', MSH-1 is the separator itself so
    # MSH-2 lands at index 1, MSH-3 at index 2, and MSH-N at index N-1.
    # MSH-18 is therefore at index 17.
    fields = msh_line.split('|')

    _msh18_split_index = 17
    msh18_value = ''

    if len(fields) > _msh18_split_index:
        msh18_value = fields[_msh18_split_index].strip()

    # .. look up the encoding ..
    encoding = _encoding_map.get(msh18_value, '')

    if not encoding:
        encoding = default_encoding

    # .. decode the full message with the resolved encoding.
    out = raw_bytes.decode(encoding, errors='replace')
    return out

# ################################################################################################################################
# ################################################################################################################################

def preprocess_message(
    raw_bytes:'bytes',
    should_normalize_line_endings:'bool' = True,
    should_repair_truncated_msh:'bool' = True,
    should_split_concatenated_messages:'bool' = True,
    should_force_standard_delimiters:'bool' = True,
    should_use_msh18_encoding:'bool' = True,
    default_character_encoding:'str' = 'utf-8',
    ) -> 'list[str]':
    """ Runs the full pre-processing pipeline on raw MLLP payload bytes.
    Returns a list of cleaned ER7 strings (one per message, usually just one).
    """

    # Decode the raw bytes to a string ..
    if should_use_msh18_encoding:
        data = decode_with_msh18(raw_bytes, default_character_encoding)
    else:
        data = raw_bytes.decode(default_character_encoding, errors='replace')

    # .. normalize line endings ..
    if should_normalize_line_endings:
        data = normalize_line_endings(data)

    # .. repair truncated MSH ..
    if should_repair_truncated_msh:
        data = repair_truncated_msh(data)

    # .. split concatenated messages ..
    if should_split_concatenated_messages:
        messages = split_concatenated_messages(data)
    else:
        messages = [data]

    # .. force standard delimiters on each message.
    if should_force_standard_delimiters:
        normalized_messages:'list[str]' = []

        for message in messages:
            normalized_message = force_standard_delimiters(message)
            normalized_messages.append(normalized_message)

        messages = normalized_messages

    return messages

# ################################################################################################################################
# ################################################################################################################################
