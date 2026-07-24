# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.rule_engine.notify.documents import documents_of_version
from zato.common.rule_engine.sql.constants import Definition_Type_Test_Set, Event_Type_Advisory_Run, System_Actor
from zato.common.rule_engine.testing import run_test_set

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import dictlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def run_advisory_suites(backend:'RuleSQLBackend', definition_id:'int', version:'int') -> 'dictlist':
    """ Runs every test suite attached to one ruleset against one of its versions,
    each run leaving an advisory event in the ruleset's history.
    """
    out = []

    # A ruleset's advisory suites are the test-set definitions attached to it as children ..
    suites = backend.definitions.list(parent_id=definition_id, object_type=Definition_Type_Test_Set)
    if not suites:
        return out

    # .. the version under test has to carry runnable rule documents ..
    documents = documents_of_version(backend, definition_id, version)
    if documents is None:
        return out

    # .. run each suite and preserve its outcome as an ordinary feed event.
    for suite in suites:
        test_set = backend.definitions.get_document(suite.id)
        result = run_test_set(test_set, documents)

        payload = {
            'test_set_id':   suite.id,
            'test_set_name': suite.name,
            'total':         result['total'],
            'passed':        result['passed'],
            'failed':        result['failed'],
            'explored':      result['explored'],
        }
        _ = backend.events.append(
            definition_id=definition_id,
            version=version,
            event_type=Event_Type_Advisory_Run,
            actor=System_Actor,
            payload=payload,
        )

        logger.info('Advisory suite `%s` ran against definition %s version %s -> %s failed of %s',
            suite.name, definition_id, version, result['failed'], result['total'])

        out.append(payload)

    return out

# ################################################################################################################################
# ################################################################################################################################
