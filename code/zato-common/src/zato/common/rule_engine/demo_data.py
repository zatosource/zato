# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.rule_engine.document_checks import validate_definition_document
from zato.common.rule_engine.loading import publish_and_reload
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql.constants import Definition_Type_Decision_Table, Definition_Type_Ruleset, \
    Definition_Type_Test_Set, Definition_Type_Vocabulary, Documents_Key, System_Actor
from zato.common.rule_engine.vocabulary import TermType
from zato.common.util.logging_ import count_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.api import RulesManager
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict, intlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What every demo definition is called, in the shape each kind of name takes - the ruleset name is
# also the REST path callers invoke, so it is the only one made of words, digits and underscores.
Demo_Ruleset_Name    = 'incident_escalation'
Demo_Vocabulary_Name = 'Incidents'
Demo_Table_Name      = 'Incident_routing'
Demo_Test_Set_Name   = 'Incident escalation scenarios'

# The comment the first version of every demo definition carries.
Demo_Comment = 'The definitions a new environment starts with'

# The severity a demo statement carries when it merely reports what happened.
_severity_info = 'info'

# The severity of a statement about an incident that someone has to look at now.
_severity_warning = 'warning'

# The severity of a statement about an incident that breaks what was promised.
_severity_violation = 'violation'

# A term that is neither deprecated nor otherwise marked carries no status.
_no_status = ''

# ################################################################################################################################
# ################################################################################################################################

# One incident, five facts about it and five rules over them - every industry has incidents,
# severities, owners and a clock, so the demo reads the same to everyone who opens it.
demo_zrules_contents = """
# ################################################################################################################################

rule
    Critical_Unacknowledged
docs
    A severity 1 incident nobody has acknowledged pages the on-call engineer and tells the manager.
when
    incident.severity is 1 and
    incident.acknowledged is false
then
    outcome.queue = 'on_call'
    outcome.notify = 'manager'
    outcome.page_on_call = true

# ################################################################################################################################

rule
    After_Hours_Routing
docs
    Outside business hours a serious incident goes to the on-call engineer, everything else to the normal queue.
when
    incident.business_hours is false and
    incident.severity is at most 2
then
    outcome.queue = 'on_call'
    outcome.notify = 'on_call_engineer'
else
    outcome.queue = 'normal'
    outcome.notify = 'service_desk'

# ################################################################################################################################

rule
    Impact_Escalation
docs
    An incident customers can feel, open for more than an hour, is escalated whatever the time of day.
when
    incident.severity is at most 2 and
    incident.customer_impact is true and
    incident.hours_open is more than 1
then
    outcome.queue = 'escalation'
    outcome.notify = 'incident_manager'
    outcome.escalate = true

# ################################################################################################################################

rule
    Stale_Low_Priority
docs
    A low-priority incident still open after a day is downgraded and its reporter is asked to confirm it.
defaults
    stale_hours = 24
when
    incident.severity is at least 3 and
    incident.hours_open is more than default.stale_hours
then
    outcome.downgrade = true
    outcome.notify = 'reporter'

# ################################################################################################################################

rule
    Auto_Close_No_Response
docs
    The lowest severity, never acknowledged and three days old - the incident closes itself.
when
    incident.severity is 4 and
    incident.acknowledged is false and
    incident.hours_open is more than 72
then
    outcome.queue = 'closed'
    outcome.close_reason = 'no response from the reporter'

# ################################################################################################################################
""".strip()

# ################################################################################################################################
# ################################################################################################################################

def _term(name:'str', type_:'str', phrase:'str') -> 'anydict':
    """ One vocabulary attribute - the name rules use, the type that decides which comparators fit
    and the phrase every screen speaks it with.
    """
    out = {'name': name, 'type': type_, 'phrase': phrase, 'status': _no_status}
    return out

# ################################################################################################################################

def demo_vocabulary() -> 'anydict':
    """ The terms the demo rules are written in - what is known about an incident and what is decided about it.
    """
    incident_terms = [
        _term('severity',        TermType.Number, 'the severity of the incident'),
        _term('hours_open',      TermType.Number, 'the hours the incident has been open'),
        _term('acknowledged',    TermType.Yes_No, 'the incident is acknowledged'),
        _term('customer_impact', TermType.Yes_No, 'customers can feel the incident'),
        _term('business_hours',  TermType.Yes_No, 'the incident arrived during business hours'),
    ]

    outcome_terms = [
        _term('queue',        TermType.Text,   'the queue the incident goes to'),
        _term('notify',       TermType.Text,   'who is told about the incident'),
        _term('close_reason', TermType.Text,   'why the incident was closed'),
        _term('page_on_call', TermType.Yes_No, 'the on-call engineer is paged'),
        _term('escalate',     TermType.Yes_No, 'the incident is escalated'),
        _term('downgrade',    TermType.Yes_No, 'the incident is downgraded'),
    ]

    entities = [
        {'name': 'incident', 'attributes': incident_terms},
        {'name': 'outcome', 'attributes': outcome_terms},
    ]

    out = {'name': Demo_Vocabulary_Name, 'entities': entities}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _column(
    number:'int',
    cells:'anydict',
    actions:'anydict',
    text:'str',
    severity:'str',
    overrides:'intlist',
    ) -> 'anydict':
    """ One column of the demo table - what it matches, what it assigns and what it says when it fires.
    """
    statement = {'text': text, 'severity': severity}

    out = {
        'number': number,
        'cells': cells,
        'actions': actions,
        'statement': statement,
        'overrides': overrides,
    }
    return out

