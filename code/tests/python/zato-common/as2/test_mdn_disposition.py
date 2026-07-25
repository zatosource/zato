# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException, AS2SecurityException, Failure
from zato.common.as2.mdn import disposition_from_exception, format_disposition, is_known_modifier, \
    new_error_disposition, new_failure_disposition, new_processed_disposition, new_warning_disposition, parse_disposition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestDispositionFormatting:
    """ The historic RFC 4130 constructions are what every AS2 implementation accepts,
    so they are the only form ever emitted.
    """

    def test_processed(self) -> 'None':
        disposition = new_processed_disposition()

        formatted = format_disposition(disposition)

        assert formatted == 'automatic-action/MDN-sent-automatically; processed'

# ################################################################################################################################

    def test_processed_error(self) -> 'None':
        disposition = new_error_disposition(AS2Error.Decryption_Failed)

        formatted = format_disposition(disposition)

        assert formatted == 'automatic-action/MDN-sent-automatically; processed/error: decryption-failed'

# ################################################################################################################################

    def test_processed_warning(self) -> 'None':
        disposition = new_warning_disposition('duplicate-document')

        formatted = format_disposition(disposition)

        assert formatted == 'automatic-action/MDN-sent-automatically; processed/warning: duplicate-document'

# ################################################################################################################################

    def test_failed_failure(self) -> 'None':
        disposition = new_failure_disposition(Failure.Unsupported_MIC_Algorithms)

        formatted = format_disposition(disposition)

        assert formatted == 'automatic-action/MDN-sent-automatically; failed/Failure: unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class TestDispositionSelection:
    """ The disposition table - error modifiers ride on processed/error, while failure descriptions,
    reserved for problems with the MDN request itself, ride on failed/Failure.
    """

    @pytest.mark.parametrize('modifier', [
        AS2Error.Integrity_Check_Failed,
        AS2Error.Authentication_Failed,
        AS2Error.Decryption_Failed,
        AS2Error.Decompression_Failed,
        AS2Error.Unexpected_Processing_Error,
    ])
    def test_content_processing_problems_are_errors(self, modifier:'any_') -> 'None':
        exception = AS2SecurityException(modifier, 'Test error detail')

        disposition = disposition_from_exception(exception)

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == modifier

# ################################################################################################################################

    @pytest.mark.parametrize('description', [
        Failure.Unsupported_Format,
        Failure.Unsupported_MIC_Algorithms,
    ])
    def test_mdn_request_problems_are_failures(self, description:'any_') -> 'None':
        exception = AS2ProtocolException(description, 'Test failure detail')

        disposition = disposition_from_exception(exception)

        assert disposition.disposition_type == 'failed'
        assert disposition.modifier_kind == 'failure'
        assert disposition.modifier == description

# ################################################################################################################################
# ################################################################################################################################

class TestDispositionParsing:

    def test_historic_processed(self) -> 'None':
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; processed')

        assert disposition.mode == 'automatic-action/MDN-sent-automatically'
        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == ''
        assert disposition.modifier == ''

# ################################################################################################################################

    def test_historic_error(self) -> 'None':
        value = 'automatic-action/MDN-sent-automatically; processed/error: authentication-failed'

        disposition = parse_disposition(value)

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == 'authentication-failed'

# ################################################################################################################################

    def test_historic_failure(self) -> 'None':
        value = 'automatic-action/MDN-sent-automatically; failed/Failure: unsupported format'

        disposition = parse_disposition(value)

        assert disposition.disposition_type == 'failed'
        assert disposition.modifier_kind == 'failure'
        assert disposition.modifier == 'unsupported format'

# ################################################################################################################################

    def test_capitalized_error_kind_is_accepted(self) -> 'None':
        value = 'automatic-action/MDN-sent-automatically; processed/Error: decryption-failed'

        disposition = parse_disposition(value)

        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == 'decryption-failed'

# ################################################################################################################################

    def test_rfc_8098_bare_modifier_form(self) -> 'None':
        # The RFC 8098 form may carry the bare kind alone, with the details in separate fields.
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; processed/error')

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == ''

# ################################################################################################################################

    def test_manual_action_mode(self) -> 'None':
        disposition = parse_disposition('manual-action/MDN-sent-manually; processed')

        assert disposition.mode == 'manual-action/MDN-sent-manually'
        assert disposition.disposition_type == 'processed'

# ################################################################################################################################

    def test_mode_may_be_absent(self) -> 'None':
        disposition = parse_disposition('processed/error: decryption-failed')

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == 'decryption-failed'

# ################################################################################################################################

    def test_modifier_is_never_split_on_a_comma(self) -> 'None':
        value = 'automatic-action/MDN-sent-automatically; processed/warning: ' + \
            'authentication-failed, processing continued'

        disposition = parse_disposition(value)

        assert disposition.modifier_kind == 'warning'
        assert disposition.modifier == 'authentication-failed, processing continued'

# ################################################################################################################################

    def test_emitted_form_parses_back(self) -> 'None':
        original = new_error_disposition(AS2Error.Integrity_Check_Failed)

        formatted = format_disposition(original)
        parsed = parse_disposition(formatted)

        assert parsed.mode == original.mode
        assert parsed.disposition_type == original.disposition_type
        assert parsed.modifier_kind == original.modifier_kind
        assert parsed.modifier == original.modifier

# ################################################################################################################################
# ################################################################################################################################

class TestKnownModifiers:
    """ The registry modifiers of the AS2 specification modernization draft parse as known values.
    """

    @pytest.mark.parametrize('modifier', [
        'authentication-failed',
        'decompression-failed',
        'decryption-failed',
        'duplicate-filename',
        'illegal-filename',
        'insufficient-message-security',
        'integrity-check-failed',
        'invalid-message-id',
        'unexpected-processing-error',
        'unknown-trading-partner',
        'unknown-trading-relationship',
    ])
    def test_registry_modifiers_are_known(self, modifier:'any_') -> 'None':
        assert is_known_modifier(modifier)

# ################################################################################################################################

    def test_free_text_is_not_a_registry_entry(self) -> 'None':
        assert not is_known_modifier('sender-equals-receiver')

# ################################################################################################################################
# ################################################################################################################################
