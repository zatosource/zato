# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import Scrubber

# Zato
from zato.common.typing_ import any_
from zato.common.util.safeguards import detectors
from zato.common.util.safeguards.common import SafeguardResult
from zato.common.util.safeguards.detectors.secrets import Region_Secrets
from zato.common.util.safeguards.walk import walk_strings

# The import above registers Zato's own detectors with the library's registry - this line keeps flake8 quiet about it.
detectors = detectors

# ################################################################################################################################
# ################################################################################################################################

# The one cleaner every gateway shares - it compiles once, on first use.
_cleaner:'Scrubber | None' = None

# ################################################################################################################################
# ################################################################################################################################

def get_secrets_cleaner() -> 'Scrubber':
    """ Returns the secrets cleaner, compiling it on first use. Replacements are always stable -
    the same secret renders as the same numbered token throughout one string.
    """
    global _cleaner

    if _cleaner is None:
        _cleaner = Scrubber(regions=[Region_Secrets], stable_tokens=True)

    return _cleaner

# ################################################################################################################################
# ################################################################################################################################

def remove_secrets(value:'any_', result:'SafeguardResult') -> 'any_':
    """ Replaces credential-shaped values in string values with their detector tokens,
    counting the matches per detector. The detector set is fixed, the stage toggle
    is the only per-gateway choice.
    """
    cleaner = get_secrets_cleaner()

    def visit(text:'str', path:'str') -> 'str':

        # A scan comes first and a string with no matches comes back as it was ..
        matches = cleaner.scan(text)

        if not matches:
            return text

        # .. every match about to be replaced is counted per detector ..
        counts = result.secrets_removed

        for match in matches:
            if count := counts.get(match.name):
                counts[match.name] = count + 1
            else:
                counts[match.name] = 1

        # .. and the clean itself replaces them with stable tokens.
        out = cleaner.clean(text)

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################
