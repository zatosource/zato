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
from typing import Callable

# Django
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.rule_store import get_backend
from zato.admin.web.views import method_allowed
from zato.common.alerting import config_map
from zato.common.alerting.config_store import apply_type_config, NoSuchRulesetError
from zato.common.alerting.notification_config import notification_keys
from zato.common.api import Alerting
from zato.common.defaults import default_cluster_id
from zato.common.rule_engine import webapi
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.rule_engine.webapi import BadRequestError, DocumentInvalidError
from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict, dictlist, stranydict
    anydict = anydict
    dictlist = dictlist
    RuleDefinitionRecord = RuleDefinitionRecord
    RuleSQLBackend = RuleSQLBackend
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults for the editor's GET parameters when the caller does not send them
_default_rule_key    = ''
_default_rule_name   = ''
_default_rule_docs   = ''
_default_rule_active = '1'

# ################################################################################################################################
# ################################################################################################################################

def _rule_entry_sort_key(entry:'anydict') -> 'str':
    """ Orders the editor's rule select by label, case-insensitively.
    """
    out = entry['label'].lower()
    return out

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
# ################################################################################################################################

# What the config screen calls each type
_type_titles = {
    'rest':          'REST and SOAP',
    'sql':           'SQL',
    'llm':           'LLM',
    'mcp':           'MCP',
    'microsoft':     'Microsoft cloud',
    'email':         'Email',
    'odoo':          'Odoo',
    'file_transfer': 'File transfer',
    'scheduler':     'Scheduler',
    'channels':      'Channels',
    'common':        'Common',
}

# What each screen cell says - the label next to the value and the unit suffix after it
_field_display = {
    'consecutive_failures': ('Consecutive failures', ''),
    'error_rate':           ('Error rate', '%'),
    'alert_threshold':      ('Alert threshold', '%'),
    'max_latency':          ('Max latency', ' ms'),
    'max_query_time':       ('Max query time', ' ms'),
    'warning_latency':      ('Warning latency', ' ms'),
    'critical_latency':     ('Critical latency', ' ms'),
    'max_tool_call_time':   ('Max tool-call time', ' ms'),
    'health_alerts':        ('Health alerts', ''),
    'max_call_time':        ('Max call time', ' ms'),
    'auth_failures':        ('Auth failures', ''),
    'warning_failures':     ('Warning failures', ''),
    'critical_failures':    ('Critical failures', ''),
    'arrival_overdue':      ('Arrival overdue', ''),
    'test_transfers':       ('Test transfers', ''),
    'overdue_multiplier':   ('Overdue multiplier', ''),
    'start_delay':          ('Start delay', ' ms'),
    'certificate_warning':  ('Certificate warning', ' days'),
    'outstanding_backlog':  ('Outstanding backlog', ''),
    'feed_silence':         ('Feed silence', ' s'),
    'use_llm':              ('LLM', ''),
}

# The five cell slots of each type's row - the columns line up across the rows,
# so a type without a value in some column carries a placeholder there.
_type_cells = {
    'rest':          ['consecutive_failures', 'error_rate', 'alert_threshold', 'max_latency', 'use_llm'],
    'sql':           ['consecutive_failures', 'error_rate', 'alert_threshold', 'max_query_time', 'use_llm'],
    'llm':           ['consecutive_failures', 'error_rate', 'warning_latency', 'critical_latency', 'use_llm'],
    'mcp':           ['consecutive_failures', 'error_rate', 'alert_threshold', 'max_tool_call_time', 'use_llm'],
    'microsoft':     ['consecutive_failures', 'error_rate', 'health_alerts', 'max_call_time', 'use_llm'],
    'email':         ['consecutive_failures', 'error_rate', 'auth_failures', 'alert_threshold', 'use_llm'],
    'odoo':          ['consecutive_failures', 'error_rate', 'auth_failures', 'max_call_time', 'use_llm'],
    'file_transfer': ['consecutive_failures', 'warning_failures', 'critical_failures', 'test_transfers', 'use_llm',
        'arrival_overdue'],
    'scheduler':     ['error_rate', 'alert_threshold', 'overdue_multiplier', 'start_delay', 'use_llm'],
    'channels':      [None, 'error_rate', None, None, None],
    'common':        ['certificate_warning', 'outstanding_backlog', 'feed_silence', None, None],
}

