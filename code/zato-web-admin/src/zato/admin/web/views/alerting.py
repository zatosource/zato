# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The alert rules screens under Monitoring - the listing, the actions on it and the screen
# embedding the rule engine's shared chip editor. Everything talks to the rule engine's
# SQL store in process, through the same shared webapi functions the rule engine
# dashboard's own views wrap - no HTTP hop and one editor codebase for both apps.

# stdlib
import json
import logging
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR

# Django
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.rule_store import get_backend
from zato.admin.web.views import method_allowed
from zato.common.api import Alerting
from zato.common.defaults import default_cluster_id
from zato.common.rule_engine import webapi
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.rule_engine.webapi import BadRequestError, DocumentInvalidError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import any_, anydict, dictlist, stranydict
    any_ = any_
    anydict = anydict
    dictlist = dictlist
    RuleDefinitionRecord = RuleDefinitionRecord
    RuleSQLBackend = RuleSQLBackend
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The listing's tabs, in the order they show.
_listing_tabs = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('all', 'All'),
)

# ################################################################################################################################
# ################################################################################################################################

def _find_definition(backend:'RuleSQLBackend', name:'str', object_type:'str') -> 'RuleDefinitionRecord | None':
    """ Returns one definition by the name and kind it was seeded under, or None when
    the store does not hold it yet.
    """
    matches = backend.definitions.find_by_name(name=name, object_type=object_type)

    if matches:
        out = matches[0]
    else:
        out = None

    return out

# ################################################################################################################################

