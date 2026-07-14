# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import Match, Scrubber

# Zato
from zato.common.typing_ import any_, anytuple, strlistnone
from zato.common.util.safeguards.common import Max_Cleaner_Cache_Entries, SafeguardConfig, SafeguardResult
from zato.common.util.safeguards.walk import walk_strings

# ################################################################################################################################
# ################################################################################################################################

# Type aliases - a cleaner is the underlying library's detector engine, Scrubber is simply what that class is called there.
match_list   = list[Match]
cleaner_dict = dict[anytuple, Scrubber]

# ################################################################################################################################
# ################################################################################################################################

# Compiled cleaners keyed by their configuration - dicts preserve insertion order,
# which the eviction below relies on to drop the oldest entry first.
_cache:'cleaner_dict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_cleaner(config:'SafeguardConfig') -> 'Scrubber':
    """ Returns a PII cleaner built from the config, reusing a previously built one when possible.
    Building a cleaner compiles detector patterns, so each configuration is compiled once and kept for later calls.
    """
    detectors = tuple(config.pii_detectors)
    lands     = tuple(config.pii_lands)
    exclude   = tuple(config.pii_exclude)

    key = (detectors, lands, exclude, config.pii_validate, config.pii_stable_tokens)

    # A cache hit skips compilation entirely.
    if out := _cache.get(key):
        return out

    # Explicit detector names win over land selection ..
    if detectors:
        cleaner_detectors:'strlistnone' = list(detectors)
        cleaner_lands:'strlistnone' = None

    # .. lands narrow the default detector set to the given ones ..
    elif lands:
        cleaner_detectors = None
        cleaner_lands = list(lands)

    # .. and with neither given, every default detector is active.
    else:
        cleaner_detectors = None
        cleaner_lands = None

    if exclude:
        cleaner_exclude:'strlistnone' = list(exclude)
    else:
        cleaner_exclude = None

    # The land selection maps to what the underlying library calls regions - this is the only place that name appears.
    out = Scrubber(
        detectors=cleaner_detectors,
        exclude=cleaner_exclude,
        regions=cleaner_lands,
        validate=config.pii_validate,
        stable_tokens=config.pii_stable_tokens,
    )

    # The oldest entry makes room when the cache is full.
    cache_size = len(_cache)
    is_full = cache_size >= Max_Cleaner_Cache_Entries

    if is_full:
        oldest = next(iter(_cache))
        del _cache[oldest]

    _cache[key] = out

    return out

# ################################################################################################################################
# ################################################################################################################################

def remove_pii(value:'any_', result:'SafeguardResult', config:'SafeguardConfig') -> 'any_':
    """ Replaces PII matches in string values with their detector tokens, counting the matches per detector.
    """
    cleaner = get_cleaner(config)

    def visit(text:'str', path:'str') -> 'str':

        # A scan is cheaper than a clean, so strings with nothing replaceable pay only the scan ..
        matches = cleaner.scan(text)

        # .. with validation on, only checksum-confirmed matches are replaced and shape-only ones survive ..
        if config.pii_validate:
            replaceable:'match_list' = []

            for match in matches:
                if match.valid:
                    replaceable.append(match)

        # .. and with validation off, every shape match is replaced.
        else:
            replaceable = matches

        if not replaceable:
            return text

        # .. every match about to be replaced is counted per detector ..
        counts = result.pii_removed

        for match in replaceable:
            if count := counts.get(match.name):
                counts[match.name] = count + 1
            else:
                counts[match.name] = 1

        # .. and the clean itself replaces them with tokens.
        out = cleaner.clean(text)

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################
