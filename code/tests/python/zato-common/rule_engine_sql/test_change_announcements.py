# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.changes import Change_Definition_Archived, Change_Definition_Created, \
    Change_Version_Created, Change_Version_Published, Change_Version_Restored
from zato.common.rule_engine.ingestion import Outcome
from zato.common.rule_engine.invocation import InvocationStatus
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key

# Local
from invocation_test_data import author, create_ruleset, documents_of, new_invoker, publish, RecordingPublisher, \
    rules_text_dotted, rules_text_lower_bar, vocabulary_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

def test_publish_becomes_visible_through_its_change_announcement(backend:'RuleSQLBackend') -> 'None':
    """ A publish changes what a live invocation runs the moment its announcement is applied -
    and until it is applied, the cache keeps serving what it holds, which is the whole point.
    """
    definition = create_ruleset(backend)
    publish(backend, definition.id)

    invoker = new_invoker(backend)

    with invoker.writer:

        # Version one needs a 700 score, so 650 does not match ..
        before = invoker.invoke('payments.discounts', {'credit_score': 650})
        assert before.version == 1

        before_decision = before.decision
        assert before_decision is not None
        assert before_decision['outcome'] == Outcome.No_Match

        # .. store and publish version two with a lower bar ..
        document = {Documents_Key: documents_of(rules_text_lower_bar)}
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=document,
            author=author,
            comment='Lower the bar',
        )
        publish(backend, definition.id, version=2)

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
    definition = create_ruleset(backend)

    document = {Documents_Key: documents_of(rules_text_lower_bar)}
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=document,
        author=author,
        comment='Lower the bar',
    )
    publish(backend, definition.id, version=2)

    invoker = new_invoker(backend)

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

def test_every_write_announces_itself(backend:'RuleSQLBackend') -> 'None':
    """ Each committed write of the mutating stores lands on the change stream exactly once,
    carrying the definition id, its name and its type.
    """
    publisher = RecordingPublisher()
    backend.set_change_publisher(publisher)

    # Creating a definition announces the creation ..
    definition = create_ruleset(backend)
    assert publisher.published == [
        (Change_Definition_Created, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. a new version announces itself ..
    publisher.published.clear()
    document = {Documents_Key: documents_of(rules_text_lower_bar)}
    _ = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=1,
        document=document,
        author=author,
        comment='Lower the bar',
    )
    assert publisher.published == [
        (Change_Version_Created, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. a publish announces itself ..
    publisher.published.clear()
    publish(backend, definition.id, version=2)
    assert publisher.published == [
        (Change_Version_Published, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. a restore announces itself ..
    publisher.published.clear()
    _ = backend.versions.restore(
        definition_id=definition.id,
        source_version=1,
        expected_current_version=2,
        actor=author,
        comment='Back to the strict bar',
    )
    assert publisher.published == [
        (Change_Version_Restored, definition.id, 'payments.discounts', Definition_Type_Ruleset),
    ]

    # .. and so does an archival.
    publisher.published.clear()
    backend.definitions.archive(definition_id=definition.id, actor=author)
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
        document=vocabulary_document(),
        author=author,
        comment='Create the vocabulary',
    )

    definition = create_ruleset(backend, text=rules_text_dotted, vocabulary_id=vocabulary.id)
    publish(backend, definition.id)

    invoker = new_invoker(backend)

    with invoker.writer:

        # A score of 800 is legal under the original range ..
        before = invoker.invoke('payments.discounts', {'customer': {'creditScore': 800}})
        assert before.status == InvocationStatus.OK

        # .. now the vocabulary narrows the range to at most 750 ..
        narrowed = vocabulary_document()
        narrowed['entities'][0]['attributes'][0]['domain'] = {'low': 300, 'high': 750}
        _ = backend.versions.create(
            definition_id=vocabulary.id,
            expected_current_version=1,
            document=narrowed,
            author=author,
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
    definition = create_ruleset(backend)
    publish(backend, definition.id)

    invoker = new_invoker(backend)

    with invoker.writer:

        # The first request caches the name's resolution ..
        first = invoker.invoke('payments.discounts', {'credit_score': 720})
        assert first.version == 1

        # .. a publish lands with no announcement, as if the listener were down ..
        document = {Documents_Key: documents_of(rules_text_lower_bar)}
        _ = backend.versions.create(
            definition_id=definition.id,
            expected_current_version=1,
            document=document,
            author=author,
            comment='Lower the bar',
        )
        publish(backend, definition.id, version=2)

        # .. dropping everything, as the listener does on recovery, catches the caches up.
        invoker.evict_all()

        after = invoker.invoke('payments.discounts', {'credit_score': 720})
        assert after.version == 2

# ################################################################################################################################
# ################################################################################################################################