# What a toggle cell's value reads as
_toggle_on_label  = 'On'
_toggle_off_label = 'Off'

# What each cell of the notifications row calls its value
_notification_display = {
    Alerting.Extra_Slack_Webhook:    'Slack webhook',
    Alerting.Extra_Teams_Webhook:    'Teams webhook',
    Alerting.Extra_Webhook_URL:      'Webhook URL',
    Alerting.Extra_Email_Connection: 'Email connection',
    Alerting.Extra_Default_To:       'Email to',
    Alerting.Extra_From:             'Email from',
    Alerting.Extra_Dashboard_URL:    'Dashboard URL',
}

# What a notification cell without a value reads as
_not_set_label = 'Not set'

# ################################################################################################################################

def _build_config_cell(field_name:'str', kind:'str', values:'stranydict') -> 'stranydict | None':
    """ One cell of one type's row - the label, the value in screen units and what
    the cell displays. A field whose rule is gone renders as a placeholder.
    """
    if field_name not in values:
        return None

    label, suffix = _field_display[field_name]
    value = values[field_name]

    # Our response to produce
    out = {
        'name': field_name,
        'label': label,
        'suffix': suffix,
    }

    if kind == config_map.Kind_Toggle:
        out['kind'] = 'checkbox'
        out['value'] = 'true' if value else 'false'
        out['display'] = _toggle_on_label if value else _toggle_off_label
    else:
        out['kind'] = 'number'
        out['value'] = value
        out['display'] = f'{value}{suffix}'

    return out

# ################################################################################################################################

@method_allowed('GET')
def config(req:'any_') -> 'TemplateResponse':
    """ The alert rules config screen - one card per rule type, each with the
    parameters its rules are driven by, read from the live rule documents
    the same way the sweep reads them.
    """
    backend = get_backend()

    types = []

    for type_name, ruleset_name in config_map.type_to_ruleset.items():

        definition = _find_definition(backend, ruleset_name, Definition_Type_Ruleset)

        # A store without the ruleset shows the row inactive with no values
        if definition:
            document = deserialize_document(definition.document)
            documents = document[Documents_Key]
        else:
            documents = {}

        values = config_map.read_type_values(type_name, documents)

        # Which kind each of the type's fields comes in
        kinds = {}

        for field in config_map.type_fields[type_name]:
            kinds[field['name']] = field['kind']

        cells = []

        for field_name in _type_cells[type_name]:

            if field_name is None:
                cells.append(None)
                continue

            cell = _build_config_cell(field_name, kinds[field_name], values)
            cells.append(cell)

        types.append({
            'name': type_name,
            'title': _type_titles[type_name],
            'is_active': config_map.is_type_active(documents),
            'cells': cells,
        })

    # The notifications row below the types - its values live in the sweep job's
    # extra and come through the same service enmasse reads them with.
    response = req.zato.client.invoke(Alerting.Get_Notification_Config_Service, {})
    notification_values = json.loads(response.data['response_data'])

    notification_cells = []

    for key in notification_keys:

        value = notification_values[key]

        notification_cells.append({
            'name': key,
            'label': _notification_display[key],
            'value': value,
            'display': value if value else _not_set_label,
        })

    return TemplateResponse(req, 'zato/alerting/config.html', {
        'cluster_id': default_cluster_id,
        'types': types,
        'notification_cells': notification_cells,
        'zato_clusters': True,
        'zato_template_name': 'zato/alerting/config.html',
    })

# ################################################################################################################################