# ################################################################################################################################

def demo_table() -> 'anydict':
    """ The same routing decision as a grid - one column per case, read top to bottom by anyone.
    """
    conditions = [
        {'letter': 'a', 'subject': 'incident.severity'},
        {'letter': 'b', 'subject': 'incident.customer_impact'},
        {'letter': 'c', 'subject': 'incident.business_hours'},
        {'letter': 'd', 'subject': 'incident.hours_open'},
    ]

    actions = [
        {'target': 'outcome.queue'},
        {'target': 'outcome.notify'},
    ]

    columns = [

        # Column 0 always fires first, so it is where an incident goes when no other column claims it ..
        _column(
            0,
            {'a': '-', 'b': '-', 'c': '-', 'd': '-'},
            {'outcome.queue': 'normal', 'outcome.notify': 'service_desk'},
            'The incident waits in the normal queue.',
            _severity_info,
            [],
        ),

        # .. a severity 1 incident is the one case nobody waits on, so it outranks every column below it ..
        _column(
            1,
            {'a': '1', 'b': '-', 'c': '-', 'd': '-'},
            {'outcome.queue': 'on_call', 'outcome.notify': 'manager'},
            'A severity 1 incident goes straight to the on-call engineer.',
            _severity_violation,
            [2, 3],
        ),

        # .. an incident customers can feel outranks the after-hours column below it ..
        _column(
            2,
            {'a': '<= 2', 'b': 'true', 'c': '-', 'd': '> 1'},
            {'outcome.queue': 'escalation', 'outcome.notify': 'incident_manager'},
            'Customers can feel this one and it has been open for more than an hour.',
            _severity_warning,
            [3],
        ),

        # .. outside business hours a serious incident has nobody at the service desk to take it ..
        _column(
            3,
            {'a': '<= 2', 'b': '-', 'c': 'false', 'd': '-'},
            {'outcome.queue': 'on_call', 'outcome.notify': 'on_call_engineer'},
            'A serious incident outside business hours goes to the on-call engineer.',
            _severity_warning,
            [],
        ),

        # .. and a low-priority incident nobody has closed in a day goes back to whoever reported it.
        _column(
            4,
            {'a': '>= 3', 'b': '-', 'c': '-', 'd': '> 24'},
            {'outcome.queue': 'backlog', 'outcome.notify': 'reporter'},
            'A low-priority incident has been open for more than a day.',
            _severity_info,
            [],
        ),
    ]

    out = {
        'name': Demo_Table_Name,
        'docs': 'Where one incident goes, by severity, customer impact, time of day and age.',
        'filter': {'subject': 'incident.severity', 'cell': '1..4'},
        'conditions': conditions,
        'actions': actions,
        'columns': columns,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def _scenario(name:'str', incident:'anydict', expected:'anydict') -> 'anydict':
    """ One scenario of the demo suite - an incident as it arrives and what the rules have to decide about it.
    """
    out = {'name': name, 'input': {'incident': incident}, 'expected': expected}
    return out

# ################################################################################################################################

def demo_test_set() -> 'anydict':
    """ Four incidents that show every path the demo rules take, including the one where nothing fires.
    """
    scenarios = [

        _scenario(
            'Severity 1 that nobody acknowledged',
            {'severity': 1, 'hours_open': 0, 'acknowledged': False, 'customer_impact': True, 'business_hours': True},
            {'outcome.queue': 'on_call', 'outcome.notify': 'manager', 'outcome.page_on_call': True},
        ),

        _scenario(
            'Customers can feel it, and it is the middle of the night',
            {'severity': 2, 'hours_open': 3, 'acknowledged': True, 'customer_impact': True, 'business_hours': False},
            {'outcome.queue': 'escalation', 'outcome.notify': 'incident_manager', 'outcome.escalate': True},
        ),

        _scenario(
            'Low priority, open since yesterday',
            {'severity': 3, 'hours_open': 30, 'acknowledged': True, 'customer_impact': False, 'business_hours': True},
            {'outcome.notify': 'reporter', 'outcome.downgrade': True},
        ),

        # A scenario with nothing expected explores rather than asserts, which is what an
        # incident no rule has anything to say about looks like.
        _scenario(
            'An ordinary incident no rule touches',
            {'severity': 3, 'hours_open': 2, 'acknowledged': True, 'customer_impact': False, 'business_hours': True},
            {},
        ),
    ]

    out = {'name': Demo_Test_Set_Name, 'scenarios': scenarios}
    return out

# ################################################################################################################################
# ################################################################################################################################

def demo_ruleset() -> 'anydict':
    """ The demo rules as the canonical documents the store keeps, parsed from the very text a new server gets on disk.
    """
    documents, errors = parse_data_details(demo_zrules_contents, Demo_Ruleset_Name)

    if errors:
        raise Exception(f'The demo rules do not parse -> {errors}')

    out = {Documents_Key: documents}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _exists(backend:'RuleSQLBackend', name:'str', object_type:'str') -> 'bool':
    """ Whether the store already holds one demo definition, under the name and the kind it is created with.

    A definition someone archived still holds its name, so archived ones count here too - what was
    put aside on purpose stays that way instead of coming back on the next start.
    """
    candidates = backend.definitions.list(object_type=object_type, include_inactive=True, search_text=name)

    for candidate in candidates:
        if candidate.name == name:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _create_definition(
    backend:'RuleSQLBackend',
    *,
    name:'str',
    object_type:'str',
    document:'anydict',
    ) -> 'RuleDefinitionRecord':
    """ Stores one demo definition together with its first version, after the same validation the screens run.
    """
    errors = validate_definition_document(object_type, document)

    if errors:
        raise Exception(f'The demo {object_type} does not validate -> {errors}')

    out = backend.definitions.create(
        name=name,
        object_type=object_type,
        document=document,
        author=System_Actor,
        comment=Demo_Comment,
    )

    logger.info('Created the demo %s `%s` (id=%s)', object_type, name, out.id)
    return out

# ################################################################################################################################

def _publish(backend:'RuleSQLBackend', definition:'RuleDefinitionRecord') -> 'None':
    """ Makes the first version of one demo definition the live one.
    """
    _ = backend.versions.publish(definition_id=definition.id, version=definition.current_version, actor=System_Actor)

# ################################################################################################################################
# ################################################################################################################################

def _seed_vocabulary(backend:'RuleSQLBackend') -> 'bool':
    """ The vocabulary comes first, because every other demo definition speaks its terms.
    """
    if _exists(backend, Demo_Vocabulary_Name, Definition_Type_Vocabulary):
        return False

    vocabulary = _create_definition(
        backend,
        name=Demo_Vocabulary_Name,
        object_type=Definition_Type_Vocabulary,
        document=demo_vocabulary(),
    )
    _publish(backend, vocabulary)

    return True

# ################################################################################################################################

def _seed_ruleset(backend:'RuleSQLBackend', manager:'RulesManager') -> 'bool':
    """ The rules go live and start running in the same call, so the demo answers REST calls at once.
    """
    if _exists(backend, Demo_Ruleset_Name, Definition_Type_Ruleset):
        return False

    document = demo_ruleset()
    ruleset = _create_definition(
        backend,
        name=Demo_Ruleset_Name,
        object_type=Definition_Type_Ruleset,
        document=document,
    )

    documents = document[Documents_Key]
    _ = backend.references.rebuild(definition_id=ruleset.id, documents=documents)
    _ = publish_and_reload(manager, backend, definition_id=ruleset.id, version=ruleset.current_version, actor=System_Actor)

    return True

# ################################################################################################################################

def _seed_table(backend:'RuleSQLBackend') -> 'bool':
    """ The same routing decision as a grid.
    """
    if _exists(backend, Demo_Table_Name, Definition_Type_Decision_Table):
        return False

    table = _create_definition(
        backend,
        name=Demo_Table_Name,
        object_type=Definition_Type_Decision_Table,
        document=demo_table(),
    )
    _publish(backend, table)

    return True

# ################################################################################################################################

def _seed_test_set(backend:'RuleSQLBackend') -> 'bool':
    """ The scenarios that show what the rules decide for four incidents.
    """
    if _exists(backend, Demo_Test_Set_Name, Definition_Type_Test_Set):
        return False

    test_set = _create_definition(
        backend,
        name=Demo_Test_Set_Name,
        object_type=Definition_Type_Test_Set,
        document=demo_test_set(),
    )
    _publish(backend, test_set)

    return True

# ################################################################################################################################
# ################################################################################################################################

def seed_demo_definitions(backend:'RuleSQLBackend', manager:'RulesManager') -> 'None':
    """ Gives an environment the demo vocabulary, rules, table and scenarios.

    Every screen opens on the first definition of its kind, so one of each is what makes a new
    environment show working rules rather than four empty states. Each one is looked up by its
    own name and kind, so a store that already holds some of them gains only what is missing,
    and anything a person created themselves is never touched.
    """
    outcomes = [
        _seed_vocabulary(backend),
        _seed_ruleset(backend, manager),
        _seed_table(backend),
        _seed_test_set(backend),
    ]

    created_count = 0

    for is_created in outcomes:
        if is_created:
            created_count += 1

    if created_count:
        created_text = count_text(created_count, 'definition', 'definitions')
        logger.info('Demo data seeded -> %s', created_text)
    else:
        logger.info('Demo data is already in place, nothing to seed')

# ################################################################################################################################
# ################################################################################################################################
