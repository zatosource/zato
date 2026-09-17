# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SOAP fault codes an outgoing SOAP connection alerts on - the text a person types parses into the standard
# names and an endpoint's own prefixed ones and refuses anything else, the matching counts sum the named codes
# alone, and the sweep's derivation reads a connection's own codes over the rule's default.

# pytest
import pytest

# Zato
from zato.common.alerting.collectors.common import new_fact
from zato.common.alerting.config_map import Fault_Codes_Default
from zato.common.alerting.fault_codes import apply_fault_codes, count_matching_faults, parse_fault_codes, \
    Fault_Code_Counts_Key, Fault_Count_Key
from zato.common.alerting.seed.rules_connections import soap_rules
from zato.common.audit_log.api import AuditSource
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.models import Rule
    Rule = Rule

# ################################################################################################################################
# ################################################################################################################################

_ruleset_name = 'alerts_soap'
_conn_name = 'crm.soap'

# The standard local names of either SOAP version, as the envelope hands them over
_standard_codes = ['Sender', 'Receiver', 'Client', 'Server', 'VersionMismatch', 'MustUnderstand', 'DataEncodingUnknown']

# ################################################################################################################################

def _load_rule(name:'str') -> 'Rule':
    """ One of the seeded soap rules as a runtime rule.
    """
    documents, errors = parse_data_details(soap_rules, _ruleset_name)
    assert errors == []

    loaded = load_documents(documents)

    out = loaded.manager[f'{_ruleset_name}_{name}']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseFaultCodes:

    def test_the_standard_names_parse_with_whatever_spacing(self) -> 'None':
        assert parse_fault_codes('Receiver, Server, Sender, Client') == ['Receiver', 'Server', 'Sender', 'Client']
        assert parse_fault_codes('Receiver,Server') == ['Receiver', 'Server']
        assert parse_fault_codes('  Receiver ') == ['Receiver']
        assert parse_fault_codes(', '.join(_standard_codes)) == _standard_codes

    def test_an_endpoints_own_prefixed_code_parses(self) -> 'None':
        assert parse_fault_codes('x:Timeout, Receiver') == ['x:Timeout', 'Receiver']
        assert parse_fault_codes('crm-v2:Order.NotFound') == ['crm-v2:Order.NotFound']

    def test_an_entry_is_kept_once_and_case_tells_codes_apart(self) -> 'None':
        assert parse_fault_codes('Receiver, Receiver, receiver') == ['Receiver', 'receiver']

    def test_empty_entries_name_nothing(self) -> 'None':
        assert parse_fault_codes('') == []
        assert parse_fault_codes('Receiver,, Server,') == ['Receiver', 'Server']

    @pytest.mark.parametrize('text', ['500', '5xx', 'Not Found', ':Timeout', 'x:', 'a:b:c', 'Receiver Server', '-Receiver'])
    def test_anything_else_is_refused(self, text:'str') -> 'None':
        with pytest.raises(ValueError) as context:
            _ = parse_fault_codes(text)

        assert text in str(context.value)

# ################################################################################################################################
# ################################################################################################################################

class TestCountMatchingFaults:

    def test_the_counts_are_summed_by_the_named_codes_alone(self) -> 'None':
        fault_counts = {'Receiver': 2, 'Sender': 1, 'x:Timeout': 3}

        matching = count_matching_faults(fault_counts, ['Receiver', 'x:Timeout'])

        assert matching == {'Receiver': 2, 'x:Timeout': 3}
        assert sum(matching.values()) == 5

    def test_nothing_matches_nothing(self) -> 'None':
        assert count_matching_faults({'Sender': 4}, ['Receiver']) == {}
        assert count_matching_faults({}, ['Receiver']) == {}

# ################################################################################################################################
# ################################################################################################################################

class TestApplyFaultCodes:

    def test_the_rules_default_codes_apply_when_the_connection_has_none_of_its_own(self) -> 'None':
        rule = _load_rule('SOAP_Faults')

        fact = new_fact(AuditSource.SOAP_Outgoing, _conn_name)
        fact['fault_counts'] = {'Receiver': 2, 'Sender': 1, 'x:Timeout': 3}

        derived = apply_fault_codes(fact, rule, {})

        # The default is Receiver, Server, Sender and Client - the endpoint's own code is not among them
        assert derived[Fault_Count_Key] == 3
        assert derived[Fault_Code_Counts_Key] == {'Receiver': 2, 'Sender': 1}

        # The fact handed in is left as it was, since every rule reads it
        assert fact[Fault_Count_Key] == 0
        assert fact[Fault_Code_Counts_Key] == {}

    def test_the_connections_own_codes_stand_in_for_the_default(self) -> 'None':
        rule = _load_rule('SOAP_Faults')

        fact = new_fact(AuditSource.SOAP_Outgoing, _conn_name)
        fact['fault_counts'] = {'Receiver': 2, 'Sender': 1, 'x:Timeout': 3}

        derived = apply_fault_codes(fact, rule, {Fault_Codes_Default: 'Receiver, x:Timeout'})

        assert derived[Fault_Count_Key] == 5
        assert derived[Fault_Code_Counts_Key] == {'Receiver': 2, 'x:Timeout': 3}

    def test_a_fact_without_fault_counts_is_handed_back_as_it_is(self) -> 'None':
        rule = _load_rule('SOAP_Faults')
        fact = new_fact(AuditSource.SOAP_Outgoing, _conn_name)

        assert apply_fault_codes(fact, rule, {}) is fact

    def test_a_rule_without_fault_codes_is_not_its_business(self) -> 'None':
        rule = _load_rule('Status_Codes')

        fact = new_fact(AuditSource.SOAP_Outgoing, _conn_name)
        fact['fault_counts'] = {'Receiver': 4}

        assert apply_fault_codes(fact, rule, {}) is fact

# ################################################################################################################################
# ################################################################################################################################
