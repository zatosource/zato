# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.changes import Change_Definition_Archived, Change_Definition_Created, \
    Change_Version_Created, Change_Version_Published, Change_Version_Restored
from zato.common.rule_engine.ingestion import Outcome
from zato.common.rule_engine.invocation import flatten_for_validation, InvocationStatus, is_ruleset_allowed, \
    parse_ruleset_path, RulesetInvoker, Vocabulary_Key
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key
from zato.common.rule_engine.vocabulary import ErrorCode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'

# One rule that fires on good scores - the first published version in every test.
_rules_text = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 700
then
    rate = 2.9
    approved = true
"""

# The same rule with a lower bar - the second version in the republish tests.
_rules_text_lower_bar = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    credit_score is at least 640
then
    rate = 2.9
    approved = true
"""

# Dotted terms match the vocabulary's entity.attribute paths - this text backs the validation tests.
_rules_text_dotted = """
rule
    Preferential_rate
docs
    Better rates for our best customers.
when
    customer.creditScore is at least 700
then
    loan.rate = 2.9
"""

# ################################################################################################################################
# ################################################################################################################################

def _documents(text:'str', ruleset_name:'str'='payments') -> 'anydict':
    """ Parses rules text into canonical documents, loud on any parse error.
    """
    documents, errors = parse_data_details(text, ruleset_name)
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def _vocabulary_document() -> 'anydict':
    """ A small loan vocabulary covering a number range and outputs.
    """
    out = {
        'name': 'Loan approval',
        'entities': [
            {'name': 'customer', 'attributes': [
                {'name': 'creditScore', 'type': 'number range', 'domain': {'low': 300, 'high': 850},
                 'phrase': "the customer's credit score", 'status': ''},
            ]},
            {'name': 'loan', 'attributes': [
                {'name': 'rate', 'type': 'number', 'phrase': 'the interest rate', 'status': ''},
            ]},
        ],
    }

    return out

# ################################################################################################################################

def _create_ruleset(
    backend:'RuleSQLBackend',
    name:'str' = 'payments.discounts',
    text:'str' = _rules_text,
    parent_id:'int | None' = None,
    vocabulary_id:'int | None' = None,
    ) -> 'RuleDefinitionRecord':
    """ Stores one ruleset definition, optionally bound to a vocabulary.
    """
    document:'anydict' = {Documents_Key: _documents(text)}

    if vocabulary_id:
        document[Vocabulary_Key] = vocabulary_id

    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document=document,
        author=_author,
        comment='Create the ruleset',
        parent_id=parent_id,
    )
    return out

# ################################################################################################################################

def _publish(backend:'RuleSQLBackend', definition_id:'int', version:'int'=1) -> 'None':
    """ Makes one stored version live.
    """
    _ = backend.versions.publish(definition_id=definition_id, version=version, actor=_author)

# ################################################################################################################################

def _new_invoker(backend:'RuleSQLBackend') -> 'RulesetInvoker':
    """ Builds an invoker over the test backend - its caches are correct until `apply_change` evicts,
    exactly as the change stream listener does on a server.
    The tests enter `invoker.writer` as a context manager, which starts the writer and flushes it on exit.
    """
    writer = backend.decision_writer()

    out = RulesetInvoker(backend, writer)
    return out

# ################################################################################################################################

class _RecordingPublisher:
    """ Stands in for the Redis-backed change publisher, recording what would land on the stream.
    """
    def __init__(self) -> 'None':
        self.published = []

    def publish(self, kind:'str', definition_id:'int', name:'str', object_type:'str') -> 'None':
        self.published.append((kind, definition_id, name, object_type))

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
    definition = _create_ruleset(backend)
    _publish(backend, definition.id)

    invoker = _new_invoker(backend)

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
    invoker = _new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('pricing.default', {'credit_score': 720})

    assert result.status == InvocationStatus.Unknown_Ruleset
    assert 'pricing.default' in result.message
    assert result.decision is None

# ################################################################################################################################

def test_unpublished_ruleset_has_no_live_version(backend:'RuleSQLBackend') -> 'None':
    """ A ruleset that was never published has nothing to run.
    """
    _ = _create_ruleset(backend)

    invoker = _new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('payments.discounts', {'credit_score': 720})

    assert result.status == InvocationStatus.No_Live_Version
    assert 'payments.discounts' in result.message

