# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.common.rule_engine.document_checks import validate_definition_document
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.render import render_documents
from zato.common.rule_engine.scenarios import run_test_set
from zato.common.rule_engine.semantics import validate_document
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.rule_engine.vocabulary import Comparators_By_Type, iter_attributes, Status_Deprecated
from zato.common.util.logging_ import count_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import any_, anydict, dictlist, intnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# How many rows a definitions listing returns when the caller does not say otherwise.
Default_List_Limit = 100

# Where a definitions listing starts when the caller does not say otherwise.
Default_List_Offset = 0

# ################################################################################################################################
# ################################################################################################################################

class BadRequestError(Exception):
    """ A request whose parameters cannot be used - always reported with a readable message.
    """

# ################################################################################################################################
# ################################################################################################################################

class DocumentInvalidError(Exception):
    """ A document that failed its type's validation - the findings travel with the exception.
    """
    def __init__(self, errors:'dictlist') -> 'None':
        super().__init__('Document validation failed')
        self.errors = errors

# ################################################################################################################################
# ################################################################################################################################

def required(body:'anydict', name:'str') -> 'any_':
    """ Returns a field every request of a given kind must carry. A text field arrives stripped,
    so what is stored is what is read back, and it must carry something.
    """
    if name not in body:
        message = f'Missing required field -> {name}'
        raise BadRequestError(message)

    out = body[name]

    if isinstance(out, str):
        out = out.strip()
        if not out:
            message = f'Empty required field -> {name}'
            raise BadRequestError(message)

    return out

# ################################################################################################################################
# ################################################################################################################################

def definition_row(record:'any_') -> 'stranydict':
    """ One definition as a list or preview row.
    """
    out = {
        'id':              record.id,
        'name':            record.name,
        'object_type':     record.object_type,
        'parent_id':       record.parent_id,
        'current_version': record.current_version,
        'live_version':    record.live_version,
        'is_active':       record.is_active,
        'created_at':      record.created_at.isoformat(),
        'updated_at':      record.updated_at.isoformat(),
    }

    return out

# ################################################################################################################################

