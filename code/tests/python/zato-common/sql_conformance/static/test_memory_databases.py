# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.sql_conformance.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx
from zato.common.test.sql_conformance.memory import get_memory_patterns, ModuleCtx as MemoryModuleCtx
from zato.common.test.sql_conformance.rust_source import get_line
from zato.common.test.sql_conformance.sources import get_setting_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

def test_no_database_in_memory() -> 'None':
    """ No source, production code and tests alike, places a database in memory or on a file system held in memory,
    however long a test takes. A linked repository may exempt a database of a third-party counterpart by declaring
    the file and the pattern in its registry, and the installation exempts none.
    """
    exemptions:'set[tuple[str, str]]' = set()

    for relative_path, pattern_name, _ in get_linked_entries(LinkedModuleCtx.Memory_Database_Exemptions):
        exemptions.add((relative_path, pattern_name))

    patterns = get_memory_patterns()
    findings:'strlist' = []

    for source in get_setting_files():

        # The patterns themselves are defined in one module
        if source.path == MemoryModuleCtx.Definition_Path:
            continue

        text = source.read()

        for item in patterns:
            for match in item.pattern.finditer(text):

                if source.is_linked:
                    if (source.relative_path, item.name) in exemptions:
                        continue

                line = get_line(text, match.start())
                findings.append(f'{source.path}:{line} -> {item.name} {match.group(0)}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