def _rule_rows(documents:'anydict') -> 'dictlist':
    """ The listing rows - one per rule of the alerts ruleset, in rule order.
    """

    # Our response to produce
    out = []

    for key, document in documents.items():

        # The flag is genuinely optional in a rule document - its absence means the rule is active
        is_active = document.get('is_active') is not False

        out.append({
            'key': key,
            'name': document['name'],
            'docs': document['docs'],
            'is_active': is_active,
        })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The alert rules listing - the rules of the alerts ruleset with their state,
    and the publish control when there are unpublished changes.
    """
    backend = get_backend()
    definition = _find_definition(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

    rows = []
    current_version = 0
    live_version = None

    if definition:
        current_version = definition.current_version
        live_version = definition.live_version

        document = deserialize_document(definition.document)
        rows = _rule_rows(document[Documents_Key])

    # One tab per state, with everything in the last one.
    tabs = []

    for value, label in _listing_tabs:

        if value == 'all':
            tab_items = rows
        elif value == 'active':
            tab_items = [row for row in rows if row['is_active']]
        else:
            tab_items = [row for row in rows if not row['is_active']]

        tabs.append({
            'name': value,
            'label': label,
            'items': tab_items,
            'count': len(tab_items),
        })

    # The publish control shows when the newest version is not the live one.
    has_draft = bool(definition) and current_version != live_version

    return TemplateResponse(req, 'zato/alerting/index.html', {
        'cluster_id': default_cluster_id,
        'tabs': tabs,
        'default_tab': 'active',
        'current_version': current_version,
        'live_version': live_version,
        'has_draft': has_draft,
        'zato_clusters': True,
        'zato_template_name': 'zato/alerting/index.html',
    })

# ################################################################################################################################

@method_allowed('GET')
def editor(req:'any_') -> 'TemplateResponse':
    """ The rule editor - one screen embedding the shared chip editor, opened either
    on an existing rule or with the name of a rule to create.
    """
    backend = get_backend()
    definition = _find_definition(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

    definition_id = definition.id if definition else 0
    rule_key = req.GET.get('rule', '')

    # The header names the rule being edited, read from the stored document.
    rule_name = ''

    if definition and rule_key:
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        if rule_key in documents:
            rule_name = documents[rule_key]['name']

    return TemplateResponse(req, 'zato/alerting/editor.html', {
        'cluster_id': default_cluster_id,
        'definition_id': definition_id,
        'rule_key': rule_key,
        'rule_name': rule_name,
        'new_rule_name': req.GET.get('new', ''),
        'zato_clusters': True,
        'zato_template_name': 'zato/alerting/editor.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def action(req:'any_') -> 'HttpResponse':
    """ Runs one listing action - publish, activate, deactivate or delete -
    against the alerts ruleset, with the Dashboard user as the actor.
    """
    backend = get_backend()
    definition = _find_definition(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

    if not definition:
        out = JsonResponse({'error': 'There is no alerts ruleset to act on'}, status=BAD_REQUEST)
        return out

    action_name = req.POST['action']
    actor = req.user.username

    try:

        # Publishing moves the live pointer to the newest version ..
        if action_name == 'publish':
            _ = backend.versions.publish(
                definition_id=definition.id, version=definition.current_version, actor=actor)
            out = JsonResponse({'is_ok': True})
            return out

        # .. everything else rewrites the rule documents into a new draft version.
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]
        rule_key = req.POST['rule']

        if rule_key not in documents:
            out = JsonResponse({'error': f'No such rule -> {rule_key}'}, status=BAD_REQUEST)
            return out

        rule_name = documents[rule_key]['name']

        if action_name == 'delete':

            # A ruleset with no rules cannot be stored, so the last rule stays
            if len(documents) == 1:
                out = JsonResponse({'error': 'The last rule of the ruleset cannot be deleted'}, status=BAD_REQUEST)
                return out

            del documents[rule_key]
            comment = f'Deleted rule {rule_name}'

        elif action_name in ('activate', 'deactivate'):
            documents[rule_key]['is_active'] = action_name == 'activate'
            comment = f'{action_name.capitalize()}d rule {rule_name}'

        else:
            out = JsonResponse({'error': f'No such action -> {action_name}'}, status=BAD_REQUEST)
            return out

        body = {
            'definition_id': definition.id,
            'expected_current_version': definition.current_version,
            'document': {Documents_Key: documents},
            'comment': comment,
        }
        _ = webapi.save_document(backend, body, actor)

        out = JsonResponse({'is_ok': True})
        return out

    except DocumentInvalidError as e:
        out = JsonResponse({'error': json.dumps(e.errors)}, status=BAD_REQUEST)
        return out

    except Exception as e:
        logger.warning('Alert rules action `%s` failed -> %s', action_name, e)
        out = JsonResponse({'error': str(e)}, status=INTERNAL_SERVER_ERROR)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _read_json(req:'any_') -> 'stranydict':
    """ The JSON body of one editor request.
    """
    out = json.loads(req.body)
    return out

# ################################################################################################################################

def _json_error(func:'any_') -> 'any_':
    """ Turns the shared webapi's exceptions into the JSON error answers the editor's
    data layer reads - the same contract the rule engine dashboard's own views keep.
    """
    def wrapper(req:'any_', *args:'any_', **kwargs:'any_') -> 'any_':
        try:
            out = func(req, *args, **kwargs)
        except BadRequestError as e:
            out = JsonResponse({'error': str(e)}, status=BAD_REQUEST)
        except Exception as e:
            logger.warning('Alerting editor endpoint failed -> %s', e)
            out = JsonResponse({'error': str(e)}, status=INTERNAL_SERVER_ERROR)
        return out

    return wrapper

# ################################################################################################################################

@method_allowed('GET')
@_json_error
def api_definitions(req:'any_') -> 'JsonResponse':
    """ The definitions the editor loads - only the alerting pair, whichever kind is asked for,
    so the editor never sees the store's unrelated rulesets and vocabularies.
    """
    backend = get_backend()
    object_type = req.GET['object_type']

    if object_type == Definition_Type_Vocabulary:
        name = Alerting.Vocabulary_Name
    else:
        name = Alerting.Ruleset_Name

    definition = _find_definition(backend, name, object_type)

    items = []

    if definition:
        items.append(webapi.definition_row(definition))

    out = JsonResponse({'items': items})
    return out

# ################################################################################################################################

@method_allowed('GET')
@_json_error
def api_preview(req:'any_', definition_id:'int') -> 'JsonResponse':
    """ One definition with its stored document - what the editor loads a ruleset through.
    """
    result, _ = webapi.preview_definition(get_backend(), definition_id)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@method_allowed('GET')
@_json_error
def api_vocabulary(req:'any_', definition_id:'int') -> 'JsonResponse':
    """ One stored vocabulary document.
    """
    result, _ = webapi.get_vocabulary(get_backend(), definition_id)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@method_allowed('GET')
@_json_error
def api_completion(req:'any_', definition_id:'int') -> 'JsonResponse':
    """ The completion payload - every offerable term with its type, phrase, values
    and legal comparators.
    """
    result, _ = webapi.completion_terms(get_backend(), definition_id)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@method_allowed('POST')
@_json_error
def api_validate(req:'any_') -> 'JsonResponse':
    """ Parses typed rules and, against the alerting vocabulary, checks their semantics too.
    """
    body = _read_json(req)
    result, _ = webapi.validate_rules(get_backend(), body)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@method_allowed('POST')
@_json_error
def api_render(req:'any_') -> 'JsonResponse':
    """ The readable text form of canonical rule documents - the editor's document view.
    """
    body = _read_json(req)
    result, _ = webapi.render_rules(body)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@method_allowed('POST')
@_json_error
def api_save(req:'any_') -> 'JsonResponse':
    """ Saves one document as a new draft version of the alerts ruleset - the live
    pointer only moves when the listing's publish control says so.
    """
    body = _read_json(req)

    # A document that fails its type's validation answers with the findings, nothing is stored.
    try:
        result, _ = webapi.save_document(get_backend(), body, req.user.username)
    except DocumentInvalidError as e:
        out = JsonResponse({'errors': e.errors}, status=BAD_REQUEST)
        return out

    out = JsonResponse(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
