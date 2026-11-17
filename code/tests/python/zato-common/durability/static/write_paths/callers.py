# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The verification of the callers of each registered function against the write path of its category. A reference is
# confined when it enters the mechanism of the category, and a function that is not an entry is confined when every
# reference to it is, which is followed through any number of functions in between.

# Zato
from references import get_references
from registry import Category, get_registry

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from references import Reference, reference_list
    from zato.common.typing_ import strlist

    Reference = Reference

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The last part of the name of the group commit, whose constructor receives the batch callback
    Commit_Queue_Name = 'CommitQueue'

    # The calls that run a function as a serialized write, by their full dotted names
    Serialized_Write_Calls = (
        'zato.common.db_env.engine.call_database',
        'zato.common.db_env.engine.execute_write',
        'self._session_factory.write',
    )

    # The runner modules of maintenance, by the end of their paths
    Runner_Paths = (
        '/zato/common/pubsub/sql/cleanup.py',
        '/zato/common/audit_log/retention_runner.py',
        '/zato/common/audit_log/search_index_merge.py',
        '/zato/common/db_env/sqlite_checkpoint.py',
        '/zato/cli/analytics.py',
    )

    # The categories whose functions are reached only through their mechanisms
    Confined_Categories = (Category.Group_Commit_Batch, Category.Serialized_Write, Category.Maintenance)

# ################################################################################################################################
# ################################################################################################################################

def _is_entry(reference:'Reference', category:'str') -> 'bool':
    """ Returns whether a reference enters the mechanism of a category.
    """
    if category == Category.Group_Commit_Batch:
        out = reference.argument_of.endswith(ModuleCtx.Commit_Queue_Name)

    elif category == Category.Serialized_Write:
        out = reference.argument_of in ModuleCtx.Serialized_Write_Calls

    else:
        out = reference.source.path.endswith(ModuleCtx.Runner_Paths)

    return out

# ################################################################################################################################

def _describe(reference:'Reference') -> 'str':
    out = f'{reference.source.path}:{reference.line} in {reference.qualname}'
    return out

# ################################################################################################################################

def walk_callers(module_name:'str', qualname:'str', category:'str') -> 'tuple[reference_list, strlist]':
    """ Follows the references to a function back to the mechanism of its category. Returns the references
    that enter the mechanism and a description of each path that reaches the function from outside of it.
    """
    registry = get_registry()

    entries:'reference_list' = []
    violations:'strlist' = []

    pending = [(module_name, qualname)]
    visited = {(module_name, qualname)}

    while pending:
        current = pending.pop()
        references = get_references(*current)

        # A function that nothing refers to is started from outside of any mechanism
        if not references:
            violations.append(f'{current[0]}.{current[1]} is not referenced')

        for reference in references:

            # The mechanism itself runs the function ..
            if _is_entry(reference, category):
                entries.append(reference)
                continue

            enclosing = (reference.module_name, reference.qualname)

            # .. a function refers to itself ..
            if enclosing == current:
                continue

            # .. a reference outside any function is never confined ..
            if not reference.qualname:
                violations.append(_describe(reference))
                continue

            # .. a registered function of another category is a write path of its own ..
            if enclosing in registry:
                if registry[enclosing] != category:
                    violations.append(_describe(reference))
                    continue

            # .. and any other function is confined only if its own callers are.
            if enclosing not in visited:
                visited.add(enclosing)
                pending.append(enclosing)

    return entries, violations

# ################################################################################################################################
# ################################################################################################################################
