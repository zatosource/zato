# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.rule_engine.invocation import is_ruleset_allowed, Vocabulary_Key
from zato.common.rule_engine.openapi import example_from_vocabulary, nest_flat_input, vocabulary_to_schema
from zato.common.rule_engine.sql.constants import Definition_Type_Test_Set
from zato.common.rule_engine.sql.document import deserialize_document
from zato.server.rule_engine_api import get_backend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict, tuple_
    from zato.server.base.parallel import ParallelServer
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The tag every ruleset operation is grouped under in the rendered document.
_rule_engine_tag = 'Rule engine'

# The name of the one shared response schema every ruleset operation returns.
_decision_schema_name = 'RuleEngineDecision'

# What every completed invocation returns - the same envelope the invoke service builds.
_decision_schema = {
    'type': 'object',
    'properties': {
        'ruleset':     {'type': 'string',  'description': 'The name the ruleset was invoked under'},
        'version':     {'type': 'integer', 'description': 'The version that served this call'},
        'decision_id': {'type': 'string',  'description': 'The id this decision is logged under'},
        'outcome':     {'enum': ['matched', 'no-match', 'error'], 'description': 'What the evaluation ended with'},
        'outputs':     {'type': 'object',  'description': 'The merged assignments of every rule that fired'},
        'messages':    {'type': 'array', 'items': {'type': 'object'}, 'description': 'One entry per fired rule, in rule order'},
        'duration_ms': {'type': 'number',  'description': 'How long the evaluation took'},
    },
}

# ################################################################################################################################
# ################################################################################################################################

def _scenario_example(backend:'RuleSQLBackend', definition_id:'int') -> 'anydict | None':
    """ Returns the first test scenario of one ruleset as a nested example request body,
    or None if the ruleset has no suites. Real scenarios beat synthesized values.
    """
    suites = backend.definitions.list(parent_id=definition_id, object_type=Definition_Type_Test_Set)

    for suite in suites:
        document = deserialize_document(suite.document)

        # The first scenario of the first suite that has one is the example -
        # its input is flat dotted paths, while the API accepts nested JSON.
        if scenarios := document.get('scenarios'):
            out = nest_flat_input(scenarios[0]['input'])
            return out

# ################################################################################################################################

def _ruleset_operation(
    backend:'RuleSQLBackend',
    definition:'RuleDefinitionRecord',
    schemas:'anydict',
    ) -> 'anydict':
    """ Builds the POST operation of one published ruleset, registering its request schema
    as a component along the way.
    """
    # The live snapshot decides which vocabulary, if any, describes the inputs ..
    live_version = backend.versions.get(definition.id, definition.live_version)
    payload = deserialize_document(live_version.document)
    vocabulary_id = payload.get(Vocabulary_Key)

    # .. a vocabulary gives callers typed fields, enums and ranges ..
    if vocabulary_id:
        vocabulary = backend.definitions.get_document(vocabulary_id)
        request_schema = vocabulary_to_schema(vocabulary)
        default_example = example_from_vocabulary(vocabulary)

    # .. without one the body is an object of whatever terms the rules read.
    else:
        request_schema = {'type': 'object'}
        default_example = None

    sanitized_name = definition.name.replace('.', '_').replace(' ', '_')
    schema_name = f'RuleEngineInput_{sanitized_name}'
    schemas[schema_name] = request_schema

    # A real test scenario beats a synthesized example.
    example = _scenario_example(backend, definition.id)

    if example is None:
        example = default_example

    request_content:'anydict' = {'schema': {'$ref': f'#/components/schemas/{schema_name}'}}

    if example:
        request_content['example'] = example

    operation = {
        'operationId': f'invoke_{sanitized_name}',
        'summary': f'Invoke ruleset {definition.name}',
        'tags': [_rule_engine_tag],
        'requestBody': {
            'required': True,
            'content': {'application/json': request_content},
        },
        'responses': {
            '200': {
                'description': 'The complete decision, logged under the decision id it carries',
                'content': {'application/json': {'schema': {'$ref': f'#/components/schemas/{_decision_schema_name}'}}},
            },
        },
    }

    out = {'post': operation}
    return out

# ################################################################################################################################

def merge_rule_engine_spec(server:'ParallelServer', spec:'anydict', channel_map:'anydict') -> 'tuple_[anydict, anydict]':
    """ Merges the per-ruleset paths of every Rule engine API object into the given document.

    This runs fresh on every spec request - a spec fetch is a cold path, so the published
    rulesets and their vocabularies are read straight from the rule engine database and the
    document is always exactly what that database holds at this moment. Nothing is cached,
    nothing invalidates and there is no staleness of any kind.
    """
    api_objects = server.config_manager.gateway_rule_engine

    # Most environments have no Rule engine API objects and skip all of this,
    # including the database reads below.
    if not api_objects:
        return spec, channel_map

    # Filtering needs the channel id each documented path belongs to.
    url_data = server.config_manager.request_dispatcher.url_data
    channel_id_by_name = {item['name']: item['id'] for item in url_data.channel_data}

    backend = get_backend()
    published = backend.definitions.list_published_rulesets()

    extra_paths:'anydict' = {}
    extra_schemas:'anydict' = {}
    extra_channel_map:'anydict' = {}

    for object_name, object_config in api_objects.items():

        # An inactive object serves no requests, so it documents none either ..
        if not object_config['is_active']:
            continue

        # .. an object whose channel is gone cannot be filtered, so it is skipped ..
        channel_id = channel_id_by_name.get(object_name)

        if channel_id is None:
            logger.info('Rule engine API `%s` has no channel, skipping its documentation', object_name)
            continue

        # .. the object's grants decide which of the published rulesets it exposes.
        base_path = object_config['url_path'].rstrip('/')
        granted_rulesets = object_config.get('rulesets') or []

        for definition in published:

            if not is_ruleset_allowed(definition.name, granted_rulesets):
                continue

            path = f'{base_path}/{definition.name}'
            extra_paths[path] = _ruleset_operation(backend, definition, extra_schemas)
            extra_channel_map[path] = {'post': channel_id}

    # No object exposed anything, so the document stays as it was.
    if not extra_paths:
        return spec, channel_map

    # Every operation shares the one decision envelope.
    extra_schemas[_decision_schema_name] = _decision_schema

    # The merged document shares the unchanged parts with the cached one, which is safe
    # because callers only ever serialize documents, never modify them.
    merged_spec = dict(spec)
    merged_spec['paths'] = dict(spec['paths'])
    merged_spec['paths'].update(extra_paths)

    merged_spec['components'] = dict(spec['components'])
    merged_spec['components']['schemas'] = dict(spec['components']['schemas'])
    merged_spec['components']['schemas'].update(extra_schemas)

    merged_channel_map = dict(channel_map)
    merged_channel_map.update(extra_channel_map)

    return merged_spec, merged_channel_map

# ################################################################################################################################
# ################################################################################################################################
