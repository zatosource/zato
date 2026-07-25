# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.ingestion import Outcome
from zato.common.rule_engine.invocation import flatten_for_validation, InvocationStatus, is_ruleset_allowed, \
    parse_ruleset_path
from zato.common.rule_engine.sql.constants import Definition_Type_Vocabulary
from zato.common.rule_engine.vocabulary import ErrorCode

# Local
from invocation_test_data import author, create_ruleset, new_invoker, publish, rules_text_dotted, vocabulary_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

def test_parse_ruleset_path_bare_name_runs_live() -> 'None':
    """ A bare name has no pinned version and no error.
    """
    parsed = parse_ruleset_path('payments.discounts')

    assert parsed.name == 'payments.discounts'
    assert parsed.version is None
    assert parsed.error is None

# ################################################################################################################################

def test_parse_ruleset_path_pins_a_version() -> 'None':
    """ The /versions/ segment pins one numeric version.
    """
    parsed = parse_ruleset_path('payments.discounts/versions/3')

    assert parsed.name == 'payments.discounts'
    assert parsed.version == 3
    assert parsed.error is None

# ################################################################################################################################

def test_parse_ruleset_path_rejects_bad_versions_and_paths() -> 'None':
    """ Non-numeric versions, version zero and extra path segments are all readable errors.
    """
    not_a_number = parse_ruleset_path('payments.discounts/versions/latest')
    assert not_a_number.error is not None
    assert 'latest' in not_a_number.error

    version_zero = parse_ruleset_path('payments.discounts/versions/0')
    assert version_zero.error is not None

    extra_segments = parse_ruleset_path('payments.discounts/history')
    assert extra_segments.error is not None

    nested_segments = parse_ruleset_path('payments.discounts/versions/3/audit')
    assert nested_segments.error is not None

# ################################################################################################################################

def test_is_ruleset_allowed_patterns() -> 'None':
    """ Exact grants, subtree grants and the match-all grant behave as documented.
    """
    # An exact grant matches only its own name ..
    assert is_ruleset_allowed('payments.discounts', ['payments.discounts'])
    assert not is_ruleset_allowed('payments.rates', ['payments.discounts'])

    # .. a subtree grant matches everything below its prefix but not the prefix itself ..
    assert is_ruleset_allowed('payments.discounts', ['payments.*'])
    assert is_ruleset_allowed('payments.eu.discounts', ['payments.*'])
    assert not is_ruleset_allowed('payments', ['payments.*'])
    assert not is_ruleset_allowed('pricing.default', ['payments.*'])

    # .. a lone star matches everything ..
    assert is_ruleset_allowed('pricing.default', ['*'])

    # .. and without grants nothing is allowed.
    assert not is_ruleset_allowed('payments.discounts', [])

# ################################################################################################################################

def test_flatten_for_validation() -> 'None':
    """ Nested caller input flattens into the dotted paths a vocabulary speaks, leaving flat keys alone.
    """
    data = {
        'channel': 'web',
        'customer': {'creditScore': 720, 'address': {'city': 'Prague'}},
    }
    flat = flatten_for_validation(data)

    expected = {
        'channel': 'web',
        'customer.creditScore': 720,
        'customer.address.city': 'Prague',
    }
    assert flat == expected

# ################################################################################################################################

def test_live_invocation_lands_with_caller(backend:'RuleSQLBackend') -> 'None':
    """ Invoking a published ruleset runs its live version and logs the caller with the decision.
    """
    definition = create_ruleset(backend)
    publish(backend, definition.id)

    invoker = new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('payments.discounts', {'credit_score': 720}, caller='crm.prod')

    # The invocation completed and reports what ran ..
    assert result.status == InvocationStatus.OK
    assert result.ruleset == 'payments.discounts'
    assert result.version == 1

    # .. the decision names its outcome and outputs ..
    decision = result.decision
    assert decision is not None
    assert decision['outcome'] == Outcome.Matched
    assert decision['actual'] == {'rate': 2.9, 'approved': True}

    # .. and the stored row carries the calling system's name.
    stored = backend.decisions.get(decision['decision_id'])
    assert stored.caller == 'crm.prod'
    assert stored.rules_version == 1

# ################################################################################################################################

def test_unknown_ruleset_is_not_available(backend:'RuleSQLBackend') -> 'None':
    """ A name that maps to nothing is reported as not available.
    """
    invoker = new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('pricing.default', {'credit_score': 720})

    assert result.status == InvocationStatus.Unknown_Ruleset
    assert 'pricing.default' in result.message
    assert result.decision is None

# ################################################################################################################################

def test_unpublished_ruleset_has_no_live_version(backend:'RuleSQLBackend') -> 'None':
    """ A ruleset that was never published has nothing to run.
    """
    _ = create_ruleset(backend)

    invoker = new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('payments.discounts', {'credit_score': 720})

    assert result.status == InvocationStatus.No_Live_Version
    assert 'payments.discounts' in result.message

# ################################################################################################################################

def test_ambiguous_name_is_refused(backend:'RuleSQLBackend') -> 'None':
    """ A name shared by rulesets under different parents cannot be invoked by name.
    """
    first = create_ruleset(backend)
    _ = create_ruleset(backend, parent_id=first.id)

    invoker = new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('payments.discounts', {'credit_score': 720})

    assert result.status == InvocationStatus.Ambiguous_Name
    assert 'payments.discounts' in result.message

# ################################################################################################################################

def test_vocabulary_validates_input_at_the_boundary(backend:'RuleSQLBackend') -> 'None':
    """ A ruleset bound to a vocabulary rejects invalid input in domain terms, before any rule runs.
    """
    vocabulary = backend.definitions.create(
        name='Loan approval',
        object_type=Definition_Type_Vocabulary,
        document=vocabulary_document(),
        author=author,
        comment='Create the vocabulary',
    )

    definition = create_ruleset(backend, text=rules_text_dotted, vocabulary_id=vocabulary.id)
    publish(backend, definition.id)

    invoker = new_invoker(backend)

    with invoker.writer:

        # A score outside the vocabulary's range never reaches the rules ..
        invalid = invoker.invoke('payments.discounts', {'customer': {'creditScore': 12000}})
        assert invalid.status == InvocationStatus.Invalid_Input
        assert invalid.decision is None

        codes = []
        for error in invalid.errors:
            codes.append(error['code'])

        assert ErrorCode.Out_Of_Range in codes

        # .. while valid input evaluates normally.
        valid = invoker.invoke('payments.discounts', {'customer': {'creditScore': 720}})
        assert valid.status == InvocationStatus.OK

        valid_decision = valid.decision
        assert valid_decision is not None
        assert valid_decision['outcome'] == Outcome.Matched
        assert valid_decision['actual'] == {'loan.rate': 2.9}

# ################################################################################################################################

def test_evaluation_error_is_a_logged_decision(backend:'RuleSQLBackend') -> 'None':
    """ Without a vocabulary, an input the rules cannot evaluate lands as an error decision.
    """
    definition = create_ruleset(backend)
    publish(backend, definition.id)

    invoker = new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('payments.discounts', {'amount': 50}, caller='crm.prod')

    # The evaluation completed as an error decision ..
    assert result.status == InvocationStatus.OK

    decision = result.decision
    assert decision is not None
    assert decision['outcome'] == Outcome.Error
    assert 'credit_score' in decision['error']

    # .. and the log holds it under the same id, caller included.
    stored = backend.decisions.get(decision['decision_id'])
    assert stored.is_error is True
    assert stored.caller == 'crm.prod'

# ################################################################################################################################
# ################################################################################################################################
