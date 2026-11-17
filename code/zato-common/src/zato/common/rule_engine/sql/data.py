# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Any, NamedTuple

# typing-extensions
from typing_extensions import TypeAlias

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime

    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

any_:TypeAlias = Any
anydict:TypeAlias = dict[str, any_]
dictlist:TypeAlias = list[anydict]
strlist:TypeAlias = list[str]
definition_record_list:TypeAlias = list['RuleDefinitionRecord']

# ################################################################################################################################
# ################################################################################################################################

class RuleDefinitionRecord(NamedTuple):
    """ One current rule-engine object.
    """

    id:              'int'
    parent_id:       'int | None'
    parent_key:      'int'
    name:            'str'
    object_type:     'str'
    current_version: 'int'
    live_version:    'int | None'
    is_active:       'bool'
    created_at:      'datetime'
    updated_at:      'datetime'
    document:        'str'

# ################################################################################################################################

class RuleVersionRecord(NamedTuple):
    """ One immutable full-document snapshot, the live pointer lives on the definition row.
    """

    id:            'int'
    definition_id: 'int'
    version:       'int'
    author:        'str'
    comment:       'str'
    created_at:    'datetime'
    document:      'str'

# ################################################################################################################################
# ################################################################################################################################