# ################################################################################################################################

def test_ambiguous_name_is_refused(backend:'RuleSQLBackend') -> 'None':
    """ A name shared by rulesets under different parents cannot be invoked by name.
    """
    first = _create_ruleset(backend)
    _ = _create_ruleset(backend, parent_id=first.id)

    invoker = _new_invoker(backend)

    with invoker.writer:
        result = invoker.invoke('payments.discounts', {'credit_score': 720})

    assert result.status == InvocationStatus.Ambiguous_Name
    assert 'payments.discounts' in result.message

# ################################################################################################################################

def test_publish_becomes_visible_through_its_change_announcement(backend:'RuleSQLBackend') -> 'None':
    """ A publish changes what a live invocation runs the moment its announcement is applied -
    and until it is applied, the cache keeps serving what it holds, which is the whole point.
    """
    definition = _create_ruleset(backend)
    _publish(backend, definition.id)

    invoker = _new_invoker(backend)

    with invoker.writer:

        # Version one needs a 700 score, so 650 does not match ..
        before = invoker.invoke('payments.discounts', {'credit_score': 650})
        assert before.version == 1

        before_decision = before.decision
        assert before_decision is not None
        assert before_decision['outcome'] == Outcome.No_Match

        # .. store and publish version two with a lower bar ..
        document = {Documents_Key: _documents(_rules_text_lower_bar)}
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=document,
            author=_author,
            comment='Lower the bar',
        )
        _publish(backend, definition.id, version=2)

        # .. with no announcement applied yet the cached entry still serves version one ..
        unapplied = invoker.invoke('payments.discounts', {'credit_score': 650})
        assert unapplied.version == 1

        # .. applying the announcement, as the server's stream listener does, evicts the entry ..
        invoker.apply_change(definition.id, definition.name, definition.object_type)

        # .. and the same call now runs the new version.
        after = invoker.invoke('payments.discounts', {'credit_score': 650})
        assert after.version == 2

        after_decision = after.decision
        assert after_decision is not None
        assert after_decision['outcome'] == Outcome.Matched

# ################################################################################################################################

def test_pinned_version_stays_pinned(backend:'RuleSQLBackend') -> 'None':
    """ An explicitly requested version runs no matter what is live.
    """
    definition = _create_ruleset(backend)

    document = {Documents_Key: _documents(_rules_text_lower_bar)}
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=document,
        author=_author,
        comment='Lower the bar',
    )
    _publish(backend, definition.id, version=2)

    invoker = _new_invoker(backend)

    with invoker.writer:

        # The live version matches a 650 score ..
        live = invoker.invoke('payments.discounts', {'credit_score': 650})
        assert live.version == 2

        live_decision = live.decision
        assert live_decision is not None
        assert live_decision['outcome'] == Outcome.Matched

        # .. while pinned version one still needs 700 ..
        pinned = invoker.invoke('payments.discounts', {'credit_score': 650}, version=1)
        assert pinned.version == 1

        pinned_decision = pinned.decision
        assert pinned_decision is not None
        assert pinned_decision['outcome'] == Outcome.No_Match

        # .. and a version that does not exist is a readable error.
        missing = invoker.invoke('payments.discounts', {'credit_score': 650}, version=99)
        assert missing.status == InvocationStatus.Unknown_Version
        assert '99' in missing.message

# ################################################################################################################################

def test_vocabulary_validates_input_at_the_boundary(backend:'RuleSQLBackend') -> 'None':
    """ A ruleset bound to a vocabulary rejects invalid input in domain terms, before any rule runs.
    """
    vocabulary = backend.definitions.create(
        name='Loan approval',
        object_type=Definition_Type_Vocabulary,
        document=_vocabulary_document(),
        author=_author,
        comment='Create the vocabulary',
    )

    definition = _create_ruleset(backend, text=_rules_text_dotted, vocabulary_id=vocabulary.id)
    _publish(backend, definition.id)

    invoker = _new_invoker(backend)

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
    definition = _create_ruleset(backend)
    _publish(backend, definition.id)

    invoker = _new_invoker(backend)

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