def event_row(record:'any_') -> 'stranydict':
    """ One history event with its parsed payload.
    """
    # Not every event carries a payload, hence the boundary check.
    payload = record.payload
    if payload is None:
        parsed = None
    else:
        parsed = json.loads(payload)

    out = {
        'id':            record.id,
        'definition_id': record.definition_id,
        'version':       record.version,
        'event_type':    record.event_type,
        'actor':         record.actor,
        'created_at':    record.created_at.isoformat(),
        'payload':       parsed,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def validate_rules(backend:'RuleSQLBackend', body:'anydict') -> 'tuple[stranydict, str]':
    """ Parses typed rules and, against a named vocabulary, checks their semantics too.
    """
    text = required(body, 'text')
    ruleset_name = required(body, 'ruleset_name')

    documents, errors = parse_data_details(text, ruleset_name)

    # Semantic checks join in when the request names a vocabulary to validate against.
    if vocabulary_id := body.get('vocabulary_id'):
        vocabulary = backend.definitions.get_document(vocabulary_id)

        for document in documents.values():
            semantic_errors = validate_document(document, vocabulary)
            errors.extend(semantic_errors)

    rules_text = count_text(len(documents), 'rule', 'rules')
    findings_text = count_text(len(errors), 'finding', 'findings')
    note = f'`{ruleset_name}` -> {rules_text}, {findings_text}'

    out = {'documents': documents, 'errors': errors}
    return out, note

# ################################################################################################################################

def render_rules(body:'anydict') -> 'tuple[stranydict, str]':
    """ The readable text form of canonical rule documents.
    """
    documents = required(body, 'documents')

    text = render_documents(documents)
    note = count_text(len(documents), 'rule', 'rules')

    out = {'text': text}
    return out, note

# ################################################################################################################################

def completion_terms(backend:'RuleSQLBackend', definition_id:'int') -> 'tuple[stranydict, str]':
    """ The completion payload - every offerable term with its type, phrase, values and legal comparators.
    """
    vocabulary = backend.definitions.get_document(definition_id)

    terms:'dictlist' = []

    for path, attribute in iter_attributes(vocabulary):

        # Deprecated terms keep old rules running but are never offered again.
        if attribute['status'] == Status_Deprecated:
            continue

        comparators = sorted(Comparators_By_Type[attribute['type']])

        term = {
            'path':        path,
            'type':        attribute['type'],
            'phrase':      attribute['phrase'],
            'comparators': comparators,
        }

        # Choices carry their closed pick list ..
        if 'values' in attribute:
            term['values'] = attribute['values']

        # .. and ranges carry their domain.
        if 'domain' in attribute:
            term['domain'] = attribute['domain']

        terms.append(term)

    terms_text = count_text(len(terms), 'term', 'terms')
    note = f'{terms_text} of vocabulary {definition_id}'

    out = {'terms': terms}
    return out, note

# ################################################################################################################################

def save_document(backend:'RuleSQLBackend', body:'anydict', actor:'str') -> 'tuple[stranydict, str]':
    """ Saves one document - a new definition with its first version or a new optimistic version of an existing one.

    Whatever the caller sends is validated here against the checks its own type declares, so a
    document only ever reaches the store in a shape the engine can run, whoever posted it.
    """
    document = required(body, 'document')
    comment = required(body, 'comment')

    # An existing definition keeps the type it was created with, a new one declares it ..
    definition_id = body.get('definition_id')

    if definition_id:
        object_type = backend.definitions.get(definition_id).object_type
    else:
        object_type = required(body, 'object_type')

    # .. and the document has to pass that type's own validation before anything is stored.
    errors = validate_definition_document(object_type, document)

    if errors:
        raise DocumentInvalidError(errors)

    # An existing definition gains a new optimistic version ..
    if definition_id:
        expected_current_version = required(body, 'expected_current_version')
        record = backend.versions.create(
            definition_id=definition_id,
            expected_current_version=expected_current_version,
            document=document,
            author=actor,
            comment=comment,
        )
        result = {'definition_id': definition_id, 'version': record.version}
        note = f'{object_type} {definition_id} stored as version {record.version}'

    # .. while a new one comes into being together with its first version.
    else:
        name = required(body, 'name')
        created = backend.definitions.create(
            name=name,
            object_type=object_type,
            document=document,
            author=actor,
            comment=comment,
        )
        definition_id = created.id
        result = {'definition_id': created.id, 'version': created.current_version}
        note = f'{object_type} `{name}` created as {created.id}, version {created.current_version}'

    # The where-used index follows every save whose document carries rule documents.
    if Documents_Key in document:
        _ = backend.references.rebuild(definition_id=definition_id, documents=document[Documents_Key])

    return result, note

# ################################################################################################################################

def run_outcomes(body:'anydict') -> 'tuple[stranydict, str]':
    """ The live-outcomes feed - the edited documents run against a test set, per-scenario results and traces included.
    """
    documents = required(body, 'documents')
    test_set = required(body, 'test_set')

    result = run_test_set(test_set, documents)

    total = result['total']
    passed = result['passed']
    failed = result['failed']
    explored = result['explored']

    scenarios_text = count_text(total, 'scenario', 'scenarios')
    rules_text = count_text(len(documents), 'edited rule', 'edited rules')

    note = f'{scenarios_text} against {rules_text} -> {passed} passed, {failed} failed, {explored} explored'

    return result, note

# ################################################################################################################################

def list_definitions(
    backend:'RuleSQLBackend',
    object_type:'strnone'=None,
    search_text:'strnone'=None,
    include_inactive:'bool'=False,
    limit:'intnone'=None,
    offset:'intnone'=None,
) -> 'tuple[stranydict, str]':
    """ Every stored definition, filterable by kind and content, paged.
    """
    if limit is None:
        limit = Default_List_Limit

    if offset is None:
        offset = Default_List_Offset

    records = backend.definitions.list(
        object_type=object_type,
        search_text=search_text,
        include_inactive=include_inactive,
        limit=limit,
        offset=offset,
    )

    items = []
    for record in records:
        row = definition_row(record)
        items.append(row)

    note = count_text(len(items), 'definition', 'definitions')

    out = {'items': items}
    return out, note

# ################################################################################################################################

def search_definitions(backend:'RuleSQLBackend', query:'str') -> 'tuple[stranydict, str]':
    """ Full-text search over rendered rule sentences, each hit carrying its match position.
    """
    hits = backend.search.search(query)

    note = count_text(len(hits), 'match', 'matches')

    out = {'items': hits}
    return out, note

# ################################################################################################################################

def preview_definition(backend:'RuleSQLBackend', definition_id:'int') -> 'tuple[stranydict, str]':
    """ Preview without opening - the definition together with its stored document and rendered rules.
    """
    record = backend.definitions.get(definition_id)
    document = deserialize_document(record.document)

    # Only documents that carry rule documents have a readable rendered form.
    if Documents_Key in document:
        documents = document[Documents_Key]
        rendered = render_documents(documents)
        rules_text = count_text(len(documents), 'rule', 'rules')
        note = f'{record.object_type} `{record.name}` version {record.current_version}, {rules_text}'
    else:
        rendered = None
        note = f'{record.object_type} `{record.name}` version {record.current_version}'

    out = {
        'definition': definition_row(record),
        'document': document,
        'rendered': rendered,
    }
    return out, note

# ################################################################################################################################

def get_vocabulary(backend:'RuleSQLBackend', definition_id:'int') -> 'tuple[stranydict, str]':
    """ One stored vocabulary document.
    """
    document = backend.definitions.get_document(definition_id)

    entities = document['entities']
    term_count = 0

    for entity in entities:
        term_count += len(entity['attributes'])

    entities_text = count_text(len(entities), 'entity', 'entities')
    terms_text = count_text(term_count, 'term', 'terms')
    note = f'{entities_text}, {terms_text}'

    out = {'vocabulary': document}
    return out, note

# ################################################################################################################################
# ################################################################################################################################
