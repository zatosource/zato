# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import Kind_Markup, Mode_Reject, SafeguardConfig, SafeguardResult
from zato.common.util.safeguards.markup import sanitize_markup

# ################################################################################################################################
# ################################################################################################################################

def _new_result() -> 'SafeguardResult':
    """ Returns a fresh result for direct stage calls.
    """
    out = SafeguardResult()
    out.pii_removed = {}
    out.signals = {}

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSanitizeMarkup:

    def test_script_elements_are_removed_with_content(self) -> 'None':

        result = _new_result()
        value = {'body': 'Before <script type="text/javascript">alert("Attack")</script> after'}

        cleaned = sanitize_markup(value, result)

        assert cleaned == {'body': 'Before  after'}
        assert result.markup_items_removed == 1

    def test_style_elements_are_removed_with_content(self) -> 'None':

        result = _new_result()
        value = {'body': 'Before <style>body { display: none }</style> after'}

        cleaned = sanitize_markup(value, result)

        assert cleaned == {'body': 'Before  after'}
        assert result.markup_items_removed == 1

    def test_event_handler_attributes_are_removed(self) -> 'None':

        result = _new_result()
        value = {'body': '<img src="logo.png" onerror="alert(1)" alt="Logo">'}

        cleaned = sanitize_markup(value, result)

        assert cleaned == {'body': '<img src="logo.png" alt="Logo">'}
        assert result.markup_items_removed == 1

    def test_javascript_uris_are_removed_from_attributes(self) -> 'None':

        result = _new_result()
        value = {'body': '<a href="javascript:alert(1)">Click here</a>'}

        cleaned = sanitize_markup(value, result)

        assert cleaned == {'body': '<a>Click here</a>'}
        assert result.markup_items_removed == 1

    def test_javascript_uris_are_removed_from_markdown_links(self) -> 'None':

        result = _new_result()
        value = {'body': 'See [the details](javascript:alert(1)) for more'}

        cleaned = sanitize_markup(value, result)

        assert cleaned == {'body': 'See [the details]() for more'}
        assert result.markup_items_removed == 1

    def test_benign_markup_is_untouched(self) -> 'None':

        result = _new_result()
        text = 'A <b>bold</b> claim with [a link](https://example.com/docs) inside'
        value = {'body': text}

        cleaned = sanitize_markup(value, result)

        assert cleaned == {'body': text}
        assert result.markup_items_removed == 0
        assert result.signals == {}

    def test_spliced_markup_is_removed_too(self) -> 'None':

        # Removing one attribute splices another one together - the rules run until nothing more matches.
        result = _new_result()
        value = {'body': '<img on onbar="x"foo="alert(1)">'}

        cleaned = sanitize_markup(value, result)

        assert 'onfoo' not in cleaned['body']
        assert result.markup_items_removed == 2

    def test_findings_are_signalled(self) -> 'None':

        result = _new_result()
        value = {'first': '<script>a()</script>', 'second': '<a href="javascript:b()">x</a> <i onclick=c>y</i>'}

        _ = sanitize_markup(value, result)

        assert result.markup_items_removed == 3

        signal = result.signals[Kind_Markup]

        assert signal.count == 3
        assert signal.paths == ['$.first', '$.second']

    def test_reject_mode_stops_the_pipeline(self) -> 'None':

        config = SafeguardConfig()
        config.sanitize_markup = True
        config.markup_mode = Mode_Reject
        config.pii_enabled = True
        config.pii_lands = ['intl']
        config.pii_detectors = []
        config.pii_exclude = []

        value = {'body': '<script>steal()</script>', 'payment': 'IBAN DE89370400440532013000'}

        result = apply_safeguards(value, config)

        assert result.was_rejected is True
        assert result.reject_kind == Kind_Markup

        # PII removal never ran - the IBAN is still in the value.
        assert result.pii_removed == {}
        assert result.value['payment'] == 'IBAN DE89370400440532013000'

# ################################################################################################################################
# ################################################################################################################################
