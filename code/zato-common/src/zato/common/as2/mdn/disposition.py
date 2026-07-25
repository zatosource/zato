# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The Disposition field of an MDN - the dispositions this implementation emits, how each of them is
written onto the wire, and how one that arrived is read back.
"""

# Zato
from zato.common.as2.common import AS2Error, Failure
from zato.common.as2.mdn.common import Disposition, DispositionType, ModifierKind

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.common import AS2ProtocolException
    AS2ProtocolException = AS2ProtocolException

# ################################################################################################################################
# ################################################################################################################################

# Failure descriptions accompany the "failed" disposition type - everything else is an error modifier.
_failure_descriptions = {
    Failure.Unsupported_Format,
    Failure.Unsupported_MIC_Algorithms,
}

# Every disposition modifier this implementation recognizes as a known value on input,
# including the registry values of the AS2 specification modernization draft.
_known_modifiers = {
    AS2Error.Authentication_Failed,
    AS2Error.Decompression_Failed,
    AS2Error.Decryption_Failed,
    AS2Error.Duplicate_Filename,
    AS2Error.Illegal_Filename,
    AS2Error.Insufficient_Message_Security,
    AS2Error.Integrity_Check_Failed,
    AS2Error.Invalid_Message_ID,
    AS2Error.Unexpected_Processing_Error,
    AS2Error.Unknown_Trading_Partner,
    AS2Error.Unknown_Trading_Relationship,
}

# ################################################################################################################################
# ################################################################################################################################

def new_processed_disposition() -> 'Disposition':
    """ Returns the disposition of a message that was processed cleanly.
    """

    # Our response to produce
    out = Disposition()

    return out

# ################################################################################################################################

def new_error_disposition(modifier:'str') -> 'Disposition':
    """ Returns a processed/error disposition with the given modifier.
    """

    # Our response to produce
    out = Disposition()

    out.modifier_kind = ModifierKind.Error
    out.modifier = modifier

    return out

# ################################################################################################################################

def new_warning_disposition(modifier:'str') -> 'Disposition':
    """ Returns a processed/warning disposition with the given modifier.
    """

    # Our response to produce
    out = Disposition()

    out.modifier_kind = ModifierKind.Warning
    out.modifier = modifier

    return out

# ################################################################################################################################

def new_failure_disposition(description:'str') -> 'Disposition':
    """ Returns a failed/Failure disposition - reserved for problems with the MDN request itself,
    such as an unsupported format or unsupported MIC algorithms, never for content processing.
    """

    # Our response to produce
    out = Disposition()

    out.disposition_type = DispositionType.Failed
    out.modifier_kind = ModifierKind.Failure
    out.modifier = description

    return out

# ################################################################################################################################

def disposition_from_exception(exception:'AS2ProtocolException') -> 'Disposition':
    """ Maps a protocol exception to its disposition - failure descriptions become failed/Failure,
    everything else is a processed/error with the exception's modifier.
    """
    if exception.modifier in _failure_descriptions:
        out = new_failure_disposition(exception.modifier)
    else:
        out = new_error_disposition(exception.modifier)

    return out

# ################################################################################################################################
# ################################################################################################################################

def describe_disposition(disposition:'str', modifier_kind:'str', modifier:'str') -> 'str':
    """ Builds the human-readable outcome of a parsed MDN disposition,
    e.g. `processed` or `processed/error: unknown-trading-partner`.
    """
    if modifier_kind:
        out = f'{disposition}/{modifier_kind}: {modifier}'
    else:
        out = disposition

    return out

# ################################################################################################################################

def format_disposition(disposition:'Disposition') -> 'str':
    """ Emits a Disposition field value in the historic RFC 4130 construction -
    the form every AS2 implementation accepts.
    """
    base = f'{disposition.mode}; {disposition.disposition_type}'

    # A clean disposition has no modifier at all ..
    if not disposition.modifier_kind:
        out = base

    # .. failure descriptions keep the capitalized spelling of the RFC 4130 examples ..
    elif disposition.modifier_kind == ModifierKind.Failure:
        out = f'{base}/Failure: {disposition.modifier}'

    # .. errors and warnings ride lowercase after the disposition type.
    else:
        out = f'{base}/{disposition.modifier_kind}: {disposition.modifier}'

    return out

# ################################################################################################################################

def parse_disposition(value:'str') -> 'Disposition':
    """ Parses a Disposition field value, accepting the historic RFC 4130 constructions
    and the RFC 3798 and RFC 8098 forms alike. The modifier is never split on a comma.
    """

    # Our response to produce
    out = Disposition()

    # The mode rides before the semicolon - lenient parsing accepts its absence.
    if ';' in value:
        mode, _, rest = value.partition(';')
        out.mode = mode.strip()
    else:
        rest = value

    rest = rest.strip()

    # The modifier follows the disposition type after a slash, when there is one.
    disposition_type, _, modifier_part = rest.partition('/')
    disposition_type = disposition_type.strip()
    out.disposition_type = disposition_type.lower()

    modifier_part = modifier_part.strip()

    if modifier_part:

        # The historic construction spells out the kind and its text, e.g. error: decryption-failed ..
        if ':' in modifier_part:
            kind, _, text = modifier_part.partition(':')
            kind = kind.strip()
            out.modifier_kind = kind.lower()
            out.modifier = text.strip()

        # .. the RFC 8098 form may carry the bare kind alone, with the details in separate fields.
        else:
            out.modifier_kind = modifier_part.lower()

    return out

# ################################################################################################################################

def is_known_modifier(value:'str') -> 'bool':
    """ Tells whether a modifier value is one of the registry values this implementation recognizes.
    """
    out = value in _known_modifiers
    return out

# ################################################################################################################################
# ################################################################################################################################