@method_allowed('POST')
def config_save(req:'any_') -> 'JsonResponse':
    """ Saves one type's config from the screen - the popover's values, the badge's
    active state or both - into the live rule documents and publishes the new version,
    the same path the listing's actions walk. A save that changes nothing stores nothing.
    """
    backend = get_backend()
    body = json.loads(req.body)

    type_name = body['type']
    actor = req.user.username

    try:
        changed = apply_type_config(
            backend,
            type_name,
            actor=actor,
            values=body.get('values'),
            is_active=body.get('is_active'),
        )

    except NoSuchRulesetError as e:
        out = JsonResponse({'error': str(e)}, status=BAD_REQUEST)
        return out

    except DocumentInvalidError as e:
        out = JsonResponse({'error': json.dumps(e.errors)}, status=BAD_REQUEST)
        return out

    except Exception as e:
        logger.warning('Alert rules config save for `%s` failed -> %s', type_name, e)
        out = JsonResponse({'error': str(e)}, status=INTERNAL_SERVER_ERROR)
        return out

    # The test transfers checkbox also drives the canary scheduler job - the rule
    # decides whether canary findings match, the job decides whether the canary
    # transfers run at all, and the two always move together.
    values = body.get('values')

    if values and 'test_transfers' in values:
        _ = req.zato.client.invoke(Alerting.Set_Canary_State_Service, {'is_active': values['test_transfers']})

    out = JsonResponse({'is_ok': True, 'changed': changed})
    return out

# ################################################################################################################################

@method_allowed('POST')
def config_notifications_save(req:'any_') -> 'JsonResponse':
    """ Saves the notifications row - the popover's values go into the alerting
    sweep job's extra through the internal service and the very next sweep
    already delivers with them.
    """
    body = json.loads(req.body)

    try:
        _ = req.zato.client.invoke(Alerting.Set_Notification_Config_Service, body['values'])

    except Exception as e:
        logger.warning('Alert notifications save failed -> %s', e)
        out = JsonResponse({'error': str(e)}, status=INTERNAL_SERVER_ERROR)
        return out

    out = JsonResponse({'is_ok': True})
    return out

# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The alert rules listing - the shared ruleset browser, opened straight
    onto the rules of the alerts ruleset.
    """
    backend = get_backend()
    definition = _find_definition(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

    definition_id = definition.id if definition else 0

    return TemplateResponse(req, 'zato/alerting/index.html', {
        'cluster_id': default_cluster_id,
        'definition_id': definition_id,
        'ruleset_name': Alerting.Ruleset_Name,
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

    if not (rule_key := req.GET.get('rule')):
        rule_key = _default_rule_key

    # The header names the rule being edited, read from the stored document,
    # and the select next to it offers every rule of the ruleset.
    rule_name = ''
    rules = []

    if definition:
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        if rule_key in documents:
            rule_name = documents[rule_key]['name']

        for key, item in documents.items():
            rules.append({'value': key, 'label': item['name']})

        rules.sort(key=_rule_entry_sort_key)

    if not (new_rule_name := req.GET.get('new')):
        new_rule_name = _default_rule_name

    if not (new_rule_docs := req.GET.get('docs')):
        new_rule_docs = _default_rule_docs

    if not (new_rule_active := req.GET.get('active')):
        new_rule_active = _default_rule_active

    return TemplateResponse(req, 'zato/alerting/editor.html', {
        'cluster_id': default_cluster_id,
        'definition_id': definition_id,
        'rule_key': rule_key,
        'rule_name': rule_name,
        'rules_json': json.dumps(rules),
        'new_rule_name': new_rule_name,
        'new_rule_docs': new_rule_docs,
        'new_rule_active': new_rule_active == '1',
        'zato_clusters': True,
        'zato_template_name': 'zato/alerting/editor.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def action(req:'any_') -> 'HttpResponse':
    """ Runs one listing action - activate, deactivate or delete - against
    the alerts ruleset, with the Dashboard user as the actor. Every change
    goes live right away, like every other object the Dashboard edits.
    """
    backend = get_backend()
    definition = _find_definition(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

    if not definition:
        out = JsonResponse({'error': 'There is no alerts ruleset to act on'}, status=BAD_REQUEST)
        return out

    action_name = req.POST['action']
    actor = req.user.username

    try:

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

        elif action_name == 'update':

            new_name = req.POST['name'].strip()
            documents[rule_key]['docs'] = req.POST['docs'].strip()
            documents[rule_key]['is_active'] = req.POST['active'] == '1'
            comment = f'Updated rule {rule_name}'

            # A changed name moves the document under a new key, since a key
            # is the ruleset's name joined with the rule's own.
            if new_name != rule_name:

                new_key = f'{Alerting.Ruleset_Name}_{new_name}'

                if new_key in documents:
                    out = JsonResponse({'error': f'A rule of that name already exists -> {new_name}'}, status=BAD_REQUEST)
                    return out

                item = documents.pop(rule_key)
                item['name'] = new_name
                item['full_name'] = new_key
                documents[new_key] = item

                comment = f'Renamed rule {rule_name} to {new_name}'

        else:
            out = JsonResponse({'error': f'No such action -> {action_name}'}, status=BAD_REQUEST)
            return out

        body = {
            'definition_id': definition.id,
            'expected_current_version': definition.current_version,
            'document': {Documents_Key: documents},
            'comment': comment,
        }
        result, _ = webapi.save_document(backend, body, actor)

        # The change goes live in the same call, so the sweep already runs with it.
        _ = backend.versions.publish(definition_id=definition.id, version=result['version'], actor=actor)

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

def _json_error(func:'Callable[..., JsonResponse]') -> 'Callable[..., JsonResponse]':
    """ Turns the shared webapi's exceptions into the JSON error answers the editor's
    data layer reads - the same contract the rule engine dashboard's own views keep.
    """
    def wrapper(req:'any_', *args:'any_', **kwargs:'any_') -> 'JsonResponse':
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
def api_search(req:'any_') -> 'JsonResponse':
    """ Full-text search over rendered rule sentences - what the listing's
    command bar highlights its hits with.
    """
    if query := req.GET.get('q'):
        query = query.strip()

    if not query:
        raise BadRequestError('Missing required parameter -> q')

    result, _ = webapi.search_definitions(get_backend(), query)

    out = JsonResponse(result)
    return out

# ################################################################################################################################

@method_allowed('POST')
@_json_error
def api_name_exists(req:'any_') -> 'JsonResponse':
    """ Whether a rule of that name already exists in the alerts ruleset - what the create
    popup's uniqueness checks ask before the editor is ever opened.
    """
    backend = get_backend()
    definition = _find_definition(backend, Alerting.Ruleset_Name, Definition_Type_Ruleset)

    name = req.POST['value'].strip()
    exists = False

    # A store without the ruleset holds no rules yet, so no name can be taken.
    if definition:
        document = deserialize_document(definition.document)
        documents = document[Documents_Key]

        for item in documents.values():
            if item['name'] == name:
                exists = True
                break

    out = JsonResponse({'exists': exists})
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
    """ Saves one document as a new version of the alerts ruleset and publishes it
    in the same call - a rule the editor saved is a rule the sweep runs with.
    """
    backend = get_backend()
    body = _read_json(req)
    actor = req.user.username

    # A document that fails its type's validation answers with the findings, nothing is stored.
    try:
        result, _ = webapi.save_document(backend, body, actor)
    except DocumentInvalidError as e:
        out = JsonResponse({'errors': e.errors}, status=BAD_REQUEST)
        return out

    # The change goes live right away, like every other object the Dashboard edits.
    _ = backend.versions.publish(definition_id=result['definition_id'], version=result['version'], actor=actor)

    out = JsonResponse(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
