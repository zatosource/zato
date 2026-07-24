# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document
from zato.common.rule_engine.sql.errors import RecordNotFoundError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def documents_of_version(backend:'RuleSQLBackend', definition_id:'int', version:'int') -> 'anydict | None':
    """ Returns the rule documents of one stored version or None when the snapshot has none.
    """
    try:
        record = backend.versions.get(definition_id, version)
    except RecordNotFoundError:
        return None

    payload = deserialize_document(record.document)

    # Only runnable ruleset snapshots keep rule documents.
    if Documents_Key not in payload:
        out = None
    else:
        out = payload[Documents_Key]

    return out

# ################################################################################################################################
# ################################################################################################################################
