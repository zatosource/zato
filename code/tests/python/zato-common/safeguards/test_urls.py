# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import strlist
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import Kind_Url, SafeguardConfig, SafeguardResult, Url_Marker, Url_Mode_Neutralize, \
    Url_Mode_Reject
from zato.common.util.safeguards.urls import apply_url_policy

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

def _new_config(allow_list:'strlist') -> 'SafeguardConfig':
    """ Returns a config with the URL policy enabled and the given allow list.
    """
    out = SafeguardConfig()
    out.url_policy_enabled = True
    out.url_allow_list = allow_list

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestApplyUrlPolicy:

    def test_allowed_hosts_pass_untouched(self) -> 'None':

        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'link': 'See https://zato.io/docs for details'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': 'See https://zato.io/docs for details'}
        assert result.urls_flagged == 0
        assert result.signals == {}

    def test_subdomains_of_allowed_hosts_pass(self) -> 'None':

        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'link': 'See https://docs.zato.io/start for details'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': 'See https://docs.zato.io/start for details'}
        assert result.urls_flagged == 0

    def test_lookalike_hosts_do_not_pass(self) -> 'None':

        # A host that merely ends with the allowed name, without a dot boundary, is not a subdomain.
        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'link': 'See https://notzato.io/start for details'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': f'See {Url_Marker} for details'}
        assert result.urls_flagged == 1

    def test_remove_mode_replaces_with_marker(self) -> 'None':

        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'link': 'Download from https://example.com/payload now'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': f'Download from {Url_Marker} now'}
        assert result.urls_flagged == 1

    def test_neutralize_mode_breaks_the_url_up(self) -> 'None':

        result = _new_result()
        config = _new_config(['zato.io'])
        config.url_mode = Url_Mode_Neutralize
        value = {'link': 'Download from https://example.com/payload now'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': 'Download from hxxps://example[.]com/payload now'}
        assert result.urls_flagged == 1

    def test_reject_mode_keeps_urls_in_place(self) -> 'None':

        # Reject mode refuses the whole document, so individual URLs stay as they are - still counted though.
        result = _new_result()
        config = _new_config(['zato.io'])
        config.url_mode = Url_Mode_Reject
        value = {'link': 'Download from https://example.com/payload now'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': 'Download from https://example.com/payload now'}
        assert result.urls_flagged == 1

    def test_empty_allow_list_flags_everything(self) -> 'None':

        result = _new_result()
        config = _new_config([])
        value = {'link': 'See https://zato.io/docs for details'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': f'See {Url_Marker} for details'}
        assert result.urls_flagged == 1

    def test_host_with_port_is_matched(self) -> 'None':

        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'link': 'The service runs at https://api.zato.io:8443/status today'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': 'The service runs at https://api.zato.io:8443/status today'}
        assert result.urls_flagged == 0

    def test_bare_host_url_is_matched(self) -> 'None':

        # A URL that is nothing but a scheme and a host still has its host extracted.
        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'link': 'https://example.com'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': Url_Marker}
        assert result.urls_flagged == 1

    def test_allow_list_matching_is_case_insensitive(self) -> 'None':

        result = _new_result()
        config = _new_config(['Zato.IO'])
        value = {'link': 'See HTTPS://ZATO.io/Docs for details'}

        cleaned = apply_url_policy(value, result, config)

        assert cleaned == {'link': 'See HTTPS://ZATO.io/Docs for details'}
        assert result.urls_flagged == 0

    def test_multiple_urls_in_one_string(self) -> 'None':

        result = _new_result()
        config = _new_config(['zato.io'])
        value = {'links': 'First https://example.com/one then https://zato.io/two then https://example.com/three'}

        cleaned = apply_url_policy(value, result, config)

        expected = f'First {Url_Marker} then https://zato.io/two then {Url_Marker}'

        assert cleaned == {'links': expected}
        assert result.urls_flagged == 2

        # Both findings share one path, so the sample holds it once while the count says two.
        signal = result.signals[Kind_Url]

        assert signal.count == 2
        assert signal.paths == ['$.links']

    def test_reject_mode_stops_the_pipeline(self) -> 'None':

        config = SafeguardConfig()
        config.url_policy_enabled = True
        config.url_allow_list = ['zato.io']
        config.url_mode = Url_Mode_Reject
        config.pii_enabled = True
        config.pii_lands = ['intl']
        config.pii_detectors = []
        config.pii_exclude = []

        value = {'link': 'Download from https://example.com/payload now', 'payment': 'IBAN DE89370400440532013000'}

        result = apply_safeguards(value, config)

        assert result.was_rejected is True
        assert result.reject_kind == Kind_Url

        # PII removal never ran - the IBAN is still in the value.
        assert result.pii_removed == {}
        assert result.value['payment'] == 'IBAN DE89370400440532013000'

# ################################################################################################################################
# ################################################################################################################################