def test_every_write_announces_itself(backend:'RuleSQLBackend') -> 'None':
    """ Each committed write of the mutating stores lands on the change stream exactly once,
    carrying the definition id, its name and its type.
    """
    publisher = _RecordingPublisher()
    backend.set_change_publisher(publisher)

    # Creating a definition announces the creation ..
    definition = _create_ruleset(backend)
    assert publisher.published == [
        (Change_Definition_Created, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. a new version announces itself ..
    publisher.published.clear()
    document = {Documents_Key: _documents(_rules_text_lower_bar)}
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=document,
        author=_author,
        comment='Lower the bar',
    )
    assert publisher.published == [
        (Change_Version_Created, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. a publish announces itself ..
    publisher.published.clear()
    _publish(backend, definition.id, version=2)
    assert publisher.published == [
        (Change_Version_Published, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. a restore announces itself ..
    publisher.published.clear()
    _ = backend.versions.restore(
        definition_id=definition.id,
        source_version=1,
        expected_current_version=2,
        actor=_author,
        comment='Back to the strict bar',
    )
    assert publisher.published == [
        (Change_Version_Restored, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. and so does an archival.
    publisher.published.clear()
    backend.definitions.archive(definition_id=definition.id, actor=_author)
    assert publisher.published == [
        (Change_Definition_Archived, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

# ################################################################################################################################

def test_vocabulary_edit_becomes_visible_through_its_change_announcement(backend:'RuleSQLBackend') -> 'None':
    """ Editing a vocabulary changes what the API validates against once its announcement is applied.
    """
    vocabulary = backend.definitions.create(
        name='Loan approval',
        object_type=Definition_Type_Vocabulary,
        document=_vocabulary_document(),
        author=_author,
        comment='Create the vocabulary',
    )

    definition = _create_ruleset(backend, text=_rules_text_dotted, vocabulary_id=vocabulary.id)
    _publish(backend, definition.id)

    invoker = _new_invoker(backend)

    with invoker.writer:

        # A score of 800 is legal under the original range ..
        before = invoker.invoke('payments.discounts', {'customer': {'creditScore': 800}})
        assert before.status == InvocationStatus.OK

        # .. now the vocabulary narrows the range to at most 750 ..
        narrowed = _vocabulary_document()
        narrowed['entities'][0]['attributes'][0]['domain'] = {'low': 300, 'high': 750}
        _ = backend.versions.create(
            definition_id=vocabulary.id,
            expected_current_version=1,
            document=narrowed,
            author=_author,
            comment='Narrow the range',
        )

        # .. the cached document still accepts 800 until the announcement is applied ..
        unapplied = invoker.invoke('payments.discounts', {'customer': {'creditScore': 800}})
        assert unapplied.status == InvocationStatus.OK

        # .. and once it is, the same input is rejected in domain terms.
        invoker.apply_change(vocabulary.id, vocabulary.name, vocabulary.object_type)

        after = invoker.invoke('payments.discounts', {'customer': {'creditScore': 800}})
        assert after.status == InvocationStatus.Invalid_Input

# ################################################################################################################################

def test_evict_all_drops_every_mutable_entry(backend:'RuleSQLBackend') -> 'None':
    """ After a full eviction, e.g. when the stream listener reconnects, the next request
    re-reads the database and sees everything that happened in the meantime.
    """
    definition = _create_ruleset(backend)
    _publish(backend, definition.id)

    invoker = _new_invoker(backend)

    with invoker.writer:

        # The first request caches the name's resolution ..
        first = invoker.invoke('payments.discounts', {'credit_score': 720})
        assert first.version == 1

        # .. a publish lands with no announcement, as if the listener were down ..
        document = {Documents_Key: _documents(_rules_text_lower_bar)}
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=document,
            author=_author,
            comment='Lower the bar',
        )
        _publish(backend, definition.id, version=2)

        # .. dropping everything, as the listener does on recovery, catches the caches up.
        invoker.evict_all()

        after = invoker.invoke('payments.discounts', {'credit_score': 720})
        assert after.version == 2

# ################################################################################################################################
# ################################################################################################################################
