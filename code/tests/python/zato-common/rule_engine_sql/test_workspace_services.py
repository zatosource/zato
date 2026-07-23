# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.rules.parser import parse_data_details
from zato.common.rules.sql import RecordNotFoundError, RuleDefinitionRecord, RuleSQLBackend
from zato.common.rules.sql.constants import Definition_Type_Ruleset, Documents_Key, Event_Type_Follow_Changed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_author = 'anna.k'
_actor = 'jan.b'

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

# ################################################################################################################################
# ################################################################################################################################

def _documents() -> 'anydict':
    """ Parses the shared rules text into canonical documents keyed by full name.
    """
    documents, errors = parse_data_details(_rules_text, 'loans')
    if errors:
        raise Exception(f'Unexpected parse errors -> {errors}')

    return documents

# ################################################################################################################################

def _create_ruleset(backend:'RuleSQLBackend', name:'str' = 'Loans') -> 'RuleDefinitionRecord':
    """ Stores one canonical ruleset definition.
    """
    out = backend.definitions.create(
        name=name,
        object_type=Definition_Type_Ruleset,
        document={Documents_Key: _documents()},
        author=_author,
        comment='Create the ruleset',
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_reference_index_answers_where_used(backend:'RuleSQLBackend') -> 'None':
    """ A rebuilt index answers where-used from its promoted term column.
    """
    definition = _create_ruleset(backend)
    documents = _documents()

    # Index every term the documents reference ..
    row_count = backend.references.rebuild(definition_id=definition.id, documents=documents)
    assert row_count > 0

    # .. the condition subject is found where it is used ..
    usages = backend.references.where_used('credit_score')
    assert len(usages) == 1

    usage = usages[0]
    assert usage.definition_id == definition.id
    assert usage.rule_name == 'loans_Preferential_rate'
    assert usage.block == 'when'
    assert usage.role == 'subject'

    # .. action targets are indexed too ..
    targets = backend.references.where_used('rate')
    assert len(targets) == 1
    assert targets[0].block == 'then'
    assert targets[0].role == 'target'

    # .. and a term nothing references can be deleted safely.
    assert backend.references.is_used('credit_score') is True
    assert backend.references.is_used('no_such_term') is False

# ################################################################################################################################

def test_reference_index_rebuild_replaces_not_appends(backend:'RuleSQLBackend') -> 'None':
    """ Rebuilding twice never duplicates index rows.
    """
    definition = _create_ruleset(backend)
    documents = _documents()

    _ = backend.references.rebuild(definition_id=definition.id, documents=documents)
    _ = backend.references.rebuild(definition_id=definition.id, documents=documents)

    usages = backend.references.where_used('credit_score')
    assert len(usages) == 1

# ################################################################################################################################

def test_follow_store_and_feed(backend:'RuleSQLBackend') -> 'None':
    """ Following starts a feed clock, marking seen empties the feed and unfollowing stops it.
    """
    definition = _create_ruleset(backend)

    # Start following ..
    follow = backend.follows.follow(actor=_actor, definition_id=definition.id)
    assert follow.actor == _actor
    assert backend.follows.is_following(actor=_actor, definition_id=definition.id) is True

    # .. following twice is the same follow ..
    again = backend.follows.follow(actor=_actor, definition_id=definition.id)
    assert again.id == follow.id

    followed = backend.follows.list_followed(_actor)
    assert len(followed) == 1

    # .. an event after the follow appears in the feed ..
    _ = backend.events.append(
        definition_id=definition.id,
        version=1,
        event_type='review.commented',
        actor=_author,
        payload={'comment': 'Looks good'},
    )
    feed = backend.follows.feed(_actor)
    event_types = set()

    for event in feed:
        event_types.add(event.event_type)

    assert 'review.commented' in event_types

    # .. marking the definition seen moves the clock past that event ..
    backend.follows.mark_seen(actor=_actor, definition_id=definition.id)
    assert backend.follows.feed(_actor) == []

    # .. unfollowing removes the follow and leaves its trace in the activity feed ..
    backend.follows.unfollow(actor=_actor, definition_id=definition.id)
    assert backend.follows.is_following(actor=_actor, definition_id=definition.id) is False
    assert backend.follows.list_followed(_actor) == []

    events = backend.events.list(definition_id=definition.id)
    follow_changes = []

    for event in events:
        if event.event_type == Event_Type_Follow_Changed:
            follow_changes.append(event)

    assert len(follow_changes) == 2

    # .. and unfollowing what is not followed is loud.
    with pytest.raises(RecordNotFoundError):
        backend.follows.unfollow(actor=_actor, definition_id=definition.id)

# ################################################################################################################################

def test_saved_views_are_per_actor_and_replaceable(backend:'RuleSQLBackend') -> 'None':
    """ Saved views store named filter payloads that saving again replaces.
    """
    # Save one view ..
    payload = {'object_type': 'ruleset', 'search_text': 'loans'}
    view = backend.views.save(actor=_actor, name='My rulesets', payload=payload)
    assert view.name == 'My rulesets'

    # .. read it back through its owner and name ..
    stored = backend.views.get(actor=_actor, name='My rulesets')
    assert stored.id == view.id

    # .. saving the same name replaces the payload without creating a second view ..
    replacement = {'object_type': 'ruleset', 'search_text': 'mortgages'}
    replaced = backend.views.save(actor=_actor, name='My rulesets', payload=replacement)
    assert replaced.id == view.id
    assert 'mortgages' in replaced.payload

    views = backend.views.list(_actor)
    assert len(views) == 1

    # .. another actor's views are their own ..
    assert backend.views.list(_author) == []

    # .. and deleting is definitive.
    backend.views.delete(actor=_actor, name='My rulesets')

    with pytest.raises(RecordNotFoundError):
        _ = backend.views.get(actor=_actor, name='My rulesets')

# ################################################################################################################################

def test_recents_keep_one_row_per_definition_newest_first(backend:'RuleSQLBackend') -> 'None':
    """ Visits are one row per definition, ordered by the latest visit.
    """
    first = _create_ruleset(backend, 'Loans')
    second = _create_ruleset(backend, 'Mortgages')

    # Visit the first, then the second, then the first again ..
    backend.views.touch_recent(actor=_actor, definition_id=first.id)
    backend.views.touch_recent(actor=_actor, definition_id=second.id)
    backend.views.touch_recent(actor=_actor, definition_id=first.id)

    recents = backend.views.list_recents(_actor)

    # .. each definition appears once ..
    assert len(recents) == 2

    # .. and the repeat visit moved the first definition to the top.
    assert recents[0].definition_id == first.id
    assert recents[1].definition_id == second.id

# ################################################################################################################################

def test_content_search_finds_rendered_sentences(backend:'RuleSQLBackend') -> 'None':
    """ Search matches the sentences a person reads and reports where the match is.
    """
    definition = _create_ruleset(backend)

    # A one-token search finds the term inside a rendered condition ..
    hits = backend.search.search('credit_score')
    assert len(hits) > 0

    hit = hits[0]
    assert hit['definition_id'] == definition.id
    assert hit['definition_name'] == 'Loans'
    assert hit['rule'] == 'loans_Preferential_rate'

    # .. the whole rendered line comes back with the match position inside it ..
    line = hit['line']
    start = hit['match_start']
    end = hit['match_end']
    assert line[start:end] == 'credit_score'
    assert 'is at least 700' in line

    # .. a search with spaces matches the rendered sentence, not the stored JSON ..
    sentence_hits = backend.search.search('at least 700')
    assert len(sentence_hits) == 1

    # .. the search is case-insensitive ..
    upper_hits = backend.search.search('CREDIT_SCORE')
    assert len(upper_hits) == len(hits)

    # .. and text nothing contains finds nothing.
    assert backend.search.search('no_such_text_anywhere') == []

# ################################################################################################################################
# ################################################################################################################################
