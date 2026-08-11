# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The component contract of the shared editor endpoints - the payloads the chip editor
# sends over the wire are fed straight into the webapi functions as plain dicts and
# the responses are asserted, the same way the rule engine's parser tests work.

# pytest
import pytest

# Zato
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.api import Alerting
from zato.common.rule_engine import webapi
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key
from zato.common.rule_engine.webapi import BadRequestError, DocumentInvalidError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    RuleDefinitionRecord = RuleDefinitionRecord
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

# The actor every write in these tests is made by
_actor = 'test-webapi'

# What the editor types into the sentence view - one finished rule of the alerts ruleset
_rule_text = """
rule
    Test_Backlog
docs
    A backlog of fifty or more raises an email alert.
when
    alert.outstanding is at least 50
then
    outcome.action = 'email'
""".strip()

# The same rule with a subject the alerting vocabulary does not know
_unknown_term_text = _rule_text.replace('alert.outstanding', 'alert.no_such_measure')

# ################################################################################################################################
# ################################################################################################################################

def _find(backend:'RuleSQLBackend', name:'str', object_type:'str') -> 'RuleDefinitionRecord':
    """ Returns one seeded definition by name and kind.
    """
    out = backend.definitions.find_by_name(name=name, object_type=object_type)[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestValidate:

    def test_typed_rules_parse_into_canonical_documents(self, backend:'RuleSQLBackend') -> 'None':
        body = {'text': _rule_text, 'ruleset_name': Alerting.Ruleset_Name}

        result, note = webapi.validate_rules(backend, body)

        assert result['errors'] == []
        assert list(result['documents']) == [f'{Alerting.Ruleset_Name}_Test_Backlog']

        document = result['documents'][f'{Alerting.Ruleset_Name}_Test_Backlog']
        assert document['name'] == 'Test_Backlog'
        assert document['ruleset_name'] == Alerting.Ruleset_Name
        assert '1 rule' in note

# ################################################################################################################################

    def test_a_named_vocabulary_adds_semantic_findings(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        vocabulary = _find(backend, Alerting.Vocabulary_Name, Definition_Type_Vocabulary)

        body = {
            'text': _unknown_term_text,
            'ruleset_name': Alerting.Ruleset_Name,
            'vocabulary_id': vocabulary.id,
        }

        result, _ = webapi.validate_rules(backend, body)

        assert len(result['errors']) == 1
        assert 'no_such_measure' in result['errors'][0]['message']

# ################################################################################################################################

    def test_a_missing_field_is_a_bad_request(self, backend:'RuleSQLBackend') -> 'None':
        with pytest.raises(BadRequestError) as info:
            _ = webapi.validate_rules(backend, {'text': _rule_text})

        assert 'ruleset_name' in str(info.value)

# ################################################################################################################################
# ################################################################################################################################

class TestRender:

    def test_canonical_documents_render_back_to_text(self, backend:'RuleSQLBackend') -> 'None':
        parsed, _ = webapi.validate_rules(backend, {'text': _rule_text, 'ruleset_name': Alerting.Ruleset_Name})

        result, _ = webapi.render_rules({'documents': parsed['documents']})

        assert 'Test_Backlog' in result['text']
        assert 'alert.outstanding is at least 50' in result['text']
        assert "outcome.action = 'email'" in result['text']

# ################################################################################################################################
# ################################################################################################################################

class TestCompletion:

    def test_every_term_arrives_with_its_comparators_and_values(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        vocabulary = _find(backend, Alerting.Vocabulary_Name, Definition_Type_Vocabulary)

        result, _ = webapi.completion_terms(backend, vocabulary.id)
        by_path = {term['path']: term for term in result['terms']}

        # A number term offers the numeric comparators ..
        outstanding = by_path['alert.outstanding']
        assert outstanding['type'] == 'number'
        assert 'is at least' in outstanding['comparators']

        # .. and a choice term carries its closed pick list.
        action = by_path['outcome.action']
        assert action['type'] == 'choice'
        assert 'diagnose' in action['values']
        assert 'email' in action['values']

# ################################################################################################################################
# ################################################################################################################################

class TestSave:

    def test_the_editors_save_body_creates_a_new_version(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        ruleset = _find(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

        # The editor validates first and saves the parsed documents merged over the stored ones
        parsed, _ = webapi.validate_rules(backend, {'text': _rule_text, 'ruleset_name': Alerting.Ruleset_Name})

        preview, _ = webapi.preview_definition(backend, ruleset.id)
        merged = dict(preview['document'][Documents_Key])
        merged.update(parsed['documents'])

        body = {
            'definition_id': ruleset.id,
            'expected_current_version': ruleset.current_version,
            'document': {Documents_Key: merged},
            'comment': 'Edited rule Test_Backlog',
        }

        result, _ = webapi.save_document(backend, body, _actor)

        assert result['definition_id'] == ruleset.id
        assert result['version'] == ruleset.current_version + 1

        # The stored document now carries the new rule alongside the seeded ones
        preview, _ = webapi.preview_definition(backend, ruleset.id)
        assert f'{Alerting.Ruleset_Name}_Test_Backlog' in preview['document'][Documents_Key]

# ################################################################################################################################

    def test_an_invalid_document_is_refused_with_findings(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        ruleset = _find(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

        body = {
            'definition_id': ruleset.id,
            'expected_current_version': ruleset.current_version,
            'document': {Documents_Key: {}},
            'comment': 'An empty ruleset',
        }

        with pytest.raises(DocumentInvalidError) as info:
            _ = webapi.save_document(backend, body, _actor)

        assert 'at least one rule' in info.value.errors[0]['message']

        # Nothing was stored - the version is what it was
        ruleset = _find(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)
        assert ruleset.current_version == 1

# ################################################################################################################################
# ################################################################################################################################

class TestListingAndPreview:

    def test_the_definitions_come_back_as_rows(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        result, _ = webapi.list_definitions(backend, object_type=Definition_Type_Ruleset)
        names = [item['name'] for item in result['items']]

        assert Alerting.Ruleset_Name in names

# ################################################################################################################################

    def test_a_preview_carries_the_document_and_its_rendered_form(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        ruleset = _find(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

        result, _ = webapi.preview_definition(backend, ruleset.id)

        assert result['definition']['name'] == Alerting.Ruleset_Name
        assert Documents_Key in result['document']
        assert 'REST_Outgoing_Error_Rate' in result['rendered']

# ################################################################################################################################

    def test_a_vocabulary_comes_back_whole(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        vocabulary = _find(backend, Alerting.Vocabulary_Name, Definition_Type_Vocabulary)

        result, _ = webapi.get_vocabulary(backend, vocabulary.id)

        entity_names = [entity['name'] for entity in result['vocabulary']['entities']]
        assert entity_names == ['alert', 'outcome']

# ################################################################################################################################
# ################################################################################################################################

class TestSearch:

    def test_hits_carry_the_rendered_line_and_the_match_position(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)
        ruleset = _find(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

        result, note = webapi.search_definitions(backend, 'error_rate')

        # Every hit points back at the alerts ruleset and the rule the line came from ..
        assert result['items']
        hit = result['items'][0]
        assert hit['definition_id'] == ruleset.id
        assert hit['definition_name'] == Alerting.Ruleset_Name
        assert hit['rule'].startswith(Alerting.Ruleset_Name)

        # .. and the match position marks the very text asked for.
        line = hit['line']
        assert line[hit['match_start']:hit['match_end']].lower() == 'error_rate'

        assert 'match' in note

# ################################################################################################################################

    def test_text_nowhere_in_the_rules_finds_nothing(self, backend:'RuleSQLBackend') -> 'None':
        ensure_alerting_definitions(backend)

        result, note = webapi.search_definitions(backend, 'no_such_text_anywhere')

        assert result['items'] == []
        assert note == '0 matches'

# ################################################################################################################################
# ################################################################################################################################
