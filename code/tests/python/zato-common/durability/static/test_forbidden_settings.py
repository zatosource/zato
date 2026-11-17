# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.durability.forbidden import get_forbidden_patterns
from zato.common.test.durability.rust_source import get_line
from zato.common.test.durability.sources import get_setting_files

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

def test_no_source_relaxes_durability() -> 'None':
    """ No source of the installation or of a linked repository, production code and tests alike, sets a database
    to a value that lets a commit return before it is on disk.
    """
    patterns = get_forbidden_patterns()
    findings:'strlist' = []

    for source in get_setting_files():
        text = source.read()

        for pattern in patterns:
            for match in pattern.finditer(text):
                line = get_line(text, match.start())
                findings.append(f'{source.path}:{line} -> {match.group(0)}')

    assert not findings, '\n'.join(findings)

# ################################################################################################################################
# ################################################################################################################################
